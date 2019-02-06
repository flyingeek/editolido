# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import datetime
import calendar
import io
import time
import re

from editolido.ofp import utc

try:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from urlparse import urlsplit
except ImportError:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from urllib.parse import urlsplit

from editolido.geoindex import GeoGridIndex
from editolido.geolite import km_to_rad, rad_to_km
from editolido.route import Route

OGIMET_URL = "http://www.ogimet.com/display_gramet.php?" \
             "lang=en&hini={hini}&tref={tref}&hfin={hfin}&fl={fl}" \
             "&hl=3000&aero=yes&wmo={wmo}&submit=submit"


def ogimet_route(route, segment_size=300, debug=False,
                 name="", description=""):
    wmo_grid = GeoGridIndex()
    wmo_grid.load()
    start = route[0]
    end = route[-1]

    def print_ogimet(points):
        print('Route Ogimet (%s): %s' % (
            len(points), '_'.join([p.name for p in points])))

    # noinspection PyShadowingNames
    def build_ogimet(default_step):
        ogimet_sites = [start.name]
        previous = start
        ogimet_points = [start]
        sid = True
        neighbours = point = None
        for i, p in enumerate(
                route.split(60, converter=km_to_rad, preserve=True)):
            neighbours = sorted(
                wmo_grid.get_nearest_points(p, 30, converter=km_to_rad),
                key=lambda t: t[1])
            if i == 0:
                if neighbours:
                    if start.name not in [n.name for n, _ in neighbours]:
                        point, d = neighbours[0]
                        ogimet_points[0] = point
                        ogimet_sites[0] = point.name
                continue
            if neighbours:
                point, d = neighbours[0]
                if sid and point.distance_to(start, converter=rad_to_km) < 500:
                    step = min(60, default_step)
                else:
                    sid = False
                    step = default_step
                if point.name not in ogimet_sites and previous.distance_to(
                        point, converter=rad_to_km) > step:
                    previous = point
                    ogimet_points.append(point)
                    ogimet_sites.append(point.name)

        if point and neighbours:
            if end.name in [n.name for n, _ in neighbours] \
                    and end.name not in ogimet_sites:
                ogimet_points[-1] = end
            elif point.name not in ogimet_sites:
                ogimet_points.append(point)
        else:
            ogimet_points[-1] = end

        return ogimet_points

    step = start.distance_to(end, converter=rad_to_km) / 200
    ogimet_points = []
    while True:
        ogimet_points = build_ogimet(step)
        if len(ogimet_points) < 23:
            break
        if debug:
            print_ogimet(ogimet_points)
        step *= 2
    if debug:
        print_ogimet(ogimet_points)
    return Route(ogimet_points).split(
        segment_size, preserve=True, name=name, description=description)


def ogimet_url_and_route_and_tref(ofp, taxitime=15, debug=False):
    """
    Computes ogimet url
    :param ofp: OFP object
    :param taxitime: taxitime in minutes
    :param debug: True or False
    """
    hini = 0
    hfin = ofp.infos['duration'].hour + 1
    # timestamp for departure
    takeoff = ofp.infos['datetime'] + datetime.timedelta(minutes=taxitime)
    # http://stackoverflow.com/questions/15447632
    ts = calendar.timegm(takeoff.timetuple())
    # http://stackoverflow.com/questions/13890935
    now_ts = int(time.time())
    tref = max(now_ts, ts)  # for old ofp timeref=now
    # average flight level
    levels = list(map(int, re.findall(r'F(\d{3})\s', ofp.raw_fpl_text())))
    if levels:
        fl = sum(levels) / float(len(levels))
        fl = 10 * int(fl / 10)
    else:
        if debug:
            print('using default flight level')
        fl = 300
    name = ("Route Gramet {flight} {departure}-{destination} "
            "{tref_dt:%d%b%Y %H:%M}z OFP {ofp}".format(
                tref_dt=datetime.datetime.fromtimestamp(tref, tz=utc),
                **ofp.infos))
    route = ogimet_route(route=ofp.route, debug=debug, name=name)
    url = OGIMET_URL.format(
        hini=hini, tref=tref, hfin=hfin, fl=fl,
        wmo='%20'.join([p.name for p in route if p.name]))
    return url, route, tref


def get_gramet_image_url(url_or_fp):
    img_src = ogimet_serverid = ''
    if isinstance(url_or_fp, io.IOBase):
        # noinspection PyUnresolvedReferences
        data = url_or_fp.read()
        u = urlsplit(OGIMET_URL)
    else:
        u = urlsplit(url_or_fp)
        import requests
        r = requests.get(url_or_fp)
        data = r.text
        ogimet_serverid = r.cookies['ogimet_serverid']
    if data:
        m = re.search(r'<img src="([^"]+/gramet_[^"]+)"', data)
        if m:
            img_src = "{url.scheme}://{url.netloc}{path}".format(
                url=u, path=m.group(1))
    return img_src.replace(' ', '%20'), ogimet_serverid
