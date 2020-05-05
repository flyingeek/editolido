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
    split_route = route.split(60, converter=km_to_rad, preserve=True)

    def get_neighbour(point):
        neighbours = sorted(
            wmo_grid.get_nearest_points(point, 77.9, converter=km_to_rad),
            key=lambda t: t[1])
        if neighbours:
            if point.name in [n.name for n, _ in neighbours]:
                return point, 0
            return neighbours[0][0], neighbours[0][1]
        return None, None

    # Route using all ogimet neigbour points found
    points = []
    points_name = []
    results = []
    oIndex = {}
    d = split_route.distance(converter=rad_to_km)
    for p in split_route:
        neighbour, x = get_neighbour(p)
        if neighbour:
            if neighbour.name in oIndex:
                if oIndex[neighbour.name][0] > x:
                    oIndex[neighbour.name] = (x, p)
            else:
                oIndex[neighbour.name] = (x, p)
            results.append((p, neighbour, x))
            if neighbour.name not in points_name:
                points_name.append(neighbour.name)
                points.append(neighbour)
    results2 = []
    for p, o, xtd in results:
        if oIndex[o.name][1] == p:
            results2.append((p, o, xtd))

    # Check to see if an ogimet point is useful
    # We do this by comparing the xtd distance from the route
    # if we remove the point
    # The function is recursive
    def filter_by_xtd_at(i, r, ref):
        if i < len(r) - 1:
            segment = (r[i - 1][1], r[i + 1][1])
            xtd = abs(Route.xtd(ref[0], segment, converter=rad_to_km))
            print("checking %s xtd: %d  d: %d [%s, %s]" % (ref[1].name, xtd, ref[2], segment[0].name, segment[1].name))
            if xtd > ref[2]:
                print("should keep %s" % ref[1].name)
                return ref
            return None
        return None

    def filter_by_xtd_upto(i, j, r):
        for k in range(i, j):
            f = filter_by_xtd_at(i, r[:i] + r[k+1:], r[k])
            if not(f is None):
                return (f, k)
        return None

    def filter_by_xtd(r):
        print([o.name for p,o,xtd in r])
        res = [r[0]]
        i = 0
        while i <= (len(r) -1):
            i += 1
            if True or filter_by_xtd_at(i, r, r[i]):
                j = i + 1
                while j < len(r) - 1:
                    print("filter from:%s to:%s" % (r[i][1].name, r[j][1].name))
                    f = filter_by_xtd_upto(i, j, r)
                    if f is None:
                        j += 1
                    else:
                        print("keeping %s" % f[0][1].name)
                        if f[0][1].name not in [o.name for _, o, _ in res]:
                            res.append(f[0])
                        i = f[1]
                        break

        res.append(r[-1])
        return res
        # if len(res) < len(r):
        #     return filter_by_xtd(res)
        # else:
        #     return res

    def filter_by_xtd_old(r):
        res = [r[0]]
        for i in range(1, len(r) - 1):
            segment = (r[i - 1][1], r[i + 1][1])
            # cross track error from ogimet segment to route point
            xtd = abs(Route.xtd(r[i][0], segment, converter=rad_to_km))
            if xtd > r[i][2]:
                res.append(r[i])
        res.append(r[-1])
        if len(res) < len(r):
            return filter_by_xtd(res)
        else:
            return res
    points = [o for p, o, xtd in filter_by_xtd(results2)]
    # Reduce ogimet route size to 22 points
    # The distance of the new route is compared to the fpl route
    # We also attempt to reduce to 15 points and we keep
    # the best global score which is computed for route
    # containing 15 to 22 points
    global_score = -1
    global_best = points[:]
    while len(points) > 22:
        best_points = []
        best_score = -1
        for i in range(1, len(points)-1):
            guess = points[:i] + points[i+1:]
            distance = Route(points=guess).distance(converter=rad_to_km)
            score = abs(distance - d)
            if best_score > score or best_score < 0:
                best_points = guess[:]
                best_score = score
        points = best_points[:]
        if len(points) <= 22:
            if global_score > best_score or global_score < 0:
                global_best = best_points[:]
                global_score = best_score
                print('best_%d: %f' % (len(points), best_score))
    print(global_best)
    return Route(points=global_best).split(
        segment_size, preserve=True, name=name, description=description)
    # def print_ogimet(points):
    #     print('Route Ogimet (%s): %s' % (
    #         len(points), '_'.join([p.name for p in points])))
    #
    # # noinspection PyShadowingNames
    # def build_ogimet(default_step):
    #     point = None
    #     neighbours = get_neighbours(start)
    #     if neighbours and start.name not in [n.name for n, _ in neighbours]:
    #         ogimet_points = [neighbours[0][0]]
    #         ogimet_sites = [neighbours[0][0].name]
    #     else:
    #         ogimet_points = [start]
    #         ogimet_sites = [start.name]
    #     step = min(60, default_step)
    #     for p in split_route:
    #         neighbours = get_neighbours(p)
    #         if neighbours:
    #             point = neighbours[0][0]
    #             if (step != default_step
    #                     and point.distance_to(start, converter=rad_to_km) > 500):
    #                 step = default_step
    #             if (point.name not in ogimet_sites
    #                     and ogimet_points[-1].distance_to(point, converter=rad_to_km) > step):
    #                 ogimet_points.append(point)
    #                 ogimet_sites.append(point.name)
    #
    #     if point and neighbours:
    #         if end.name in [n.name for n, _ in neighbours] \
    #                 and end.name not in ogimet_sites:
    #             ogimet_points[-1] = end
    #         elif point.name not in ogimet_sites:
    #             ogimet_points.append(point)
    #     else:
    #         ogimet_points[-1] = end
    #
    #     return ogimet_points
    #
    # step = start.distance_to(end, converter=rad_to_km) / 200
    #
    # while True:
    #     ogimet_points = build_ogimet(step)
    #     for p in ogimet_points[1:]:
    #         print((p.name,previous.distance_to(p, converter=rad_to_km)))
    #         previous = p
    #     if len(ogimet_points) < 22:
    #         break
    #     if debug:
    #         print_ogimet(ogimet_points)
    #     step *= 2
    # if debug:
    #     print_ogimet(ogimet_points)
    # return Route(ogimet_points).split(
    #     segment_size, preserve=True, name=name, description=description)


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
    print(route)
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
