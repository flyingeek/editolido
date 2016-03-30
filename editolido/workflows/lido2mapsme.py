# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os


def get_abspath(relpath):
    return os.path.join(os.path.expanduser('~/Documents'), relpath)


def lido2mapsme(action_in, params, debug=False):
    """
    Lido2Mapsme KML rendering action
    :param action_in: unicode action input
    :param params: dict action's parameters
    :param debug: bool determines wether or not to print ogimet debug messages
    :return:
    """
    from editolido.constants import NAT_POSITION_ENTRY, PIN_NONE, PIN_PINK
    from editolido.geopoint import GeoPoint
    from editolido.kml import KMLGenerator
    from editolido.ofp import OFP
    from editolido.route import Route
    from editolido.ogimet import ogimet_route
    ofp = OFP(action_in)
    kml = KMLGenerator()

    kml.add_folders('greatcircle', 'ogimet', 'rnat', 'ralt', 'rmain')
    route_name = "{departure}-{destination}".format(**ofp.infos)
    route = ofp.route
    route.name = route_name
    route.description = ofp.description

    natmarks = []
    if params.get('Afficher NAT', False):
        pin_pos = 0 if params['Position repère'] == NAT_POSITION_ENTRY else -1
        pin_style = params.get('Repère NAT', PIN_NONE)
        for track in ofp.tracks:
            if track:
                kml.add_line('rnat', track)
                if pin_style != PIN_NONE:
                    if track.is_mine:
                        p = GeoPoint(track[0], name=track.name,
                                     description=track.description)
                        natmarks.append(p)
                        kml.add_point('rnat', p, style=pin_style)
                        p = GeoPoint(track[-1], name=track.name,
                                     description=track.description)
                        natmarks.append(p)
                        kml.add_point('rnat', p, style=pin_style)
                    else:
                        p = GeoPoint(track[pin_pos], name=track.name,
                                     description=track.description)
                        natmarks.append(p)
                        kml.add_point('rnat', p, style=pin_style)
            else:
                print("empty track found %s" % track.name)

    if params.get('Afficher Ortho', False):
        greatcircle = Route((route[0], route[-1])).split(
            300, name="Ortho %s" % route_name)
        kml.add_line('greatcircle', greatcircle)

    kml.add_line('rmain', route)
    if params.get('Point Route', PIN_NONE) != PIN_NONE:
        kml.add_points('rmain', route,
                       excluded=natmarks, style=params['Point Route'])

    if params.get('Afficher Dégagement', False):
        alt_route = Route(ofp.wpt_coordinates_alternate,
                          name="Route Dégagement")
        kml.add_line('ralt', alt_route)
        if params.get('Point Dégagement', PIN_NONE) != PIN_NONE:
            kml.add_points(
                'ralt', alt_route[1:],
                style=params.get('Point Dégagement', PIN_PINK))

    if params.get('Afficher Ogimet', False):
        kml.add_line('ogimet',
                     ogimet_route(route, debug=debug, name="Ogimet Route"))

    return kml.render(
        name=ofp.description,
        rnat_color=params.get('Couleur NAT', '') or '60DA25A8',
        ogimet_color=params.get('Couleur Ogimet', '')  or '50FF0000',
        greatcircle_color=params.get('Couleur Ortho', '')  or '5F1478FF',
        rmain_color=params.get('Couleur Route', '')  or 'FFDA25A8',
        ralt_color=params.get('Couleur Dégagement', '') or 'FFFF00FF'
    )


def load_or_save(action_in, save=None, reldir=None, filename=None):
    """
    Load/Save action input
    :param action_in: workflow action input
    :param save: bool switch to save or not
    :param reldir: relative path to folder containing the saved elements
    :param filename: filename to use (Python template format)
    :return: unicode action_out

    Usage from Editorial is:

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals
    import workflow
    from editolido.workflows.lido2mapsme import load_or_save


    params = workflow.get_parameters()
    filename = params.get('Nom', '') or '{flight}_{departure}-{destination}_{date}_{datetime:%H:%M}z_OFP_{ofp}.txt'
    action_in = workflow.get_input()
    save = params.get('Sauvegarder', False)
    reldir = params.get('Dossier', '') or '_lido2mapsme_/data'
    workflow.set_output(load_or_save(action_in, save=save, reldir=reldir, filename=filename))
    """
    import console  # EDITORIAL module
    import dialogs  # EDITORIAL module
    import editor  # EDITORIAL module

    from editolido.ofp import OFP
    ofp = None
    if action_in:
        ofp = OFP(action_in)
        if not ofp.infos:
            save = True  # force saving of unknown ofp
    if save and action_in:
        absdir = get_abspath(reldir)
        if not os.path.exists(absdir):
            os.makedirs(absdir)
        try:
            relpath = os.path.join(
                reldir, filename.format(**ofp.infos).replace('/', '_'))
        except TypeError:
            editor.set_file_contents(
                os.path.join(reldir, '_ofp_non_reconnu_.txt'),
                action_in.encode('utf-8'))
            print("OFP non reconnu, merci de créer un ticket (issue) sur:")
            print("https://github.com/flyingeek/editolido/issues")
            print("N'oubliez pas de joindre votre OFP en pdf.")
            print("Vous pouvez aussi le poster sur Yammer (groupe Mapsme)")
            raise KeyboardInterrupt
        else:
            editor.set_file_contents(relpath, action_in.encode('utf-8'))
    elif not action_in:  # Load
        try:
            files = os.listdir(get_abspath(reldir))
            if not files:
                raise OSError
        except OSError:
            console.alert('Aucune sauvegarde disponible',
                          'sauvegarder au moins une fois',
                          'Annuler',
                          hide_cancel_button=True)
            raise KeyboardInterrupt
        else:
            filename = dialogs.list_dialog('Choisir un fichier', files)
            if not filename:
                raise KeyboardInterrupt
            relpath = os.path.join(reldir, filename)
            content = editor.get_file_contents(relpath)
            return content.decode('utf-8') if content else ''
    return action_in


def save_kml(content, save=None, reldir=None, filename=None, workflow_in=None):
    """

    :param content:
    :param save:
    :param reldir:
    :param filename:
    :param workflow_in:
    :return:

    Usage from Editorial is:

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals
    import workflow
    from editolido.workflows.lido2mapsme import save_kml


    params = workflow.get_parameters()
    filename = params.get('Nom', '') or  '{flight}_{departure}-{destination}_{date}_{datetime:%H:%M}z_OFP_{ofp}.kml'
    workflow_in = workflow.get_variable('workflow_in')
    save = params.get('Sauvegarder', False)
    content = params.get('Contenu', '') or workflow.get_input()
    reldir = params.get('Dossier', '') or '_lido2mapsme_/KML'
    workflow.set_output(save_kml(content, save=save, reldir=reldir, filename=filename, workflow_in=workflow_in))
    """
    import editor  # EDITORIAL module

    if save:
        from editolido.ofp import OFP
        ofp = OFP(workflow_in)
        absdir = get_abspath(reldir)
        if content:
            if not os.path.exists(absdir):
                os.makedirs(absdir)
            try:
                relpath = os.path.join(
                    reldir,
                    filename.format(**ofp.infos).replace('/', '_'))
            except TypeError:
                relpath = os.path.join(reldir,
                                       '_ofp_non_reconnu_.kml')
            editor.set_file_contents(relpath,
                                     content.encode('utf-8'))
    return content
