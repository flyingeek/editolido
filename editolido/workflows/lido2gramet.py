# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import json
import requests


def get_sigmets_json():
    r = requests.get(
        'http://www.aviationweather.gov/gis/scripts/IsigmetJSON.php'
        '?type=all&bbox=-180,-90,180,90')
    return r.json() or {}


def add_sigmets(kml, folder, jsondata):
    from editolido.geopoint import GeoPoint
    from editolido.route import Route
    for d in jsondata['features']:
        props = d['properties']
        geom = d['geometry']
        name = "{firName}: {qualifier} {hazard}".format(**props)
        description = "{rawSigmet}".format(**props)
        if geom['type'] == 'LineString':
            geom['coordinates'] = [geom['coordinates']]
        if geom['type'] in ('Polygon', 'LineString'):
            for area in geom['coordinates']:
                route = Route(
                    [GeoPoint((lat, lon)) for lon, lat in area],
                    name=name,
                    description=description
                )
                kml.add_line(folder, route)
                kml.add_point(
                    folder,
                    GeoPoint.get_center(
                        route,
                        name=name, description=description),
                )
        elif geom['type'] == 'Point':
            kml.add_point(
                folder,
                GeoPoint(
                    (geom['coordinates'][1], geom['coordinates'][0]),
                    name=name, description=description),
            )
        else:
            print(d)
            print('unknown geometry type: %s' % geom['type'])
            raise ValueError


def lido2gramet(action_in, params=None):
    """
     Puts the Ogimet/Gramet route in the clipboard
     Output kml route if params['Afficher Ogimet'] is True
    :param action_in: the OFP text
    :param params: workflow action parameters
    :return: unicode kml or None

    Usage from Editorial is:

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals
    import workflow
    from editolido.workflows.lido2gramet import lido2gramet


    params = workflow.get_parameters()
    action_in = workflow.get_input()
    workflow.set_output(lido2gramet(action_in, params=params))
    """
    import datetime
    from editolido.ofp import OFP
    from editolido.ofp_infos import utc
    from editolido.kml import KMLGenerator
    from editolido.ogimet import \
        ogimet_url_and_route_and_tref,\
        get_gramet_image_url
    from editolido.constants import PIN_ORANGE
    params = params or {}
    ofp = OFP(action_in)
    kml = KMLGenerator()
    taxitime = (ofp.infos['taxitime'] or
                int(params.get('Temps de roulage', '') or '15'))
    ogimet_url, route, tref = ogimet_url_and_route_and_tref(ofp,
                                                            taxitime=taxitime)
    url, ogimet_serverid = get_gramet_image_url(ogimet_url)
    url = url or ogimet_url
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    import clipboard  # EDITORIAL module
    clipboard.set(url)

    switch_sigmets = params.get('Afficher SIGMETs', True)
    switch_ogimet = params.get('Afficher Ogimet', True)

    switch_kml = params.get('Générer KML', None)  # 1.0.x compatibility
    if switch_kml is not None:
        switch_ogimet = switch_sigmets = switch_kml

    if switch_ogimet:
        kml.add_folder('ogimet')
        kml.add_line('ogimet', route)

    if switch_sigmets:
        pin_sigmets = params.get('Label SIGMET', PIN_ORANGE)
        kml.add_folder('SIGMETs', pin=pin_sigmets)
        try:
            jsondata = get_sigmets_json() or {}
        except requests.exceptions.RequestException:
            pass
        else:
            try:
                add_sigmets(kml, 'SIGMETs', jsondata)
            except ValueError:
                pass

    name = ("Route Gramet/SIGMETs {flight} {departure}-{destination} "
            "{tref_dt:%d%b%Y %H:%M}z OFP {ofp}".format(
                tref_dt=datetime.datetime.fromtimestamp(tref, tz=utc),
                **ofp.infos))
    if switch_ogimet or switch_sigmets:
        kml = kml.render(
            name=name,
            ogimet_color=params.get('Couleur Ogimet', '') or '40FF0000',
            SIGMETs_color=params.get('Couleur SIGMET', '') or '50143CFA')
        try:
            # noinspection PyUnresolvedReferences,PyPackageRequirements
            import clipboard  # EDITORIAL Module
            json_results = {
                'type': '__editolido__.extended_clipboard',
                'gramet_url': url,
                'ogimet_url': ogimet_url,
                'ogimet_serverid': ogimet_serverid,
                'kml': kml,
            }
            clipboard.set(json.dumps(json_results))
        except ImportError:
            pass
        return kml
    try:
        # noinspection PyUnresolvedReferences,PyPackageRequirements
        import clipboard  # EDITORIAL Module
        json_results = {
            'type': '__editolido__.extended_clipboard',
            'gramet_url': url,
            'ogimet_url': ogimet_url,
            'ogimet_serverid': ogimet_serverid,
            'kml': '',
        }
        clipboard.set(json.dumps(json_results))
    except ImportError:
        pass
    return ''
