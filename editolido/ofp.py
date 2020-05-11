# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import base64
from datetime import datetime, timedelta, tzinfo, time
from enum import Enum
from io import BytesIO
import itertools
import re

from editolido.pdfminer.converter import TextConverter
from editolido.pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from editolido.pdfminer.pdfpage import PDFPage
from editolido.fishpoint import get_missing_fishpoints
from editolido.route import Route, Track
from editolido.geopoint import GeoPoint, dm_normalizer, arinc_normalizer

try:
    # noinspection PyUnresolvedReferences
    zip23 = itertools.izip
    PY2 = True
except AttributeError:
    zip23 = zip
    PY2 = False

try:
    # noinspection PyUnresolvedReferences
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


def is_base64_pdf(text):
    """
    Check if a text is a base64 encoded pdf
    param: text: unicode
    return: boolean
    """
    if text is None:
        return False
    # noinspection SpellCheckingInspection
    return text.startswith('JVBERi0xLj')


def io_base64_decoder(text):
    """
    BinaryIO base64 decoder
    :param text: unicode
    :raise: TypeError
    :rtype: typing.BinaryIO
    """
    pdf_io = BytesIO()
    pdf_io.write(base64.b64decode(text))
    return pdf_io


def ofp_to_text(fp):
    """
    convert a base64 ofp binary to text
    :param fp: typing.BinaryIO
    :return unicode
    :raises TypeError
    """
    manager = PDFResourceManager(caching=False)
    text = ""
    for page in PDFPage.get_pages(fp, caching=False, check_extractable=False):
        out_fo = BytesIO()
        device = TextConverter(manager, out_fo)
        interpreter = PDFPageInterpreter(manager, device)
        page.rotate = (page.rotate + 0) % 360
        interpreter.process_page(page)
        device.close()
        page_text = out_fo.getvalue().decode(encoding='utf-8')
        out_fo.close()
        if 'Long copy #1' in page_text and 'NEXT AIRCRAFT LEG' not in page_text:
            text += page_text
        elif text:
            break
    return text


class PdfParser(Enum):
    PYPDF2 = 3
    WORKFLOW177 = 4


class OfpType(Enum):
    S4 = 1
    NVP = 2


class OFP(object):
    def __init__(self, text):
        self.workflow_version = PdfParser.PYPDF2
        self.ofp_type = OfpType.S4
        if is_base64_pdf(text):
            try:
                pdf_io = io_base64_decoder(text)
            except TypeError:
                self.log_error('Invalid base64 file')
                raise KeyboardInterrupt
            self.text = ofp_to_text(pdf_io)
            pdf_io.close()
        else:
            # Using text entry (running test or using replay mode)
            self.text = text
            if not self.text.startswith('FLIGHT SUMMARYOFP'):
                # This is also true for NVP/pypdf2 OFP
                # but in that case, next test will handle this.
                self.workflow_version = PdfParser.WORKFLOW177

        if '--FLIGHT SUMMARY--' in self.text:
            self.workflow_version = PdfParser.PYPDF2
            self.ofp_type = OfpType.NVP
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
    def wpt_coordinates_generator(text):
        for m in re.finditer(r'(\S+|\s+)\s+([NS]\d{4}\.\d)([EW]\d{5}\.\d)',
                             text):
            name = m.group(1).strip()
            yield GeoPoint(
                (m.group(2), m.group(3)),
                name=name, normalizer=dm_normalizer
            )

    def wpt_coordinates(self, start="WPT COORDINATES"):
        """
        Return a generator of the ofp wpt_coordinates
        """
        end = '----'
        if self.ofp_type == OfpType.NVP:
            end = '----' + self.infos['destination']
        try:
            s = self.get_between(start, end)
        except LookupError:
            self.log_error("%s not found" % start)
            raise KeyboardInterrupt
        wpts = self.wpt_coordinates_generator(s)
        return wpts

    @property
    def route(self):
        """
        Return a Route of the wpt_coordinates
        """
        return self._route or Route(self.wpt_coordinates())

    def wpt_coordinates_alternate(self, start='WPT COORDINATES', end_is_optional=False):
        """
        Return a generator of the ofp wpt_coordinates for alternate
        end tag is computed, if you need to skip it you can turn end_is_optional to True
        """
        end = 'ATC FLIGHT PLAN'
        if self.ofp_type == OfpType.NVP:
            end = "--WIND INFORMATION--"
        try:
            s = self.get_between(start, end, end_is_optional)
        except LookupError:
            self.log_error("%s not found" % start)
        except EOFError:
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
        if self.workflow_version == PdfParser.WORKFLOW177:
            s = self.get_between('TRACKSNAT', 'NOTES:')
        else:
            s = self.get_between('ATC FLIGHT PLAN', 'NOTES:')
            s = self.extract(s, ')', None)
        if 'REMARKS:' in s:
            s = s.split('REMARKS:', 1)[0]  # now REMARKS: instead of NOTES:
            s = s.split('Generated at')[0]
        if ' LVLS ' in s:
            # old mode, split at track letter, discard first part.
            it = iter(re.split(r'(?:\s|[^A-Z\d])([A-Z])\s{3}', s)[1:])
            return zip23(it, it)
        else:
            # self.workflow_version == PdfParser.WORKFLOW177
            def updated_mar2016_generator():
                # Letter is lost in the middle
                # track route starts with something like ELSIR 50
                markers = [m.start() for m in re.finditer(r'[A-Z]{5} \d\d', s)]
                for start, end in zip_longest23(markers, markers[1:]):
                    t = s[start:end]
                    # letter is here
                    parts = re.split('([A-Z])LVLS', t)
                    # adds some missing spaces
                    parts[2] = parts[2].replace(
                        'LVLS', ' LVLS').replace('NIL', 'NIL ')
                    yield parts[1], "%s LVLS%s" % (parts[0], parts[2])
            return updated_mar2016_generator()

    def is_my_track(self, letter):
        """
        Checks if the designated track is in the fpl
        """
        if not self.fpl_route:
            return False
        return Track.label(letter) in self.fpl_route[1:-1]

    def tracks(self, fishfile=None):
        """
        Yield a route for each track found
        Note: track points only include arinc points (no entry or exit point)
        Full track display requires an optional csv files containing fish points.
        :return: generator
        """
        try:
            tracks = self.tracks_iterator()
        except (LookupError, IndexError):
            return
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
        Dictionary of common OFP data:
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
        :return: Dict[str, Any]
        """
        if self._infos is None:
            self._infos = {}
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
                self._infos.update(m.groupdict())
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
                    print('duration set arbitrary to 1 hour')
                    self._infos['duration'] = time(1, 0, tzinfo=utc)
                # try with 2 alternates first
                pattern = r'-%s' % self._infos['destination'] + r'.+\s(\S{4})\s(\S{4})\s?[\n\-]'
                m = re.search(pattern, fpl_raw_text)
                self._infos['alternates'] = []
                if m:
                    self._infos['alternates'] = list(m.groups())
                else:
                    # backup with one alternate only
                    pattern = r'-%s' % self._infos['destination'] + r'.+\s(\S{4})\s?[\n\-]'
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
        return self._infos

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
                [s.strip() for s in text.split(' ') if not s.startswith('-N')] +
                [self.infos['destination']])

    @property
    def fpl_route(self):
        """
        FPL route found in OFP (fpl without any speed/FL information)
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
            route = route[:]  # copy
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
                lido_route, Track.label(letter), track_points)
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
