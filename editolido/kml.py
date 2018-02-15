# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
import io
import os
from editolido.constants import PINS, GOOGLE_ICONS, PIN_NONE

try:
    integer_types = (int, long,)
except NameError:
    integer_types = (int,)

default_linestyle = """
    <Style id='{0}'>
        <LineStyle>
            <width>6</width>
            <color>{{{0}_color}}</color>
        </LineStyle>
    </Style>
"""
default_iconstyle = """
    <Style id='{0}'>
        <IconStyle>
            <Icon>
                <href><![CDATA[{1}]]></href>
            </Icon>
            <hotSpot x="0.5"  y="0.0" xunits="fraction" yunits="fraction"/>
        </IconStyle>
    </Style>
"""


class KMLGenerator(object):
    def __init__(self, template=None, point_template=None, line_template=None,
                 folder_template=None, style_template=default_linestyle,
                 icon_template=default_iconstyle, segment_template=None,
                 icons=GOOGLE_ICONS):
        datadir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'data')

        def read_template(name):
            with io.open(os.path.join(datadir, name),
                         encoding='utf-8') as f:
                return f.read()

        self.template = (template
                         or read_template('mapsme_template.kml'))
        self.point_template = (point_template
                               or read_template('mapsme_point_tpl.kml'))
        self.line_template = (line_template
                              or read_template('mapsme_line_tpl.kml'))
        self.folder_template = (folder_template
                                or read_template('mapsme_folder_tpl.kml'))
        self.segment_template = (segment_template
                                 or read_template('mapsme_segment_tpl.kml'))
        self.style_template = style_template
        self.icon_template = icon_template
        self.folders = OrderedDict()
        self.styles = OrderedDict()
        self.folder_styles = OrderedDict()
        self.icons = icons

    @staticmethod
    def escape(text):
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace("&", "&amp;")
        text = text.replace("\"", "&quot;")
        return text

    def add_folder(self, name, pin=PIN_NONE):
        """
        Add a folder and a style to the kml
        If there is no pin you must specify style for points added into
        that folder
        :param name: the folder name
        :param pin: a default pin for points in the folder
        """
        self.folders[name] = []
        style = self.style_template.format(name)
        if pin != PIN_NONE:
            style += self.icon_template.format(PINS[pin][1:], self.icons[pin])
        self.styles[name] = style
        self.folder_styles[name] = PINS[pin]

    def add_folders(self, *values):
        for value in values:
            try:
                name, pin = value
            except ValueError:
                name = value
                pin = PIN_NONE
            self.add_folder(name, pin)

    @staticmethod
    def _update_kwargs(folder, kwargs):
        """
        Apply style value based on context
        - if style is not set, uses folder name
        - if style is integer, replace with the style's name
        :param folder: str
        :param kwargs: list
        """
        style = kwargs.get('style', None)
        if style is None:
            kwargs['style'] = '#' + folder
        elif isinstance(style, integer_types):
            kwargs['style'] = PINS[style]

    def add_line(self, folder, route, **kwargs):
        """
        Add a route as a LineString in the .kml
        :param folder: folder name
        :param route: Route
        :param kwargs: optional args passed to the renderer
        """
        self._update_kwargs(folder, kwargs)
        coordinates = []
        for p in route:
            coordinates.append(
                "{lng:.6f},{lat:.6f}".format(lat=p.latitude, lng=p.longitude))
        variables = dict(
            name=route.name or '',
            description=route.description or '')
        variables.update(kwargs)
        self.folders[folder].append(self.line_template.format(
            coordinates=' '.join(coordinates),
            **variables))

    def add_points(self, folder, route, excluded=None, **kwargs):
        """
        Add a route as a Points in the .kml
        :param folder: folder name
        :param route: Route
        :param excluded: list of GeoPoint to exclude from rendering
        :param kwargs: optional args passed to the renderer

        If folder does not have a pin set, points must define style kwargs
        otherwise nothing is added
        """
        self._update_kwargs(folder, kwargs)
        excluded = excluded or []
        for geopoint in route:
            if geopoint not in excluded:
                self.add_point(folder, geopoint, **kwargs)

    def add_point(self, folder, geopoint, **kwargs):
        """
        Add a GeoPoint in the .kml
        :param folder: folder name
        :param geopoint: GeoPoint
        :param kwargs: optional args passed to the renderer

        If folder does not have a pin set, point must define style kwargs
        otherwise nothing is added
        """
        kwargs.setdefault('style', self.folder_styles[folder])
        self._update_kwargs(folder, kwargs)
        if kwargs['style'] != PINS[PIN_NONE]:
            coordinates = "{lng:.6f},{lat:.6f}".format(
                lat=geopoint.latitude, lng=geopoint.longitude)
            variables = dict(
                name=geopoint.name or geopoint.dm,
                description=geopoint.description or '')
            variables.update(kwargs)
            self.folders[folder].append(self.point_template.format(
                coordinates=coordinates,
                **variables))

    def add_segments(self, folder, route, **kwargs):
        """
        Add a route as LineString segments in the .kml
        :param folder: folder name
        :param route: Route
        :param kwargs: optional args passed to the renderer
        """
        self._update_kwargs(folder, kwargs)
        for p1, p2 in route.segments:
            coordinates = "{p1.longitude:.6f},{p1.latitude:.6f} " \
                          "{p2.longitude:.6f},{p2.latitude:.6f}".format(
                              p1=p1, p2=p2)
            variables = dict(
                name="{label}: {p1}->{p2}".format(
                    label=route.name or folder,
                    p1=p1.name or p1.dm,
                    p2=p2.name or p2.dm))
            variables.update(kwargs)
            self.folders[folder].append(self.segment_template.format(
                coordinates=coordinates,
                **variables))

    def render(self, **kwargs):
        """
        Render the full .kml
        :param kwargs:
        :return: unicode
        """
        return self.template.format(
            styles=''.join(self.styles.values()).format(**kwargs),
            folders=self.render_folders(),
            **kwargs
        )

    def render_folder(self, folder):
        """
        Render a folder content
        :param folder:
        :return: str
        """
        return self.folder_template.format(
            name=folder,
            open=1,
            content='\n'.join(self.folders[folder]),
        )

    def render_folders(self):
        """
        Render all folders
        :return: str
        """
        return '\n'.join(
            [self.render_folder(folder) for folder in self.folders])
