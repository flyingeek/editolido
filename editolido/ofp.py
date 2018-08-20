# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import base64
import itertools
import re
from datetime import datetime, timedelta, tzinfo, time

from editolido.fishpoint import get_missing_fishpoints
from editolido.route import Route, Track
from editolido.geopoint import GeoPoint, dm_normalizer, arinc_normalizer

try:
    zip23 = itertools.izip
    PY2 = True
except AttributeError:
    zip23 = zip
    PY2 = False

try:
    zip_longest23 = itertools.izip_longest
except AttributeError:
    # noinspection PyUnresolvedReferences
    zip_longest23 = itertools.zip_longest

MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
          'Nov', 'Dec')

ZERO = timedelta(0)


# A UTC class.
class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        if PY2:
            return b"UTC"
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()


class OFP(object):
    def __init__(self, text='', pdf=None, progressbar=None):
        self.workflow_version = '1.7.7'
        if pdf:
            self.workflow_version = 'pypdf2'
            with open(pdf, 'rb') as pdf_io:
                from editolido.PyPDF2 import PdfFileReader
                reader = PdfFileReader(pdf_io)
                self.text = ''
                number_of_pages = reader.numPages
                if progressbar:
                    progressbar.set_total(number_of_pages)
                for page in range(number_of_pages):
                    page_text = reader.getPage(page).extractText()
                    if progressbar:
                        progressbar.print_progress_bar(page + 1)
                    if 'Long copy #1' in page_text:
                        self.text += page_text
                    elif self.text:
                        if progressbar:
                            progressbar.print_progress_bar(number_of_pages)
                        break
        elif text and text.startswith('JVBERi0xLj'):
            # PyPDF2 conversion of base64 encoded pdf file
            self.workflow_version = 'pypdf2'
            from io import BytesIO
            from editolido.PyPDF2 import PdfFileReader
            pdf_io = BytesIO()
            try:
                pdf_io.write(base64.b64decode(text))
            except TypeError:
                self.log_error('Invalid base64 file')
                raise KeyboardInterrupt
            reader = PdfFileReader(pdf_io)
            self.text = ''
            for page in range(reader.numPages):
                page_text = reader.getPage(page).extractText()
                if 'Long copy #1' in page_text:
                    self.text += page_text
                elif self.text:
                    break
        else:
            self.text = text
            if not self.text or (' ' == self.text[0] and '\n' in self.text[0:3]):
                self.workflow_version = '1.7.8'
            elif self.text.startswith('FLIGHT SUMMARYOFP'):
                self.workflow_version = 'pypdf2'
        self._infos = None
        self._fpl_route = None
        self._route = None
        self._raw_fpl = None
        self._raw_fs = None

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
        # noinspection PyArgumentList
        return tpl.format(**self.infos)

    @staticmethod
    def wpt_coordinates_generator(text, destination=None):
        if destination:  # fix for Workflow 1.7.8
            # add missing spaces
            text = re.sub(r'\n([NS]\d{4}\.\d)([EW]\d{5}\.\d)', '        \g<1>\g<2>', text)

        for m in re.finditer(r'(\S+|\s+)\s+([NS]\d{4}\.\d)([EW]\d{5}\.\d)',
                             text):
            name = m.group(1).strip()
            yield GeoPoint(
                (m.group(2), m.group(3)),
                name=name, normalizer=dm_normalizer
            )
            if destination and name == destination: # fix for Workflow 1.7.8
                break

    def wpt_coordinates(self, start="WPT COORDINATES", end='----'):
        """
        Return a generator of the ofp's wpt_coordinates
        """
        try:
            if self.workflow_version == '1.7.8':
                s = self.text
            else:
                s = self.get_between(start, end)
        except LookupError:
            self.log_error("%s not found" % start)
            raise KeyboardInterrupt
        if self.workflow_version == '1.7.8':
            destination = self.infos['destination']
            wpts = list(self.wpt_coordinates_generator(s, destination=destination))
            # Now we attempt to reorder points in case the pdf to text parser of workflow 1.7.8 mixed up
            # global direction of the flight

            def sign(a):
                return (a > 0) - (a < 0)

            direction = sign(wpts[0].longitude - wpts[-1].longitude)
            # find blocks of two or more unnamed geopoints
            # those blocks might be in the wrong order so fix them
            blocks = []
            start = end = 0
            longitude_pointer = wpts[0].longitude
            # VSM   N3657.8W02510.0        N3000.0W03000.0
            # N2000.0W03500.0  XIBOT N1815.3W03526.8
            # N4200.0W02000.0
            # N2500.0W03300.0
            # N1700.0W03600.0
            # GOGSO N1140.0W03642.0
            #
            # becomes
            # N4200.0W02000.0
            # VSM   N3657.8W02510.0
            # N3000.0W03000.0
            # N2500.0W03300.0
            # N2000.0W03500.0
            # XIBOT N1815.3W03526.8
            # N1700.0W03600.0
            # GOGSO N1140.0W03642.0
            for i,geopoint in enumerate(wpts):
                name = geopoint.name
                if start == 0 and not name:
                    # identify point without name
                    start = end = i
                    if sign(longitude_pointer - geopoint.longitude) == direction:
                        # general case mark start of unnamed waypoints block
                        pass
                    elif blocks:
                        # covers XIBOT beetween W035 and W020
                        # a named point was misplaced beetween 2 blocks of unamed points
                        # so we set the start to the start of previous block
                        start = blocks.pop()[0]

                    # ugly but as a correct text conversion output should be on three columns
                    # we make sure to go back for at least two values
                    if start > 3:
                        start = start - 2  # covers VSM
                elif start > 0 and end == i-1 and not name:
                    # increase end pointer for unnamed waypoints
                    end = i
                elif start > 0 and end == i - 1 and name:
                    # first named point longitude after unnamed block becomes reference
                    longitude_pointer = geopoint.longitude
                    if start != i-1:
                        blocks.append((start, end))
                    start = end = 0
            for block in blocks:
                reordered_wpts = sorted(wpts[block[0]:block[1]], key=lambda g: g.longitude, reverse=direction > 0)
                wpts = wpts[0:block[0]] + reordered_wpts + wpts[block[1]:]
        else:
            wpts = self.wpt_coordinates_generator(s)
        return wpts

    @property
    def route(self):
        """
        Return a Route of the wpt_coordinates
        """
        return self._route or Route(self.wpt_coordinates())

    def wpt_coordinates_alternate(self, start='WPT COORDINATES',
                                  end='ATC FLIGHT PLAN'):
        """
        Return a generator of the ofp's wpt_coordinates for alternate
        """
        try:
            if self.workflow_version == '1.7.8':
                s = self.text
            else:
                s = self.get_between(start, end,
                                     end_is_optional=False if end else True)
        except LookupError:
            self.log_error("%s not found" % start)
        except EOFError:
            self.log_error('%s not found' % end)
        else:
            try:
                if self.workflow_version == '1.7.8':
                    context_marker = '%s ' % self.infos['destination']
                    s = s.split('----\n%s' % context_marker, 1)[1]
                    s = context_marker + s
                else:
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
        if self.workflow_version == '1.7.7' or self.workflow_version == 'pypdf2':
            if self.workflow_version == 'pypdf2':
                s = self.get_between('ATC FLIGHT PLAN', 'NOTES:')
            else:
                s = self.get_between('TRACKSNAT', 'NOTES:')
            if 'REMARKS:' in s:
                s = s.split('REMARKS:', 1)[0]  # now REMARKS: instead of NOTES:
                s = s.split('Generated at')[0]
            if ' LVLS ' in s:
                # old mode, split at track letter, discard first part.
                it = iter(re.split(r'(?:\s|[^A-Z\d])([A-Z])\s{3}', s)[1:])
                return zip23(it, it)
            else:
                def updated_mar2016_generator():
                    # Letter is lost in the middle
                    # track route starts with something like ELSIR 50
                    l = [m.start() for m in re.finditer('[A-Z]{5} \d\d', s)]
                    for start, end in zip_longest23(l, l[1:]):
                        t = s[start:end]
                        # letter is here
                        parts = re.split('([A-Z])LVLS', t)
                        # adds some missing spaces
                        parts[2] = parts[2].replace(
                            'LVLS', ' LVLS').replace('NIL', 'NIL ')
                        yield parts[1], "%s LVLS%s" % (parts[0], parts[2])
                return updated_mar2016_generator()
        else:
            s = self.get_between('TRACKS\n NAT', 'NOTES:')
            track_letters = []
            for line in s.split('\n'):
                regex = r'^\s?\S$'
                m = re.match(regex, line)
                if m:
                    track_letters.append(line.strip())
            s = self.get_between('WPT COORDINATES', 'TRACKS\n NAT')
            s = self.extract(s, '(Long copy #1)', None)
            s = s.replace(self.raw_fpl_text(), '')  # avoid false match in fpl part
            regex = r'^\S{5,9} \S\S\S.+'
            tracks = [t.replace('\n', '  ') for t in s.split('\n ') if re.match(regex, t)]
            if len(track_letters) != len(tracks):
                self.log_error("Error: tracks letters/definitions mismatch, skipping tracks.")
                return []
            return zip23(track_letters, tracks)

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

    def tracks(self, fishfile=None):
        """
        Yield a route for each track found
        Note: track points only include arinc points (no entry or exit point)
        Full track display requires an optionnal csv files containing fish points.
        :return: generator
        """
        try:
            tracks = self.tracks_iterator()
        except (LookupError, IndexError):
            raise StopIteration
        geo_wpt_regex = r'(\d{2,4}[NS]\d{3,5}[EW]|[NESW]\d{4}|\d[NESW]\d{3}[^EW])'
        tracks = list(tracks)
        fish_points = None

        # optionally find entry/exit points
        if fishfile:
            unknown_wpts = []
            for letter, description in tracks:
                track_points = [p.strip() for p in description.split(' ') if p.strip()]
                for label in track_points:
                    if label == 'LVLS':
                        break
                    m = re.match(geo_wpt_regex, label)
                    if not m:
                        unknown_wpts.append(label)
            fish_points = get_missing_fishpoints(unknown_wpts, fishfile=fishfile)

        for letter, description in tracks:
            is_mine = self.is_my_track(letter)
            if is_mine:
                label_dict = {p.name: p for p in self.route if p.name}
            else:
                label_dict = fish_points

            track_points = [p.strip() for p in description.split(' ') if p.strip()]
            track_route = []
            track_is_complete = True
            for label in track_points:
                if label == 'LVLS':
                    break
                m = re.match(geo_wpt_regex, label)
                if m:
                    track_route.append(GeoPoint(label, normalizer=arinc_normalizer, name=label))
                elif label_dict and label in label_dict:
                    track_route.append(GeoPoint(label_dict[label], name=label))
                else:
                    track_is_complete = False
            yield Track(
                track_route,
                name="NAT %s" % letter,
                description=description,
                is_mine=self.is_my_track(letter),
                is_complete=track_is_complete,
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
        - alternates a list of alternate
        - ralts a list of route alternates (ETOPS)
        - taxitime (int departure taxi time in mn)
        :return: dict
        """
        if self._infos is None:
            pattern = r'(?P<flight>AF.+)' \
                      r'(?P<departure>\S{4})/' \
                      r'(?P<destination>\S{4})\s+' \
                      r'(?P<datetime>\S+/\S{4})z.*OFP\s+' \
                      r'(?P<ofp>\S+)Main'
            m = re.search(pattern, self.text)
            if not m:
                pattern = r'(?P<flight>AF\s+\S+\s+)' \
                          r'(?P<departure>\S{4})/' \
                          r'(?P<destination>\S{4})\s+' \
                          r'(?P<datetime>\S+/\S{4})z.*OFP\s+' \
                          r'(?P<ofp>\d+\S{0,8})'
                m = re.search(pattern, self.text, re.DOTALL)
            if m:
                self._infos = m.groupdict()
                self._infos['flight'] = self._infos['flight'].replace(' ', '')
                self._infos['ofp'] = self._infos['ofp'].replace('\xa9', '')
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
                # try with 2 alternates first
                pattern = r'-%s' % self._infos['destination'] + r'.+\s(\S{4})\s(\S{4})[\n\-]'
                m = re.search(pattern, fpl_raw_text)
                self._infos['alternates'] = []
                if m:
                    self._infos['alternates'] = list(m.groups())
                else:
                    # backup with one alternate only
                    pattern = r'-%s' % self._infos['destination'] + r'.+\s(\S{4})[\n\-]'
                    m = re.search(pattern, fpl_raw_text)
                    if m:
                        self._infos['alternates'] = list(m.groups())
                pattern = r'RALT/((?:\S{4}[ \n])+)'
                m = re.search(pattern, fpl_raw_text)
                self._infos['ralts'] = []
                if m:
                    self._infos['ralts'] = m.group(1).split()

                pattern = r'\s(\d{2})(\d{2})\s+TAXI IN'
                m = re.search(pattern, self.raw_flight_summary_text())
                self._infos['taxitime'] = 0
                if m:
                    self._infos['taxitime'] = (
                        int(m.group(1))*60 + int(m.group(2)))
        return self._infos or {}

    def raw_flight_summary_text(self):
        """Extract the optional FLIGHT SUMMARY part of the OFP"""
        if self._raw_fs is None:
            tag = "FLIGHT SUMMARY"
            try:
                self._raw_fs = self.get_between(tag, 'Generated')
            except LookupError:
                pass
        return self._raw_fs or ''

    def raw_fpl_text(self):
        """
        Extract the FPL text part of the OFP
        """
        if self._raw_fpl is None:
            if self.workflow_version == '1.7.8':
                try:
                    self._raw_fpl = self.extract(self.text, '(FPL', ')',
                                                 end_is_optional=False,
                                                 inclusive=True)
                except (LookupError, EOFError) as e:
                    self.log_error("ATC FLIGHT PLAN not found")
                    self._raw_fpl = e
            else:
                tag = 'ATC FLIGHT PLAN'
                try:
                    self._raw_fpl = self.get_between(tag, 'TRACKSNAT')
                except LookupError as e:
                    self.log_error("%s not found" % tag)
                    self._raw_fpl = e
                else:
                    try:
                        self._raw_fpl = self.extract(self._raw_fpl, '(', ')',
                                                     end_is_optional=False,
                                                     inclusive=True)
                    except (LookupError, EOFError) as e:
                        self.log_error("enclosing brackets not found in %s" % tag)
                        self._raw_fpl = e

        if isinstance(self._raw_fpl, Exception):
            raise LookupError
        return self._raw_fpl or ''

    @property
    def fpl(self):
        """
        FPL found in OFP from departure to destination
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
        if self.infos['alternates']:
            lido_route += self.infos['alternates']
        if self.infos['ralts']:
            lido_route += self.infos['ralts']
        return lido_route
