# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from editolido.constants import PIN_ORANGE
from editolido.workflows.lido2gramet import lido2gramet, add_sigmets
from editolido.kml import KMLGenerator


def test_add_sigmets(sigmets_json):
    kml = KMLGenerator()
    kml.add_folder('sigmets', pin=PIN_ORANGE)
    add_sigmets(kml, 'sigmets', sigmets_json)
    out = kml.render_folder('sigmets')
    assert out
    assert '#placemark-orange' in out
    assert '#sigmets' in out


def test_lido2gramet_output_is_kml(ofp_text):
    # do not request sigmets here, them them in test_add_sigmets
    # otherwise json is requested in a fixture loop
    params = {'Afficher Ogimet': True, 'Afficher SIGMETs': False}
    output = lido2gramet(
        ofp_text, params, debug=False)
    assert '<kml ' in output

