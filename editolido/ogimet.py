# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import datetime
import calendar
import io
import time
import re
from collections import namedtuple
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
    Result = namedtuple('Result', ['fpl', 'ogimet'])
    wmo_grid = GeoGridIndex()
    wmo_grid.load()
    split_route = route.split(60, converter=km_to_rad, preserve=True)
    d = split_route.distance(converter=rad_to_km)

    def get_neighbour(point):
        """
        Find neighbour ogimet point
        Prefer fpl point if it exists
        :param point:
        :return: tuple(Geopoint, float)
        """
        neighbours = sorted(
            wmo_grid.get_nearest_points(point, 77.9, converter=km_to_rad),
            key=lambda t: t[1])
        if neighbours:
            if point.name in [n.name for n, _ in neighbours]:
                return point, 0
            return neighbours[0][0], neighbours[0][1]
        return None, None

    # Here we find all ogimet points for our route
    # The same ogimet point can be used by many fpl points
    # prepare oIndex which will be used to deduplicates
    # we place in oIndex points with the shortest distance
    results = []
    oIndex = {}
    for p in split_route:
        neighbour, x = get_neighbour(p)
        if neighbour:
            if neighbour.name in oIndex:
                if oIndex[neighbour.name][0] > x:
                    oIndex[neighbour.name] = (x, p)
            else:
                oIndex[neighbour.name] = (x, p)
            results.append(Result(p, neighbour))
    # filter results using oIndex
    results = list(filter(lambda r: oIndex[r.ogimet.name][1] == r.fpl, results))

    def find_strategic(i, j, results):
        """
        Find point you can not suppress without increasing xtd
        :param i: int
        :param j: int
        :param results: [Result]
        :return:
        """
        # search in reverse order to stop at the latest point in the route direction
        # in segment [i, j] we try to remove inner elements by checking the xtd
        for k in range(j - 1, i, -1):
            # xtd from ogimet point to fpl segment
            oxtd = Route.xtd(results[k].ogimet, (results[k].fpl, results[k + 1].fpl))
            # xtd from fpl point to ogimet segment
            xtd = Route.xtd(results[k].fpl, (results[i].ogimet, results[j].ogimet))
            # info = ("%s xtd: %f  d: %f [%s, %s]" % (results[k].ogimet.name, xtd, oxtd, results[i].ogimet.name, results[j].ogimet.name))
            if abs(xtd) > abs(oxtd):
                # print("+" + info)
                return k
            # print("-" + info)
        return None

    def filter_by_xtd(r):
        """
        Here we keep significants ogimet points.

        By significants, I mean points which increase the xtd if missing.
        The algorithm is recursive, if route is A B C D E F
        and ogimet route found is A B'C'D'E'F
        We try to suppress B', if successful we try to suppress C' and so on
        For example if B', C' and E' are not relevant the loop
        will try to suppress B' and C', then it will keep D' and
        start again from D' to suppress E' and keep F
        At the end we try again (recursion) until the route size is constant.
        For information a typical NAT route will reduce from 26 to 15 points
        and a flight to NRT will end with 26 points (starting from 79)
        :param r: [Result]
        :return: [Result]
        """
        res = [r[0]]
        i = -1
        while i < (len(r) - 1):
            i += 1
            j = i + 2
            while j <= len(r) - 1:
                k = find_strategic(i, j, r)
                if k is None:
                    j += 1
                else:
                    if r[k].ogimet.name not in [o.name for _, o in res]:
                        res.append(r[k])
                    i = k - 1  # will start at k on next round
                    break
        res.append(r[-1])
        if len(res) < len(r):
            return filter_by_xtd(res)
        else:
            return res

    results = filter_by_xtd(results)

    # Reduce ogimet route size to 22 points
    # We have to loose precision, we use a stupid? score
    # which is lowest xtd loss
    while len(results) > 22:
        best_xtd = 0
        best = None
        maxi = len(results) - 1
        for i, r in enumerate(results):
            if 1 <= i < maxi:
                xtd = abs(
                    Route.xtd(r.fpl,
                              (results[i - 1].ogimet, results[i + 1].ogimet)
                              )
                )
                if best is None or xtd < best_xtd:
                    best = i
                    best_xtd = xtd
        results = results[:best] + results[best+1:]

    points = [o for p, o in results]
    return Route(points=points).split(
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
        wmo='_'.join([p.name for p in route if p.name]))
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
    return img_src, ogimet_serverid
