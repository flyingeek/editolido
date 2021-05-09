# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import datetime
import calendar
import io
import time
import re
from collections import namedtuple
from editolido.ofp_infos import utc
from editolido.route import Route

try:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from urlparse import urlsplit
except ImportError:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from urllib.parse import urlsplit

from editolido.geoindex import GeoGridIndex
from editolido.geolite import km_to_rad, rad_to_km

# noinspection SpellCheckingInspection
OGIMET_URL = "http://www.ogimet.com/display_gramet.php?" \
             "lang=en&hini={hini}&tref={tref}&hfin={hfin}&fl={fl}" \
             "&hl=3000&aero=yes&wmo={wmo}&submit=submit"

Result = namedtuple('Result', ['fpl', 'ogimet'])


def lowest_crs_index(results):
    """
    Index to the point which causes the smallest course change if removed
    :param results: [Result]
    :return: int
    """
    best_diff = 0
    best = None
    maxi = len(results) - 1
    for i, r in enumerate(results):
        if 1 <= i < maxi:
            diff = abs(
                results[i - 1].ogimet.course_to(results[i].ogimet)
                - results[i - 1].ogimet.course_to(results[i+1].ogimet)
            )
            if best is None or diff < best_diff:
                best = i
                best_diff = diff
    return best


def lowest_xtd_index(results):
    """
    Index to the point which causes the less xtd loss if removed
    :param results: [Result]
    :return: int
    """
    best_xtd = 0
    best = None
    maxi = len(results) - 1
    for i, r in enumerate(results):
        if 1 <= i < maxi:
            xtd = abs(
                r.fpl.xtd_to((results[i - 1].ogimet, results[i + 1].ogimet))
            )
            if best is None or xtd < best_xtd:
                best = i
                best_xtd = xtd
    return best


def get_nearest_wmo(route, wmo_grid):
    # Here we find all ogimet points for our route
    # The same ogimet point can be used by many fpl points
    # prepare o_index which will be used to deduplicate
    # we place in o_index points with the shortest distance
    ogimet_results = []
    o_index = {}
    neighbour_radius = (rad_to_km(wmo_grid.grid_size) / 2.0) - 0.1

    def get_neighbour(point):
        """
        Find neighbour ogimet point
        Prefer fpl point if it exists
        :param point:
        :return: tuple(Geopoint, float)
        """
        neighbours = sorted(
            wmo_grid.get_nearest_points(point, neighbour_radius),
            key=lambda t: t[1]
        )
        if neighbours:
            if point.name in [n.name for n, _ in neighbours]:
                return point, 0
            return neighbours[0][0], neighbours[0][1]
        return None, None

    for p in route.split(60, converter=km_to_rad, preserve=True):
        neighbour, x = get_neighbour(p)
        if neighbour:
            if neighbour.name in o_index:
                if o_index[neighbour.name][0] > x:
                    o_index[neighbour.name] = (x, p)
            else:
                o_index[neighbour.name] = (x, p)
            ogimet_results.append(Result(p, neighbour))

    # filter using o_index (keep points that were stored in o.index)
    return list(
        filter(lambda r: o_index[r.ogimet.name][1] == r.fpl, ogimet_results)
    )


def reduce_results(results):
    # Reduce ogimet route size to 22 points
    # We have to loose precision, we score the lowest xtd loss
    # as an alternative you may use lowest_crs_index but I did
    # not find major gain yet.
    while len(results) > 21:
        idx = lowest_xtd_index(results)
        results = results[:idx] + results[idx+1:]
    return results


def ogimet_route(route, segment_size=300, name="", description=""):

    wmo_grid = GeoGridIndex()
    wmo_grid.load()

    def find_strategic(start, end, results):
        """
        Find point you can not suppress without increasing xtd
        :param start: int
        :param end: int
        :param results: [Result]
        :return:
        """
        # search in reverse order to stop at the latest point in the route direction
        # in segment [i, j] we try to remove inner elements by checking the xtd
        for k in range(end - 1, start, -1):
            # xtd from ogimet point to fpl segment
            o_xtd = results[k].ogimet.xtd_to(
                (results[k].fpl, results[k + 1].fpl)
            )
            # xtd from fpl point to ogimet segment
            f_xtd = results[k].fpl.xtd_to(
                (results[start].ogimet, results[end].ogimet)
            )
            if abs(f_xtd) > abs(o_xtd):
                fpl_d = results[k].fpl.distance_to(results[k + 1].fpl)
                if abs(f_xtd) < fpl_d:
                    return k
        return None

    def filter_by_xtd(results):
        """
        Here we keep significant ogimet points.

        By significant, I mean points which increase the xtd if missing.
        The algorithm is recursive, if route is A B C D E F
        and ogimet route found is A B'C'D'E'F
        We try to suppress B', if successful we try to suppress C' and so on
        For example if B', C' and E' are not relevant the loop
        will try to suppress B' and C', then it will keep D' and
        start again from D' to suppress E' and keep F
        At the end we try again (recursion) until the route size is constant.
        For information a typical NAT route will reduce from 26 to 15 points
        and a flight to NRT will end with 26 points (starting from 79)
        :param results: [Result]
        :return: [Result]
        """
        res = [results[0]]
        i = -1
        while i < (len(results) - 1):
            i += 1
            j = i + 2
            # we try to remove many consecutive points until it fails
            while j <= len(results) - 1:
                k = find_strategic(i, j, results)
                if k is None:
                    j += 1  # no significant point yet, try to extend to next
                else:
                    # a significant point was found, store it
                    if results[k].ogimet.name not in [o.name for _, o in res]:
                        res.append(results[k])
                    i = k - 1  # will start at k on next round
                    break
        res.append(results[-1])
        # recursion works, so try it until there is no change
        if len(res) < len(results):
            return filter_by_xtd(res)
        else:
            return res

    ogimet_results = get_nearest_wmo(route, wmo_grid)
    # keep only significant points (strategic points)
    ogimet_results = filter_by_xtd(ogimet_results)
    # enforce max ogimet length
    ogimet_results = reduce_results(ogimet_results)

    return Route(points=[ogimet for _, ogimet in ogimet_results]).split(
        segment_size, preserve=True, name=name, description=description)


def ogimet_url_and_route_and_tref(ofp, taxitime=15):
    """
    Computes ogimet url
    :param ofp: OFP object
    :param taxitime: taxitime in minutes
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
    levels = list(map(int, re.findall(r'F(\d{3})\s', ofp.raw_fpl_text)))
    if levels:
        fl = sum(levels) / float(len(levels))
        fl = 10 * int(fl / 10)
    else:
        fl = 300
    name = ("Route Gramet {flight} {departure}-{destination} "
            "{tref_dt:%d%b%Y %H:%M}z OFP {ofp}".format(
                tref_dt=datetime.datetime.fromtimestamp(tref, tz=utc),
                **ofp.infos))
    route = ogimet_route(route=ofp.route, name=name)
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
