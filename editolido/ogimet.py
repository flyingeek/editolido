# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from editolido.geoindex import GeoGridIndex
from editolido.geolite import km_to_rad, rad_to_km
from editolido.geopoint import GeoPoint
from editolido.route import Route


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
            if end.name in [n.name for n, _ in neighbours] and end.name not in ogimet_sites:
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
