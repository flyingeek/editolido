# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import itertools
import re
from datetime import datetime, timedelta, tzinfo, time
from editolido.route import Route, Track
from editolido.geopoint import GeoPoint, dm_normalizer, arinc_normalizer

MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
          'Nov', 'Dec')

ZERO = timedelta(0)


# A UTC class.
class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return b"UTC"

    def dst(self, dt):
        return ZERO
utc = UTC()


class OFP(object):
    def __init__(self, text):
        self.text = text
        self._infos = None
        self._fpl_route = None
        self._route = None
        self._raw_fpl = None

    @classmethod
    def log_error(cls, message):  # pragma no cover
        print(message)
        print("retry or send OFP to Yammer's group Maps.me")
        print("or https://github.com/flyingeek/editolido/issues")

    @staticmethod
    def extract(text, start, end, end_is_optional=True, inclusive=False):
        """
        Extract in text between start and end marks
        :param text: unicode
        :param start: unicode or None
        :param end: unicode or None
        :param end_is_optional: if end is missing, captures till EOF
        :param inclusive: if True, captures start and end
        :return: unicode
        """
        if start:
            try:
                s = text.split(start, 1)[1]
            except IndexError:
                raise LookupError
            if inclusive:
                s = start + s
        else:
            s = text

        if not end:
            return s

        try:
            s, _ = s.split(end, 1)
        except ValueError:
            if not end_is_optional:
                raise EOFError
        if inclusive:
            s += end
        return s

    def get_between(self, start, end, end_is_optional=True, inclusive=False):
        """
        Get text between start and end marks
        :param start: unicode or None
        :param end: unicode or None
        :param end_is_optional: if end is missing, captures till EOF
        :param inclusive: if True, captures start and end
        :return: unicode
        """
        return self.extract(
            self.text,
            start, end,
            end_is_optional=end_is_optional, inclusive=inclusive)

    @property
    def description(self, tpl="{flight} {departure}-{destination} {date} "
                              "{datetime:%H:%M}z OFP {ofp}"):
        return tpl.format(**self.infos)

    @staticmethod
    def wpt_coordinates_generator(text):
        for m in re.finditer(r'(\S+|\s+)\s+([NS]\d{4}\.\d)([EW]\d{5}\.\d)',
                             text):
            yield GeoPoint(
                (m.group(2), m.group(3)),
                name=m.group(1).strip(), normalizer=dm_normalizer
            )

    @property
    def wpt_coordinates(self):
        """
        Return a generator of the ofp's wpt_coordinates
        """
        tag = 'WPT COORDINATES'
        try:
            s = self.get_between(tag, '----')
        except LookupError:
            self.log_error("%s not found" % tag)
            raise KeyboardInterrupt
        return self.wpt_coordinates_generator(s)

    @property
    def route(self):
        """
        Return a Route of the wpt_coordinates
        """
        if self._route is None:
            self._route = Route(self.wpt_coordinates)
        return self._route

    @property
    def wpt_coordinates_alternate(self):
        """
        Return a generator of the ofp's wpt_coordinates for alternate
        """
        start = 'WPT COORDINATES'
        end = 'ATC FLIGHT PLAN'
        try:
            s = self.get_between(start, end, end_is_optional=False)
        except LookupError:
            self.log_error("%s not found" % start)
        except EOFError():
            self.log_error('%s not found' % end)
        else:
            try:
                s = s.rsplit('----', 1)[1]
            except IndexError:
                self.log_error('---- not found while '
                               'extracting alternate coordinates')
            else:
                return self.wpt_coordinates_generator(s)
        return []

    def tracks_iterator(self):
        """
        Tracks Iterator
        :return: iterator of tuple (letter, full description)
        """
        s = self.get_between('TRACKSNAT', 'NOTES:')
        if 'REMARKS:' in s:
            s = s.split('REMARKS:', 1)[0]  # now REMARKS: instead of NOTES:
            s = s.split('Generated at')[0]
        if ' LVLS ' in s:
            # old mode, split at track letter, discard first part.
            it = iter(re.split(r'(?:\s|[^A-Z\d])([A-Z])\s{3}', s)[1:])
            return itertools.izip(it, it)
        else:
            def updated_mar2016_generator():
                # Letter is lost in the middle
                # track route starts with something like ELSIR 50
                l = [m.start() for m in re.finditer('[A-Z]{5} \d\d', s)]
                for start, end in itertools.izip_longest(l, l[1:]):
                    t = s[start:end]
                    # letter is here
                    parts = re.split('([A-Z])LVLS', t)
                    # adds some missing spaces
                    parts[2] = parts[2].replace(
                        'LVLS', ' LVLS').replace('NIL', 'NIL ')
                    yield parts[1], "%s LVLS%s" % (parts[0], parts[2])
            return updated_mar2016_generator()

    @staticmethod
    def fpl_track_label(letter):
        """
        return the label designating the track in the FPL
        """
        return "NAT%s" % letter

    def is_my_track(self, letter):
        """
        Checks if the designated track is in the fpl
        """
        if not self.fpl_route:
            return False
        return self.fpl_track_label(letter) in self.fpl_route[1:-1]

    @property
    def tracks(self):
        """
        Yield a route for each track found
        Note: track points only include arinc points (no entry or exit point)
        :return: generator
        """
        try:
            tracks = self.tracks_iterator()
        except (LookupError, IndexError):
            raise StopIteration

        # noinspection PyShadowingNames
        def nat_route_generator(text, label_dict=None):
            track_points = [p.strip() for p in text.split(' ') if p.strip()]

            for label in track_points:
                m = re.match(
                    r'(\d{2,4}[NS]\d{3,5}[EW]|[NESW]\d{4}|\d[NESW]\d{3}[^EW])',
                    label
                )
                if m:
                    yield GeoPoint(label, normalizer=arinc_normalizer,
                                   name=label)
                elif label_dict and label in label_dict:
                    yield label_dict[label]

        for letter, description in tracks:
            is_mine = self.is_my_track(letter)
            label_dict = None
            if is_mine:
                label_dict = {p.name: p for p in self.route if p.name}
            yield Track(
                nat_route_generator(
                    description,
                    label_dict),
                name="NAT %s" % letter,
                description=description,
                is_mine=self.is_my_track(letter),
            )

    @property
    def infos(self):
        """
        Dictionnary of common OFP data:
        - flight (AF009)
        - departure (KJFK)
        - destination (LFPG)
        - datetime (a python datetime for scheduled departure block time)
        - date (OFP text date 25Apr2016)
        - datetime2 (a python datetime for scheduled arrival block time)
        - ofp (OFP number 9/0/1)
        :return: dict
        """
        if self._infos is None:
            pattern = r'(?P<flight>AF.+)' \
                      r'(?P<departure>\S{4})/' \
                      r'(?P<destination>\S{4})\s+' \
                      r'(?P<datetime>\S+/\S{4})z.*OFP\s+' \
                      r'(?P<ofp>\S+)Main'
            m = re.search(pattern, self.text)
            if m:
                self._infos = m.groupdict()
                self._infos['flight'] = self._infos['flight'].replace(' ', '')

                s = self._infos['datetime']
                self._infos['date'] = s[:-5]
                date_text = "{0}{1:0>2}{2}".format(
                    s[0:2],
                    MONTHS.index(s[2:5]) + 1,
                    s[5:]
                )
                date_object = datetime.strptime(date_text, '%d%m%Y/%H%M'
                                                ).replace(tzinfo=utc)
                self._infos['datetime'] = date_object
                fpl_raw_text = self.raw_fpl_text()
                pattern = r'-%s' % self._infos['destination'] + r'(\d{4})\s'
                m = re.search(pattern, fpl_raw_text)
                if m:
                    self._infos['duration'] = time(
                        int(m.group(1)[:2]), int(m.group(1)[2:]), tzinfo=utc)
                else:
                    print('duration not found in opt, please report !')
                    print('duration set arbitray to 1 hour')
                    self._infos['duration'] = time(1, 0, tzinfo=utc)

                pattern = r'-%s' % self._infos['destination'] + r'.+\s(\S{4})-'
                m = re.search(pattern, fpl_raw_text)
                self._infos['alternate'] = ''
                if m:
                    self._infos['alternate'] = m.group(1)

                pattern = r'RALT/((?:\S{4} )+)'
                m = re.search(pattern, fpl_raw_text)
                self._infos['ralts'] = []
                if m:
                    self._infos['ralts'] = m.group(1).split()

        return self._infos

    def raw_fpl_text(self):
        """
        Extract the FPL text part of the OFP
        """
        if self._raw_fpl is None:
            tag = 'ATC FLIGHT PLAN'
            try:
                self._raw_fpl = self.get_between(tag, 'TRACKSNAT')
            except LookupError as e:
                self.log_error("%s not found" % tag)
                self._raw_fpl = e
        if isinstance(self._raw_fpl, Exception):
            raise LookupError
        return self._raw_fpl

    @property
    def fpl(self):
        """
        FPL found in OFP
        :return: list
        """
        try:
            text = self.raw_fpl_text()
        except LookupError:
            return []
        try:
            text = self.extract(
                text,
                '-%s' % self.infos['departure'],
                '-%s' % self.infos['destination'],
                end_is_optional=False)
        except (LookupError, EOFError, TypeError):
            self.log_error("incomplete Flight Plan")
            return []
        text = text[text.index(' ') + 1:]
        return ([self.infos['departure']] +
                [s.strip() for s in text.split(' ')] +
                [self.infos['destination']])

    @property
    def fpl_route(self):
        """
        FPL route found in OFP (fpl without any speed/FL informations)
        :return: list
        """
        if self._fpl_route is None:
            self._fpl_route = \
                [p.split('/', 1)[0] if '/' in p else p for p in self.fpl]
        return self._fpl_route

    @property
    def lido_route(self):
        """
        A route suitable for lido's app mPilot
        SID/STAR/NAT are represented by geographic points
        :return: list
        """
        points = []  # backup if no fpl
        raw_points = []
        for p in self.route:
            raw_points.append(p.dm)
            if re.search(r'\d+', p.name) or not p.name:
                points.append(p.dm)
            else:
                points.append(p.name)

        lido_route = []
        try:
            departure, inner_fpl_route, destination = (
                self.fpl_route[0], self.fpl_route[1:-1], self.fpl_route[-1])
        except IndexError:
            return points
        # replace points by raw_points before first common waypoint
        for i, p in enumerate(inner_fpl_route):
            if p in points:
                offset = points.index(p)
                lido_route = raw_points[1:offset] + inner_fpl_route[i:]
                break

        # replace points after last common waypoint by raw_points
        for i, p in enumerate(reversed(lido_route)):
            if p in points:
                offset = points[::-1].index(p)
                if i > 0:
                    lido_route = lido_route[0:-i]
                lido_route += raw_points[-offset:-1]
                break

        # build a list of tracks including entry/exit points
        # and replace known tracks (NATA, NATB...) by track_points
        try:
            tracks = self.tracks_iterator()
        except (LookupError, IndexError):
            tracks = []

        # noinspection PyShadowingNames
        def recursive_nat_replace(route, needle, track_points):
            """
            When there is a FL or Speed change, we may have multiple
            "NATW" in the FPL, so change them all.
            :param route: list of waypoint
            :param needle: unicode
            :param track_points: list of track waypoint
            :return: False or list
            """
            route = list(route)  # copy
            match = False
            while True:
                try:
                    offset = route.index(needle)
                except ValueError:
                    return match
                try:
                    route[offset:offset + 1] = \
                        track_points[track_points.index(
                            route[offset - 1]) + 1:track_points.index(
                            route[offset + 1])]
                except IndexError:
                    pass  # leave as is
                match = route

        for track in tracks:
            letter, text = track
            text = text.split('LVLS', 1)[0].strip()
            track_points = [p for p in text.split(' ') if p]
            m = recursive_nat_replace(
                lido_route, self.fpl_track_label(letter), track_points)
            if m:
                lido_route = m
                break

        # replace NAR by intermediate points if any
        # Should be correctly handheld by mPilot, but just in case...
        # for i, p in enumerate(lido_route):
        #     if re.match(r'^N\d+A$', p.strip()):
        #         try:
        #             before = points.index(lido_route[i - 1])
        #             after = (len(points) -
        #                      points[::-1].index(lido_route[i + 1]))
        #             lido_route[i:i + 1] = points[before + 1:after - 1]
        #         except (ValueError, IndexError):
        #             continue

        # adds back departure and destination
        lido_route = [departure] + lido_route + [destination]
        # adds alternate and etops
        if self.infos['alternate']:
            lido_route += [self.infos['alternate']]
        if self.infos['ralts']:
            lido_route += self.infos['ralts']
        return lido_route
