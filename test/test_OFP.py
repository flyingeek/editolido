# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import base64
from unittest import TestCase
import mock
import os

from editolido.route import Route
from editolido.ofp import OFP
from editolido.geopoint import GeoPoint, dm_normalizer

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
FISHFILE = os.path.join(DATADIR, 'WPTS_OCA.csv')

# noinspection PyUnresolvedReferences
patch_object = mock.patch.object


def load_ofp(filepath):
    with open(filepath, 'r') as f:
        text = f.read()
    try:
        text = text.decode('utf-8')
    except AttributeError:
        pass
    return OFP(text)


class TestOFP(TestCase):
    def test_pdf_to_text(self):
        from editolido.ofp import is_base64_pdf, pdf_to_text, io_base64_decoder
        with self.assertRaises(TypeError):
            pdf_io = io_base64_decoder("not base64")
            pdf_io.close()
        with open(DATADIR + "/hello_world.pdf", 'rb') as f:
            pdf = f.read()
            text = base64.b64encode(pdf)
        self.assertTrue(is_base64_pdf(text))
        pdf_io = io_base64_decoder(text)
        text = pdf_to_text(pdf_io)
        self.assertTrue(text.startswith("Long copy #1Hello World"))

    def test_get_between(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')
        self.assertEqual('1.7.7', ofp.workflow_version)
        s = ofp.get_between('WPT COORDINATES', '----')
        self.assertEqual(s[:4], 'KJFK')
        self.assertEqual(s[-21:-17], 'LFPG')

        s = ofp.get_between('WPT COORDINATES', '----', inclusive=True)
        self.assertTrue(s.startswith('WPT COORDINATES'))
        self.assertTrue(s.endswith('----'))
        self.assertEqual(s[15:19], 'KJFK')
        self.assertEqual(s[-25:-21], 'LFPG')

        with self.assertRaises(LookupError):
            ofp.get_between('####', '----')

        with self.assertRaises(EOFError):
            ofp.get_between('WPT COORDINATES', '****', end_is_optional=False)

        s = ofp.get_between('WPT COORDINATES', '****')
        self.assertTrue(s.endswith('STANDARD\n'))

        s = ofp.get_between('WPT COORDINATES', '****', inclusive=True)
        self.assertTrue(s.endswith('****'))

        s = ofp.get_between(None, 'KJFK/LFPG')
        self.assertEqual(s, 'retrieved: 27Mar/0429zAF  009  ')

        s = ofp.get_between('USED AS A ', None)
        self.assertEqual(s, 'STANDARD\n')

        s = ofp.get_between(None, None)
        self.assertEqual(s, ofp.text)

    def test_wpt_coordinates(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        points = list(ofp.wpt_coordinates())
        self.assertEqual(len(points), 31)
        self.assertEqual(points[0].name, 'KJFK')
        self.assertEqual(points[-1].name, 'LFPG')
        self.assertEqual(points[5].name, '')
        self.assertEqual(
            points[0],
            GeoPoint('N4038.4W07346.7', normalizer=dm_normalizer))
        self.assertEqual(
            points[-1],
            GeoPoint('N4900.6E00232.9', normalizer=dm_normalizer))
        self.assertEqual(
            points[5],
            GeoPoint('N5100.0W05000.0', normalizer=dm_normalizer))

    def test_wpt_coordinates_alternate(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        points = list(ofp.wpt_coordinates_alternate())
        self.assertEqual(
            points[0],
            GeoPoint('N4900.6E00232.9', normalizer=dm_normalizer))
        self.assertEqual(
            points[1],
            GeoPoint('N4825.8E00213.8', normalizer=dm_normalizer))
        self.assertEqual(
            points[-1],
            GeoPoint('N4843.4E00222.8', normalizer=dm_normalizer))

    def test_wpt_coordinates_alternate_af011_22Mar2016(self):
        ofp = load_ofp(DATADIR + '/AF011_KJFK-LFPG_22Mar2016_02:45z_OFP_8_0_1.txt')

        points = list(ofp.wpt_coordinates_alternate())
        self.assertEqual(
            points[0],
            GeoPoint('N4900.6E00232.9', normalizer=dm_normalizer))
        self.assertEqual(
            points[1],
            GeoPoint('N4825.8E00213.8', normalizer=dm_normalizer))
        self.assertEqual(
            points[-1],
            GeoPoint('N4843.4E00222.8', normalizer=dm_normalizer))

    @patch_object(OFP, 'log_error')
    def test_missing_wpt_coordinates(self, logger):
        ofp = OFP('blabla blabla')
        with self.assertRaises(KeyboardInterrupt):
            list(ofp.wpt_coordinates())
        logger.assert_called_with('WPT COORDINATES not found')

    @patch_object(OFP, 'log_error')
    def test_missing_wpt_coordinates_alternate(self, logger):
        ofp = OFP('blabla blabla')
        self.assertFalse(list(ofp.wpt_coordinates_alternate()))
        logger.assert_called_with('WPT COORDINATES not found')

    def test_missing_tracks(self):
        ofp = OFP('blabla blabla')
        self.assertEqual(list(ofp.tracks()), [])
        with self.assertRaises(LookupError):
            ofp.tracks_iterator()

    def test_tracks(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        tracks = list(ofp.tracks())
        self.assertEqual(len(tracks), 9)
        self.assertEqual(
            tracks[0],
            Route([
                GeoPoint((56.000000, -20.000000)),
                GeoPoint((57.000000, -30.000000)),
                GeoPoint((58.000000, -40.000000)),
                GeoPoint((58.000000, -50.000000))])
        )
        self.assertEqual(
            tracks[-1],
            Route([
                GeoPoint((42.000000, -40.000000)),
                GeoPoint((38.000000, -50.000000)),
                GeoPoint((33.000000, -60.000000))])
        )
        for p in tracks[0]:
            self.assertTrue(p.name)
        self.assertTrue(tracks[0].name.endswith('A'))
        self.assertTrue(tracks[-1].name.endswith('J'))

    def test_tracks_with_fishpoints(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        tracks = list(
            ofp.tracks(fishfile=FISHFILE))
        self.assertEqual(len(tracks), 9)
        self.assertEqual(
            tracks[0],
            Route([
                GeoPoint((55.000000, -15.000000), name="RESNO"),
                GeoPoint((56.000000, -20.000000)),
                GeoPoint((57.000000, -30.000000)),
                GeoPoint((58.000000, -40.000000)),
                GeoPoint((58.000000, -50.000000)),
                GeoPoint((56.700000, -57.000000), name="CUDDY")])
        )
        self.assertEqual(
            tracks[-1],
            Route([
                GeoPoint((42.000000, -40.000000)),
                GeoPoint((38.000000, -50.000000)),
                GeoPoint((33.000000, -60.000000)),
                GeoPoint((32.670000, -61.190000), name="NUMBR")])
        )
        for p in tracks[0]:
            self.assertTrue(p.name)
        self.assertTrue(tracks[0].name.endswith('A'))
        self.assertTrue(tracks[-1].name.endswith('J'))

    def tests_tracks_rlat_new_format(self):
        ofp = load_ofp(DATADIR + '/AF009_KJFK-LFPG_18Mar2016_04:55z_OFP_12_0_1.txt')

        tracks = list(ofp.tracks())
        self.assertEqual(len(tracks), 7)
        self.assertEqual(
            tracks[0],
            Route([
                GeoPoint((50, -50)),
                GeoPoint((51, -40)),
                GeoPoint((52, -30)),
                GeoPoint((53, -20))])
        )
        self.assertFalse(tracks[0].is_complete)
        self.assertEqual(
            tracks[2],
            Route([
                GeoPoint((48.5, -50)),
                GeoPoint((49.5, -40)),
                GeoPoint((50.5, -30)),
                GeoPoint((51.5, -20))])
        )
        self.assertFalse(tracks[2].is_complete)
        self.assertTrue(tracks[0].name.endswith('T'))
        self.assertTrue(tracks[-1].name.endswith('Z'))

    def tests_tracks_rlat_new_format_with_fishpoints(self):
        ofp = load_ofp(DATADIR + '/AF009_KJFK-LFPG_18Mar2016_04:55z_OFP_12_0_1.txt')

        tracks = list(
            ofp.tracks(fishfile=FISHFILE))
        self.assertEqual(len(tracks), 7)
        self.assertEqual(
            tracks[0],
            Route([
                GeoPoint((49.500000, -52.000000), name="ELSIR"),
                GeoPoint((50, -50)),
                GeoPoint((51, -40)),
                GeoPoint((52, -30)),
                GeoPoint((53, -20)),
                GeoPoint((53.000000, -15.000000), name="MALOT"),
                GeoPoint((53.000000, -14.000000), name="GISTI")])
        )
        self.assertTrue(tracks[0].is_complete)
        self.assertEqual(
            tracks[2],
            Route([
                GeoPoint((48.000000, -52.000000), name="MUSAK"),
                GeoPoint((48.5, -50)),
                GeoPoint((49.5, -40)),
                GeoPoint((50.5, -30)),
                GeoPoint((51.5, -20)),
                GeoPoint((51.5, -15.000000), name="ADARA"),
                GeoPoint((51.5, -14.000000), name="LEKVA")])
        )
        self.assertTrue(tracks[2].is_complete)
        self.assertTrue(tracks[0].name.endswith('T'))
        self.assertTrue(tracks[-1].name.endswith('Z'))

    def tests_tracks_with_page_break(self):
        ofp = load_ofp(DATADIR + '/AF011_KJFK-LFPG_22Mar2016_02:45z_OFP_8_0_1.txt')

        tracks = list(ofp.tracks())
        self.assertEqual(len(tracks), 8)
        self.assertEqual(
            tracks[0],
            Route([
                GeoPoint((51, -50)),
                GeoPoint((52, -40)),
                GeoPoint((54, -30)),
                GeoPoint((56, -20))])
        )
        self.assertFalse(tracks[0].is_complete)
        self.assertEqual(tracks[6].name, 'NAT Y')
        self.assertEqual(
            tracks[6],  # Y
            Route([
                GeoPoint((40, -60)),
                GeoPoint((41, -50)),
                GeoPoint((41, -40))])
        )
        self.assertFalse(tracks[6].is_complete)
        self.assertEqual(tracks[4].name, 'NAT W')  # FPL Track
        self.assertEqual(
            tracks[4],  # W
            Route([
                GeoPoint((46.500000, -52.000000), name="PORTI"),
                GeoPoint((47, -50)),
                GeoPoint((48, -40)),
                GeoPoint((50, -30)),
                GeoPoint((52, -20)),
                GeoPoint((52.000000, -15.000000), name="LIMRI"),
                GeoPoint((52.000000, -14.000000), name="XETBO"),
            ])
        )
        self.assertTrue(tracks[4].is_complete)
        self.assertTrue(tracks[0].name.endswith('S'))
        self.assertTrue(tracks[-1].name.endswith('Z'))

    def tests_tracks_with_page_break_and_fishpoints(self):
        ofp = load_ofp(DATADIR + '/AF011_KJFK-LFPG_22Mar2016_02:45z_OFP_8_0_1.txt')

        tracks = list(
            ofp.tracks(fishfile=FISHFILE))
        self.assertEqual(len(tracks), 8)
        self.assertEqual(
            tracks[0],
            Route([
                GeoPoint((50.500000, -52.000000), name="ALLRY"),
                GeoPoint((51, -50)),
                GeoPoint((52, -40)),
                GeoPoint((54, -30)),
                GeoPoint((56, -20)),
                GeoPoint((56.000000, -15.000000), name="PIKIL"),
                GeoPoint((56.000000, -14.000000), name="SOVED")])
        )
        self.assertTrue(tracks[0].is_complete)
        self.assertEqual(tracks[6].name, 'NAT Y')
        self.assertEqual(
            tracks[6],  # Y
            Route([
                GeoPoint((40.120000, -67.000000), name="JOBOC"),
                GeoPoint((40, -60)),
                GeoPoint((41, -50)),
                GeoPoint((41, -40))])
        )
        self.assertTrue(tracks[6].is_complete)
        self.assertEqual(tracks[4].name, 'NAT W')  # FPL Track
        self.assertEqual(
            tracks[4],  # W
            Route([
                GeoPoint((46.500000, -52.000000), name="PORTI"),
                GeoPoint((47, -50)),
                GeoPoint((48, -40)),
                GeoPoint((50, -30)),
                GeoPoint((52, -20)),
                GeoPoint((52.000000, -15.000000), name="LIMRI"),
                GeoPoint((52.000000, -14.000000), name="XETBO"),
            ])
        )
        self.assertTrue(tracks[4].is_complete)
        self.assertTrue(tracks[0].name.endswith('S'))
        self.assertTrue(tracks[-1].name.endswith('Z'))

    def test_infos(self):
        from datetime import datetime, timedelta, time
        from editolido.ofp import utc
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        expected = {
            'flight': 'AF009',
            'destination': 'LFPG',
            'departure': 'KJFK',
            'datetime': datetime(2015, 3, 27, 5, 45, tzinfo=utc),
            'duration': time(5, 54, tzinfo=utc),
            'ofp': '9/0/1',
            'date': '27Mar2015',
            'alternates': ['LFPO'],
            'ralts': ['CYQX', 'EINN'],
            'taxitime': 0,
        }
        self.assertDictEqual(ofp.infos, expected)
        dt = ofp.infos['datetime']
        self.assertEqual(dt.tzname(), 'UTC')
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_infos_af011_22Mar2016(self):
        from datetime import datetime, timedelta, time
        from editolido.ofp import utc
        ofp = load_ofp(DATADIR + '/AF011_KJFK-LFPG_22Mar2016_02:45z_OFP_8_0_1.txt')

        expected = {
            'flight': 'AF011',
            'destination': 'LFPG',
            'departure': 'KJFK',
            'datetime': datetime(2016, 3, 22, 2, 45, tzinfo=utc),
            'duration': time(6, 18, tzinfo=utc),
            'ofp': '8/0/1',
            'date': '22Mar2016',
            'ralts': ['LPLA', 'EINN'],
            'alternates': ['LFPO'],
            'taxitime': 0,
        }
        self.assertDictEqual(ofp.infos, expected)
        dt = ofp.infos['datetime']
        self.assertEqual(dt.tzname(), 'UTC')
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_infos_af1753_28Mar2016(self):
        from datetime import datetime, timedelta, time
        from editolido.ofp import utc
        ofp = load_ofp(DATADIR + '/AF1753_UKBB-LFPG_28Mar2016_12:15z_OFP13.txt')

        expected = {
            'flight': 'AF1753',
            'departure': 'UKBB',
            'destination': 'LFPG',
            'datetime': datetime(2016, 3, 28, 12, 15, tzinfo=utc),
            'duration': time(2, 57, tzinfo=utc),
            'ofp': '13',
            'date': '28Mar2016',
            'alternates': ['LFOB'],
            'ralts': [],
            'taxitime': 0,
        }
        self.assertDictEqual(ofp.infos, expected)
        dt = ofp.infos['datetime']
        self.assertEqual(dt.tzname(), 'UTC')
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_infos_af6744_11Jul2017(self):
        from datetime import datetime, timedelta, time
        from editolido.ofp import utc
        ofp = load_ofp(DATADIR + '/AF6744_GABS-LFPG_11Jul2017_08:25z_OFP_7_0_1.txt')

        # In this case also flight time of OFP is 05h06, in fpl it is written 04h56
        expected = {
            'flight': 'AF6744',
            'departure': 'GABS',
            'destination': 'LFPG',
            'datetime': datetime(2017, 7, 11, 8, 25, tzinfo=utc),
            'duration': time(4, 56, tzinfo=utc),
            'ofp': '7/0/1',
            'date': '11Jul2017',
            'alternates': ['LFQQ', 'LFPO'],
            'ralts': ['GABS'],
            'taxitime': 15,
        }
        self.assertDictEqual(ofp.infos, expected)
        dt = ofp.infos['datetime']
        self.assertEqual(dt.tzname(), 'UTC')
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_description(self):
        ofp =load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        self.assertEqual(
            ofp.description,
            "AF009 KJFK-LFPG 27Mar2015 05:45z OFP 9/0/1"
        )

    @patch_object(OFP, 'log_error')
    def test_fpl_lookup_error(self, logger):
        ofp = OFP('')
        self.assertEqual(ofp.fpl, [])
        logger.assert_called_with('ATC FLIGHT PLAN not found')
        logger.reset_mock()

        ofp = OFP('ATC FLIGHT PLANblabla')
        self.assertEqual(ofp.fpl, [])
        logger.assert_called_with(
            'enclosing brackets not found in ATC FLIGHT PLAN')
        logger.reset_mock()

        ofp = OFP('ATC FLIGHT PLAN(blabla)')
        self.assertEqual(ofp.fpl, [])
        logger.assert_called_with('incomplete Flight Plan')
        logger.reset_mock()

    def test_fpl(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        self.assertEqual(
            ' '.join(ofp.fpl),
            "KJFK DCT GREKI DCT MARTN DCT EBONY/M084F350 N247A ALLRY/M084F370 "
            "DCT 51N050W 53N040W 55N030W 55N020W DCT RESNO DCT "
            "NETKI/N0479F350 DCT BAKUR/N0463F350 UN546 STU UP2 "
            "NIGIT UL18 SFD/N0414F250 UM605 BIBAX BIBAX7W LFPG"
        )

    def test_raw_fpl_text(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        self.assertEqual(
            ofp.raw_fpl_text(),
            '(FPL-AFR009-IS-B77W/H-SDE2E3FGHIJ3J5J6M1M2RWXY/LB1D1'
            '-KJFK0545-N0476F350 DCT GREKI DCT MARTN DCT EBONY/M084F350 N247A '
            'ALLRY/M084F370 DCT 51N050W 53N040W 55N030W 55N020W DCT RESNO DCT '
            'NETKI/N0479F350 DCT BAKUR/N0463F350 UN546 STU UP2 NIGIT UL18 '
            'SFD/N0414F250 UM605 BIBAX BIBAX7W-LFPG0554 LFPO-PBN/A1B1C1D1L1S1 '
            'DOF/150327 REG/FGSQB EET/KZBW0004 CZQM0047 CZQX0119 ALLRY0156 '
            '51N050W0205 53N040W0247 EGGX0328 55N020W0403 RESNO0420 NETKI0423 '
            'EISN0432 EGTT0457 LFFF0526 SEL/HPLM OPR/AFR RALT/CYQX EINN '
            'RVR/100 RMK/ACAS)',
        )

    def test_fpl_route(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        self.assertEqual(
            ' '.join(ofp.fpl_route),
            "KJFK DCT GREKI DCT MARTN DCT EBONY N247A ALLRY "
            "DCT 51N050W 53N040W 55N030W 55N020W DCT RESNO DCT "
            "NETKI DCT BAKUR UN546 STU UP2 "
            "NIGIT UL18 SFD UM605 BIBAX BIBAX7W LFPG"
        )

    def test_fpl_route_af011_22Mar2016(self):
        ofp = load_ofp(DATADIR + '/AF011_KJFK-LFPG_22Mar2016_02:45z_OFP_8_0_1.txt')

        self.assertEqual(
            ' '.join(ofp.fpl_route),
            "KJFK DCT BETTE DCT ACK DCT KANNI N139A PORTI NATW "
            "LIMRI NATW XETBO DCT UNLID DCT LULOX UN84 NAKID UM25 UVSUV "
            "UM25 INGOR UM25 LUKIP LUKIP7E LFPG"
        )

    def test_lido_route(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')
        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.lido_route),
            'KJFK GREKI DCT MARTN DCT EBONY N247A ALLRY DCT 51N050W '
            '53N040W 55N030W 55N020W DCT RESNO DCT NETKI DCT BAKUR UN546 '
            'STU UP2 NIGIT UL18 SFD UM605 BIBAX N4918.0E00134.2 '
            'N4917.5E00145.4 N4915.7E00223.3 N4915.3E00230.9 '
            'N4913.9E00242.9 LFPG LFPO CYQX EINN'
        )

    def test_lido_route_af011_22Mar2016(self):
        ofp = load_ofp(DATADIR + '/AF011_KJFK-LFPG_22Mar2016_02:45z_OFP_8_0_1.txt')

        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.lido_route),
            "KJFK N4036.7W07353.7 BETTE DCT ACK DCT KANNI N139A PORTI "
            "47N050W 48N040W 50N030W 52N020W "
            "LIMRI XETBO DCT UNLID DCT LULOX UN84 NAKID UM25 UVSUV "
            "UM25 INGOR UM25 LUKIP N4918.0E00134.2 N4917.5E00145.4 "
            "N4910.2E00150.4 LFPG LFPO LPLA EINN"
        )

    def test_lido_route_no_tracksnat(self):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        ofp.text = ofp.text.replace('TRACKSNAT', 'TRACKSNA*')
        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.lido_route),
            'KJFK GREKI DCT MARTN DCT EBONY N247A ALLRY DCT 51N050W '
            '53N040W 55N030W 55N020W DCT RESNO DCT NETKI DCT BAKUR UN546 '
            'STU UP2 NIGIT UL18 SFD UM605 BIBAX N4918.0E00134.2 '
            'N4917.5E00145.4 N4915.7E00223.3 N4915.3E00230.9 '
            'N4913.9E00242.9 LFPG LFPO CYQX EINN'
        )

    @patch_object(OFP, 'log_error')
    def test_lido_route_no_fpl(self, logger):
        ofp = load_ofp(DATADIR + '/KJFK-LFPG 27Mar2015 05:45z OFP.txt')

        ofp.text = ofp.text.replace('ATC FLIGHT PLAN', 'ATC*FLIGHT*PLAN')
        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.lido_route),
            'KJFK GREKI MARTN EBONY ALLRY N5100.0W05000.0 N5300.0W04000.0 '
            'N5500.0W03000.0 N5500.0W02000.0 RESNO NETKI BAKUR STU NUMPO '
            'OKESI BEDEK NIGIT VAPID MID SFD WAFFU HARDY XIDIL PETAX BIBAX '
            'KOLIV MOPAR N4915.7E00223.3 CRL N4913.9E00242.9 LFPG'
        )
        logger.assert_called_with('ATC FLIGHT PLAN not found')

    def test_lido_route_with_naty(self):
        ofp = load_ofp(DATADIR + '/AF007_KJFK-LFPG_13Mar2016_00:15z_OFP_6_0_1.txt')

        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.lido_route),
            'KJFK HAPIE DCT YAHOO DCT DOVEY 42N060W 43N050W 46N040W 49N030W '
            '49N020W BEDRA NERTU DCT TAKAS UN490 MOSIS UN491 BETUV UY111 '
            'JSY UY111 INGOR UM25 LUKIP N4918.0E00134.2 '
            'N4917.5E00145.4 N4910.2E00150.4 LFPG LFPO CYYT EINN'
        )

    @patch_object(OFP, 'log_error')
    def test_lido_route_with_naty_no_fpl(self, logger):
        ofp = load_ofp(DATADIR + '/AF007_KJFK-LFPG_13Mar2016_00:15z_OFP_6_0_1.txt')

        ofp.text = ofp.text.replace('ATC FLIGHT PLAN', 'ATC*FLIGHT*PLAN')
        self.assertEqual(
            ' '.join(ofp.lido_route),
            'KJFK HAPIE YAHOO DOVEY N4200.0W06000.0 N4300.0W05000.0 '
            'N4600.0W04000.0 N4900.0W03000.0 N4900.0W02000.0 BEDRA NERTU '
            'TAKAS ALUTA MOSIS DEKOR NERLA RUSIB BETUV JSY INGOR LUKIP '
            'KOLIV MOPAR N4910.2E00150.4 LFPG'
        )
        logger.assert_called_with('ATC FLIGHT PLAN not found')

    def test_lido_route_with_naty_no_tracksnat(self):
        ofp = load_ofp(DATADIR + '/AF007_KJFK-LFPG_13Mar2016_00:15z_OFP_6_0_1.txt')

        ofp.text = ofp.text.replace('TRACKSNAT', 'TRACKSNA*')
        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.lido_route),
            'KJFK HAPIE DCT YAHOO DCT DOVEY NATY NERTU DCT TAKAS UN490 '
            'MOSIS UN491 BETUV UY111 '
            'JSY UY111 INGOR UM25 LUKIP N4918.0E00134.2 '
            'N4917.5E00145.4 N4910.2E00150.4 LFPG LFPO CYYT EINN'
        )

    def test_lido_route_ofp374_22Jul2016(self):
        """
        Ensure all waypoints and in the good order
        """
        ofp = load_ofp(DATADIR + '/AF374_LFPG-CYVR_22Jul2016_08:45z_OFP_8_0_1.txt')

        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.lido_route),
            'LFPG N4900.9E00225.0 N4907.1E00219.2 ATREX UT225 VESAN UL613 '
            'SOVAT UL613 TLA UN601 STN UN610 BARKU UN610 RATSU DCT '
            '66N020W 68N030W 69N040W 70N050W 70N060W DCT ADSAM DCT 69N080W '
            '6730N09000W DCT ALKAP DCT 60N110W 55N117W DCT BOOTH '
            'N4928.2W12210.4 N4924.1W12220.9 N4916.8W12239.1 N4914.4W12254.1 '
            'N4915.2W12300.4 N4916.2W12307.9 N4917.6W12319.9 N4919.1W12331.9 '
            'N4914.7W12333.1 CYVR KSEA BIKF CYYR CYZF'
        )

    def test_wpt_ofp374_22Jul2016(self):
        """
        Ensure all waypoints and in the good order
        """
        ofp = load_ofp(DATADIR + '/AF374_LFPG-CYVR_22Jul2016_08:45z_OFP_8_0_1.txt')

        self.assertEqual(
            ' '.join([p.dm for p in ofp.route]),
            'N4900.6E00232.9 N4900.9E00225.0 N4907.1E00219.2 '
            'N4947.1E00222.1 N5022.3E00201.6 N5039.4E00138.2 '
            'N5046.8E00128.0 N5103.9E00104.0 N5201.6W00001.3 '
            'N5218.5W00016.2 N5300.6W00054.1 N5325.1W00116.8 '
            'N5344.1W00134.8 N5408.9W00158.8 N5530.0W00321.2 '
            'N5627.8W00418.4 N5641.7W00432.7 N5812.4W00611.0 '
            'N6001.2W00834.1 N6036.3W00924.6 N6100.0W01000.0 '
            'N6600.0W02000.0 N6800.0W03000.0 N6900.0W04000.0 '
            'N7000.0W05000.0 N7000.0W06000.0 N6955.3W06313.2 '
            'N6900.0W08000.0 N6730.0W09000.0 N6227.6W10621.0 '
            'N6000.0W11000.0 N5500.0W11700.0 N4931.3W12202.7 '
            'N4928.2W12210.4 N4924.1W12220.9 N4916.8W12239.1 '
            'N4914.4W12254.1 N4915.2W12300.4 N4916.2W12307.9 '
            'N4917.6W12319.9 N4919.1W12331.9 N4914.7W12333.1 '
            'N4911.7W12311.0'
        )

    def test_lido_route_af1753_28Mar2016(self):
        ofp = load_ofp(DATADIR + '/AF1753_UKBB-LFPG_28Mar2016_12:15z_OFP13.txt')

        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.lido_route),
            'UKBB N5030.6E03051.1 N5032.0E03039.8 N5024.3E03017.3 '
            'KR P27 PEVOT T708 GIDNO T708 DIBED L984 OKG UL984 NOSPA DCT '
            'IDOSA UN857 RAPOR UZ157 VEDUS N4935.8E00404.0 N4928.5E00346.7 '
            'N4927.0E00337.9 N4925.2E00327.1 N4916.5E00319.6 LFPG LFOB'
        )

    def test_fpl_route_af6752_05Feb2017(self):
        ofp = load_ofp(DATADIR + '/AF6752_FMEE-FMMI_05Feb2017_11:50z_OFP_5_0_1.txt')

        self.assertEqual(
            ' '.join(ofp.fpl_route),
            "FMEE UNKIK4C UNKIK UA401 TE TE1Z FMMI"
        )

    def test_lido_route_af6752_05Feb2017(self):
        ofp = load_ofp(DATADIR + '/AF6752_FMEE-FMMI_05Feb2017_11:50z_OFP_5_0_1.txt')

        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.lido_route),
            'FMEE UNKIK UA401 TE S1847.0E04723.6 S1847.6E04727.3 FMMI HTDA'
        )

    def test_tracks_af6752_05Feb2017_empty(self):
        ofp = load_ofp(DATADIR + '/AF6752_FMEE-FMMI_05Feb2017_11:50z_OFP_5_0_1.txt')

        self.maxDiff = None
        self.assertEqual(
            ' '.join(ofp.tracks()),
            ''
        )

    def test_taxitime_af6752_05Feb2017(self):
        ofp = load_ofp(DATADIR + '/AF6752_FMEE-FMMI_05Feb2017_11:50z_OFP_5_0_1.txt')

        self.assertEqual(
            ofp.infos['taxitime'],
            8
        )

    def test_extract_coordinates_from_text(self):
        ofp = load_ofp(DATADIR + '/pdf_coordinates_copied_from_goodreader.txt')

        self.assertEqual(len(list(ofp.wpt_coordinates(start=None))), 80)
        self.assertEqual(
            len(list(ofp.wpt_coordinates_alternate(start=None, end=None))), 9)


class TestOFPForWorkflow178(TestCase):
    def test_infos(self):
        from datetime import datetime, timedelta, time
        from editolido.ofp import utc
        ofp = load_ofp(DATADIR + '/AF651_MMUN-LFPG_08Mar2018_00:30z_OFP_9_0_1_workflow_1_7_8.txt')

        self.assertEqual('1.7.8', ofp.workflow_version)
        expected = {
            'flight': 'AF651',
            'departure': 'MMUN',
            'destination': 'LFPG',
            'datetime': datetime(2018, 3, 8, 0, 30, tzinfo=utc),
            'duration': time(8, 20, tzinfo=utc),
            'ofp': '9/0/1',
            'date': '08Mar2018',
            'alternates': ['LFPO'],
            'ralts': ['MYNN', 'CYQX', 'LPLA', 'EINN'],
            'taxitime': 19,
        }
        self.assertDictEqual(ofp.infos, expected)
        dt = ofp.infos['datetime']
        self.assertEqual(dt.tzname(), 'UTC')
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_duration_AF650(self):
        from datetime import datetime, timedelta, time
        from editolido.ofp import utc
        ofp = load_ofp(DATADIR + '/AF650_LFPG_MMUN_04Mar2018_13:55z_OFP_7_0_1_workflow_1_7_8.txt')

        self.assertEqual('1.7.8', ofp.workflow_version)
        expected = {
            'flight': 'AF650',
            'departure': 'LFPG',
            'destination': 'MMUN',
            'datetime': datetime(2018, 3, 4, 13, 55, tzinfo=utc),
            'duration': time(9, 27, tzinfo=utc),
            'ofp': '7/0/1',
            'date': '04Mar2018',
            'alternates': ['MMMD'],
            'ralts': ['EINN', 'CYQX'],
            'taxitime': 18,
        }
        self.assertDictEqual(ofp.infos, expected)
        dt = ofp.infos['datetime']
        self.assertEqual(dt.tzname(), 'UTC')
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_fpl_route(self):
        ofp = load_ofp(DATADIR + '/AF651_MMUN-LFPG_08Mar2018_00:30z_OFP_9_0_1_workflow_1_7_8.txt')

        expected = """(FPL-AFR651-IS
-B77W/H-SDE2E3FGHIJ3J5J6M1M2RWXYZ/LB1D1
-MMUN0030
-N0490F330 ANTEK2A ANTEK UJ18 URTOK UG765 MAXIM DCT EYW DCT
 PBI/M083F330 DCT SNAGY DCT OMALA M202 MUNEY/M083F360 NATY
 NERTU/M083F350 DCT RATKA/N0469F350 N502 PIKOD UN502 JSY/N0425F280
 UY111 INGOR UM25 LUKIP LUKIP8W
-LFPG0820 LFPO
-PBN/A1B1C1D1L1O1S2 DAT/1FANSP2PDC DOF/180308 REG/FGSQN
 EET/MUFH0012 KZMA0038 PBI0100 KZWY0126 OMALA0155 ONGOT0202
 GOUGH0209 KINER0227 OVAPI0236 MUNEY0247 41N060W0317 44N050W0411
 CZQX0427 47N040W0505 EGGX0552 49N020W0637 BEDRA0659 NERTU0703
 EGTT0729 LFFF0741 SEL/EJAG OPR/AFR PER/D RALT/MYNN CYQX LPLA EINN
 RVR/075 RMK/ACAS TCAS)"""
        self.assertEqual(expected, ofp.raw_fpl_text())
        expected = ['MMUN', 'ANTEK2A', 'ANTEK', 'UJ18', 'URTOK', 'UG765', 'MAXIM', 'DCT', 'EYW', 'DCT', 'PBI', 'DCT', 'SNAGY', 'DCT', 'OMALA', 'M202', 'MUNEY', 'NATY', 'NERTU', 'DCT', 'RATKA', 'N502', 'PIKOD', 'UN502', 'JSY', 'UY111', 'INGOR', 'UM25', 'LUKIP', 'LUKIP8W', 'LFPG']
        self.assertEqual(expected, ofp.fpl_route)

    def test_description(self):
        ofp = load_ofp(DATADIR + '/AF651_MMUN-LFPG_08Mar2018_00:30z_OFP_9_0_1_workflow_1_7_8.txt')

        expected = "AF651 MMUN-LFPG 08Mar2018 00:30z OFP 9/0/1"
        self.assertEqual(expected, ofp.description)

    def test_wpt_coordinates(self):
        ofp = load_ofp(DATADIR + '/AF651_MMUN-LFPG_08Mar2018_00:30z_OFP_9_0_1_workflow_1_7_8.txt')

        wpt_coordinates = list(ofp.wpt_coordinates())
        self.assertEqual(41, len(wpt_coordinates))

    def test_wpt_coordinates_alternate(self):
        ofp = load_ofp(DATADIR + '/AF651_MMUN-LFPG_08Mar2018_00:30z_OFP_9_0_1_workflow_1_7_8.txt')

        wpt_coordinates = list(ofp.wpt_coordinates_alternate())
        self.assertEqual(3, len(wpt_coordinates))

    def test_tracks_iterator(self):
        ofp = load_ofp(DATADIR + '/AF651_MMUN-LFPG_08Mar2018_00:30z_OFP_9_0_1_workflow_1_7_8.txt')

        tracks = list(ofp.tracks_iterator())
        self.assertEqual(8, len(tracks))

    def test_lido_route(self):
        ofp = load_ofp(DATADIR + '/AF651_MMUN-LFPG_08Mar2018_00:30z_OFP_9_0_1_workflow_1_7_8.txt')

        route = ofp.lido_route
        expected = ['MMUN', 'N2101.5W08651.5', 'ANTEK', 'UJ18', 'URTOK', 'UG765', 'MAXIM', 'DCT', 'EYW',
                    'DCT', 'PBI', 'DCT', 'SNAGY', 'DCT', 'OMALA', 'M202', 'MUNEY',
                    '41N060W', '44N050W', '47N040W', '48N030W', '49N020W', 'BEDRA',
                    'NERTU', 'DCT', 'RATKA', 'N502', 'PIKOD', 'UN502', 'JSY', 'UY111', 'INGOR', 'UM25',
                    'LUKIP', 'N4918.0E00134.2', 'N4917.5E00145.4', 'N4915.7E00223.3', 'N4915.3E00230.9',
                    'N4913.9E00242.9', 'LFPG', 'LFPO', 'MYNN', 'CYQX', 'LPLA', 'EINN']
        self.assertEqual(expected, route)

    def tests_tracks_with_fishpoints(self):
        ofp = load_ofp(DATADIR + '/AF651_MMUN-LFPG_08Mar2018_00:30z_OFP_9_0_1_workflow_1_7_8.txt')

        tracks = list(
            ofp.tracks(fishfile=FISHFILE))
        self.assertEqual(len(tracks), 8)
        self.assertEqual(
            tracks[0],
            Route([
                GeoPoint((49.500000, -52.000000), name="ELSIR"),
                GeoPoint((50, -50)),
                GeoPoint((52, -40)),
                GeoPoint((53, -30)),
                GeoPoint((54, -20)),
                GeoPoint((54.000000, -15.000000), name="DOGAL"),
                GeoPoint((54.000000, -14.000000), name="BEXET")])
        )
        self.assertTrue(tracks[0].is_complete)
        self.assertEqual(tracks[0].name, 'NAT S')
        self.assertEqual(tracks[7].name, 'NAT Z')
        self.assertEqual(
            tracks[7],  # Z
            Route([
                GeoPoint((38.500000, -60.270000), name="SOORY"),
                GeoPoint((43, -50)),
                GeoPoint((46, -40)),
                GeoPoint((47, -30)),
                GeoPoint((48, -20)),
                GeoPoint((48, -15)),
                GeoPoint((48.840000, -12), name="OMOKO"),
            ])
        )
        self.assertFalse(tracks[7].is_complete)  # GUNSO is missing in WPTS_OCA testfile
        self.assertTrue(tracks[0].name.endswith('S'))
        self.assertTrue(tracks[-1].name.endswith('Z'))

    def test_af377(self):
        ofp = load_ofp(DATADIR + '/AF377_KDTW-LFPG_11Mar2018_02:05z_OFP_9_0_1.txt')
        tracks = list(ofp.tracks())
        self.assertEqual(10, len(tracks))
        self.assertEqual(27, len(ofp.route))
        self.assertEqual(3, len(list(ofp.wpt_coordinates_alternate())))

    def test_af401(self):
        ofp = load_ofp(DATADIR + '/AF401_SCEL-LFPG_11Mar2018_17:15z_OFP_9_0_1.txt')
        self.assertEqual('9/0/1', ofp.infos['ofp'])
        tracks = list(ofp.tracks())
        self.assertEqual(9, len(tracks))
        self.assertEqual(107, len(ofp.route))
        self.assertEqual(3, len(list(ofp.wpt_coordinates_alternate())))

    def test_af946(self):
        # workflow 1.7.8 puts points without name in the wrong order, test the fix
        ofp = load_ofp(DATADIR + '/AF946_LFPG-MUHA_07Jun2018_14:10z_OFP_15_0_1.txt')
        self.assertEqual('1.7.8', ofp.workflow_version)
        wpt_coordinates = list(ofp.wpt_coordinates())
        self.assertEqual(36, len(wpt_coordinates))
        self.assertListEqual(
            [2.5483333333333333, 2.3466666666666667, 1.8933333333333333, 1.2216666666666667, -0.25, -1.1783333333333332,
             -2.046666666666667, -3.075, -3.55, -4.9816666666666665, -5.266666666666667, -5.823333333333333,
             -6.218333333333334, -7.0216666666666665, -8.0, -12.0, -15.0, -20.0, -30.0, -40.0, -45.0, -50.0, -55.0,
             -60.0, -67.24166666666666, -69.45333333333333, -71.09833333333333, -73.725, -76.32166666666667, -76.91,
             -77.44666666666667, -79.52833333333334, -82.92, -82.82666666666667, -82.57833333333333, -82.41],
            [float(wpt.longitude) for wpt in wpt_coordinates]
        )

    def test_af406(self):
        # workflow 1.7.8 puts points without name in the wrong order, test the fix
        ofp = load_ofp(DATADIR + '/AF406_LFPG-SCEL_25Jun2018_21:40z_OFP_14_0_1.txt')
        self.assertEqual('1.7.8', ofp.workflow_version)
        wpt_coordinates = list(ofp.wpt_coordinates())
        self.assertEqual(89, len(wpt_coordinates))
        self.maxDiff = None
        self.assertListEqual(
            [2.5483333333333333, 2.77, 2.9566666666666666, 2.395, 0.53, 0.15666666666666668, -0.25, -1.5183333333333333,
             -1.9283333333333332, -3.0, -5.408333333333333, -8.0, -8.75, -13.0, -20.0, -25.166666666666668, -30.0,
             -33.0, -35.0, -35.446666666666665, -36.0, -36.7, -40.0, -43.913333333333334, -44.068333333333335, -44.235,
             -44.44166666666667, -44.68333333333333, -44.81166666666667, -45.325, -45.905, -46.54833333333333,
             -47.17166666666667, -47.541666666666664, -48.195, -48.385, -48.505, -48.931666666666665,
             -49.266666666666666, -49.901666666666664, -50.35166666666667, -50.53333333333333, -51.08,
             -51.36833333333333, -51.843333333333334, -52.13, -52.295, -52.73166666666667, -53.12, -53.47833333333333,
             -54.01833333333333, -54.13, -54.346666666666664, -54.64, -54.99333333333333, -55.13166666666667, -55.53,
             -55.58833333333333, -56.98833333333334, -57.42166666666667, -57.49, -57.81333333333333, -58.11333333333334,
             -59.681666666666665, -59.98, -60.23, -60.995, -61.31166666666667, -61.92333333333333, -62.55,
             -62.86833333333333, -63.81, -64.08, -64.65333333333334, -65.74666666666667, -66.37, -66.80333333333333,
             -67.94833333333334, -69.31333333333333, -70.31666666666666, -70.49333333333334, -70.61666666666666, -70.72,
             -70.82333333333334, -70.81666666666666, -70.81166666666667, -70.80666666666667, -70.80333333333333,
             -70.79333333333334],
            [float(wpt.longitude) for wpt in wpt_coordinates]
        )

    def test_af406_pypdf2(self):
        # workflow 1.7.8 puts points without name in the wrong order, test the fix using pypdf2
        ofp = load_ofp(DATADIR + '/AF406_LFPG-SCEL_25Jun2018_21:40z_OFP_14_0_1_pypdf2.txt')
        self.assertEqual('pypdf2', ofp.workflow_version)
        wpt_coordinates = list(ofp.wpt_coordinates())
        self.assertEqual(89, len(wpt_coordinates))
        self.maxDiff = None
        self.assertListEqual(
            [2.5483333333333333, 2.77, 2.9566666666666666, 2.395, 0.53, 0.15666666666666668, -0.25, -1.5183333333333333,
             -1.9283333333333332, -3.0, -5.408333333333333, -8.0, -8.75, -13.0, -20.0, -25.166666666666668, -30.0,
             -33.0, -35.0, -35.446666666666665, -36.0, -36.7, -40.0, -43.913333333333334, -44.068333333333335, -44.235,
             -44.44166666666667, -44.68333333333333, -44.81166666666667, -45.325, -45.905, -46.54833333333333,
             -47.17166666666667, -47.541666666666664, -48.195, -48.385, -48.505, -48.931666666666665,
             -49.266666666666666, -49.901666666666664, -50.35166666666667, -50.53333333333333, -51.08,
             -51.36833333333333, -51.843333333333334, -52.13, -52.295, -52.73166666666667, -53.12, -53.47833333333333,
             -54.01833333333333, -54.13, -54.346666666666664, -54.64, -54.99333333333333, -55.13166666666667, -55.53,
             -55.58833333333333, -56.98833333333334, -57.42166666666667, -57.49, -57.81333333333333, -58.11333333333334,
             -59.681666666666665, -59.98, -60.23, -60.995, -61.31166666666667, -61.92333333333333, -62.55,
             -62.86833333333333, -63.81, -64.08, -64.65333333333334, -65.74666666666667, -66.37, -66.80333333333333,
             -67.94833333333334, -69.31333333333333, -70.31666666666666, -70.49333333333334, -70.61666666666666, -70.72,
             -70.82333333333334, -70.81666666666666, -70.81166666666667, -70.80666666666667, -70.80333333333333,
             -70.79333333333334],
            [float(wpt.longitude) for wpt in wpt_coordinates]
        )


class TestOFPForWorkflow178MC(TestCase):
    def test_infos(self):
        from datetime import datetime, timedelta, time
        from editolido.ofp import utc
        ofp = load_ofp(DATADIR + '/AF1753_UKBB-LFPG_28Mar2016_12:15z_OFP13_workflow_1.7.8.txt')

        self.assertEqual('1.7.8', ofp.workflow_version)
        expected = {
            'flight': 'AF1753',
            'departure': 'UKBB',
            'destination': 'LFPG',
            'datetime': datetime(2016, 3, 28, 12, 15, tzinfo=utc),
            'duration': time(2, 57, tzinfo=utc),
            'ofp': '13',
            'date': '28Mar2016',
            'alternates': ['LFOB'],
            'ralts': [],
            'taxitime': 11,
        }
        self.assertDictEqual(ofp.infos, expected)
        dt = ofp.infos['datetime']
        self.assertEqual(dt.tzname(), 'UTC')
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_fpl_route(self):
        ofp = load_ofp(DATADIR + '/AF1753_UKBB-LFPG_28Mar2016_12:15z_OFP13_workflow_1.7.8.txt')

        self.assertEqual('1.7.8', ofp.workflow_version)
        expected = """(FPL-AFR1753-IS
-A319/M-SDE2E3FGIJ1RWY/H
-UKBB1215
-K0818F360 KR P27 PEVOT T708 GIDNO/K0829F380 T708 DIBED/N0446F380
 L984 OKG UL984 NOSPA DCT IDOSA UN857 RAPOR UZ157 VEDUS VEDUS6W
-LFPG0257 LFOB
-PBN/A1B1C1D1L1O1S2 DOF/160328 REG/FGRHK EET/EPWW0046 LKAA0112
 EDUU0146 EBUR0222 LFFF0228 CODE/3944EA OPR/AFR RVR/075 RMK/TCAS)"""
        self.assertEqual(expected, ofp.raw_fpl_text())
        expected = ['UKBB', 'KR', 'P27', 'PEVOT', 'T708', 'GIDNO', 'T708', 'DIBED', 'L984', 'OKG', 'UL984', 'NOSPA',
                    'DCT', 'IDOSA', 'UN857', 'RAPOR', 'UZ157', 'VEDUS', 'VEDUS6W', 'LFPG']
        self.assertEqual(expected, ofp.fpl_route)

    def test_description(self):
        ofp = load_ofp(DATADIR + '/AF1753_UKBB-LFPG_28Mar2016_12:15z_OFP13_workflow_1.7.8.txt')

        self.assertEqual('1.7.8', ofp.workflow_version)
        expected = "AF1753 UKBB-LFPG 28Mar2016 12:15z OFP 13"
        self.assertEqual(expected, ofp.description)

    def test_wpt_coordinates(self):
        ofp = load_ofp(DATADIR + '/AF1753_UKBB-LFPG_28Mar2016_12:15z_OFP13_workflow_1.7.8.txt')

        self.assertEqual('1.7.8', ofp.workflow_version)
        wpt_coordinates = list(ofp.wpt_coordinates())
        self.assertEqual(59, len(wpt_coordinates))

    def test_wpt_coordinates_alternate(self):
        ofp = load_ofp(DATADIR + '/AF1753_UKBB-LFPG_28Mar2016_12:15z_OFP13_workflow_1.7.8.txt')

        self.assertEqual('1.7.8', ofp.workflow_version)
        wpt_coordinates = list(ofp.wpt_coordinates_alternate())
        self.assertEqual(3, len(wpt_coordinates))

    def test_lido_route(self):
        ofp = load_ofp(DATADIR + '/AF1753_UKBB-LFPG_28Mar2016_12:15z_OFP13_workflow_1.7.8.txt')

        self.assertEqual('1.7.8', ofp.workflow_version)
        route = ofp.lido_route
        expected = ['UKBB', 'N5030.6E03051.1', 'N5032.0E03039.8', 'N5024.3E03017.3', 'KR', 'P27', 'PEVOT', 'T708',
                    'GIDNO', 'T708', 'DIBED', 'L984', 'OKG', 'UL984', 'NOSPA', 'DCT', 'IDOSA', 'UN857', 'RAPOR',
                    'UZ157', 'VEDUS', 'N4935.8E00404.0', 'N4928.5E00346.7', 'N4927.0E00337.9',
                    'N4925.2E00327.1', 'N4916.5E00319.6', 'LFPG', 'LFOB']
        self.assertEqual(expected, route)


class TestNVPOFPForPdfMiner(TestCase):
    def test_infos(self):
        from datetime import datetime, timedelta, time
        from editolido.ofp import utc
        ofp = load_ofp(DATADIR + '/AF 010_LFPG-KJFK_27Sep2019_1450z_OFP_6_nvp_pdfminer.txt')
        self.assertEqual('pypdf2', ofp.workflow_version)
        expected = {
            'flight': 'AF010',
            'departure': 'LFPG',
            'destination': 'KJFK',
            'datetime': datetime(2019, 9, 27, 14, 50, tzinfo=utc),
            'duration': time(7, 5, tzinfo=utc),
            'ofp': '6',
            'date': '27Sep2019',
            'alternates': ['KBOS'],
            'ralts': [],
            'taxitime': 24,
        }
        self.maxDiff = None
        self.assertDictEqual(ofp.infos, expected)
        dt = ofp.infos['datetime']
        self.assertEqual(dt.tzname(), 'UTC')
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_fpl_route(self):
        ofp = load_ofp(DATADIR + '/AF 010_LFPG-KJFK_27Sep2019_1450z_OFP_6_nvp_pdfminer.txt')
        expected = """(FPL-AFR010-IS -A388/H-SDE2E3GHIJ4J5M1P2RWXYZ/LB1D1 -LFPG1450 -N0480F260 ATREX3A ATREX UT225 VESAN UL613 SOVAT/N0502F380 UL613 SANDY UN601 LESTA UP6 RODOL UM65 TENSO L603 REMSI DCT GOMUP/M086F380 NATB LOMSI/N0498F380 DCT DANOL DCT ENE J121 SEY PARCH3 -KJFK0705 KBOS -PBN/A1B1C1D1L1O1S2 DAT/1FANSP2PDC SUR/RSP180 DOF/190927 REG/FHPJE EET/EGTT0019 EGPX0104 EGGX0129 58N020W0209 CZQX0249 57N040W0329 55N050W0415 LOMSI0449 CZUL0504 CZQM0546 KZBW0608 SEL/CPHQ CODE/39BD24 OPR/AFR PER/C RVR/075 RMK/ACAS TCAS)"""
        self.assertEqual(expected, ofp.raw_fpl_text())
        expected = [u'LFPG', u'ATREX3A', u'ATREX', u'UT225', u'VESAN', u'UL613', u'SOVAT', u'UL613', u'SANDY', u'UN601', u'LESTA', u'UP6', u'RODOL', u'UM65', u'TENSO', u'L603', u'REMSI', u'DCT', u'GOMUP', u"NATB", u'LOMSI', u'DCT', u'DANOL', u'DCT', u'ENE', u'J121', u'SEY', u'PARCH3', u'', u'KJFK']
        self.assertEqual(expected, ofp.fpl_route)

    def test_description(self):
        ofp = load_ofp(DATADIR + '/AF 010_LFPG-KJFK_27Sep2019_1450z_OFP_6_nvp_pdfminer.txt')
        print(ofp.description)
        expected = "AF010 LFPG-KJFK 27Sep2019 14:50z OFP 6"
        self.assertEqual(expected, ofp.description)

    def test_wpt_coordinates(self):
        ofp = load_ofp(DATADIR + '/AF 010_LFPG-KJFK_27Sep2019_1450z_OFP_6_nvp_pdfminer.txt')

        wpt_coordinates = list(ofp.wpt_coordinates())
        self.assertEqual(36, len(wpt_coordinates))

    def test_wpt_coordinates_alternate(self):
        ofp = load_ofp(DATADIR + '/AF 010_LFPG-KJFK_27Sep2019_1450z_OFP_6_nvp_pdfminer.txt')

        wpt_coordinates = list(ofp.wpt_coordinates_alternate())
        self.assertEqual(11, len(wpt_coordinates))

    def test_lido_route(self):
        ofp = load_ofp(DATADIR + '/AF 010_LFPG-KJFK_27Sep2019_1450z_OFP_6_nvp_pdfminer.txt')

        route = ofp.lido_route
        expected = [u'LFPG', u'N4900.9E00225.0', u'N4907.1E00219.2', u'ATREX', u'UT225', u'VESAN', u'UL613', u'SOVAT', u'UL613', u'SANDY', u'UN601', u'LESTA', u'UP6', u'RODOL', u'UM65', u'TENSO', u'L603', u'REMSI', u'DCT', u'GOMUP', u'58N020W', u'58N030W', u'57N040W', u'55N050W', u'LOMSI', u'DCT', u'DANOL', u'DCT', u'ENE', u'J121', u'SEY', u'N4106.0W07207.2', u'N4055.8W07247.9', u'N4041.1W07302.0', u'N4041.2W07320.6', u'N4045.6W07337.8', u'KJFK', u'KBOS']
        self.assertEqual(expected, route)

    def test_tracks(self):
        ofp = load_ofp(DATADIR + '/AF 010_LFPG-KJFK_27Sep2019_1450z_OFP_6_nvp_pdfminer.txt')

        tracks = list(ofp.tracks())
        self.assertEqual(len(tracks), 5)
        self.assertEqual(
            tracks[0],
            Route([
                GeoPoint((59.000000, -20.000000)),
                GeoPoint((59.000000, -30.000000)),
                GeoPoint((58.000000, -40.000000)),
                GeoPoint((56.000000, -50.000000))])
        )
        for p in tracks[0]:
            self.assertTrue(p.name)
        self.assertTrue(tracks[0].name.endswith('A'))
        self.assertTrue(tracks[-1].name.endswith('E'))


class TestS4OFPForPdfMiner(TestCase):
    def test_infos(self):
        from datetime import datetime, timedelta, time
        from editolido.ofp import utc
        ofp = load_ofp(DATADIR + '/AF342_LFPG-CYUL_30Jul2019_14-00z_OFP7_0_1_pdfminer.txt')
        self.assertEqual('pypdf2', ofp.workflow_version)
        expected = {
            'flight': 'AF342',
            'departure': 'LFPG',
            'destination': 'CYUL',
            'datetime': datetime(2019, 7, 30, 13, 40, tzinfo=utc),
            'duration': time(6, 46, tzinfo=utc),
            'ofp': '7/0/1',
            'date': '30Jul2019',
            'alternates': ['KBGR'],
            'ralts': ['EINN', 'CYYR'],
            'taxitime': 20,
        }
        self.maxDiff = None
        self.assertDictEqual(ofp.infos, expected)
        dt = ofp.infos['datetime']
        self.assertEqual(dt.tzname(), 'UTC')
        self.assertEqual(dt.utcoffset(), timedelta(0))

    def test_fpl_route(self):
        ofp = load_ofp(DATADIR + '/AF342_LFPG-CYUL_30Jul2019_14-00z_OFP7_0_1_pdfminer.txt')

        self.assertEqual('pypdf2', ofp.workflow_version)
        expected = """(FPL-AFR342-IS-B77W/H-SDE2E3FGHIJ3J5J6M1M2P2RWXYZ/LB1D1-LFPG1340-N0489F340 EVX2A EVX UT300 SENLO UN502 JSY UN160 LIZAD UL739 GAPLI/M083F340 DCT RODEL DCT 51N020W 52N030W 52N040W/M083F360 51N050W DCT ALLRY/N0481F360 N362A MIILS DCT VLV OMBRE6-CYUL0646 KBGR-PBN/A1B1C1D1L1O1S2 DAT/1FANSP2PDC SUR/RSP180 DOF/190730 REG/FGZNO EET/EGTT0038 EGGX0057 RODEL0134 51N020W0159 CZQX0250 52N040W0341 51N050W0432 ALLRY0443 CZQM0536 KZBW0611 CZUL0625 SEL/CPEQ CODE/3965AE OPR/AFR PER/D RALT/EINN CYYR RVR/075 RMK/ACAS TCAS)"""
        self.assertEqual(expected, ofp.raw_fpl_text())
        expected = [u'LFPG', u'EVX2A', u'EVX', u'UT300', u'SENLO', u'UN502', u'JSY', u'UN160', u'LIZAD', u'UL739', u'GAPLI', u'DCT', u'RODEL', u'DCT', u'51N020W', u'52N030W', u'52N040W', u'51N050W', u'DCT', u'ALLRY', u'N362A', u'MIILS', u'DCT', u'VLV', u'OMBRE6', u'CYUL']
        self.assertEqual(expected, ofp.fpl_route)

    def test_description(self):
        ofp = load_ofp(DATADIR + '/AF342_LFPG-CYUL_30Jul2019_14-00z_OFP7_0_1_pdfminer.txt')

        self.assertEqual('pypdf2', ofp.workflow_version)
        expected = "AF342 LFPG-CYUL 30Jul2019 13:40z OFP 7/0/1"
        self.assertEqual(expected, ofp.description)

    def test_wpt_coordinates(self):
        ofp = load_ofp(DATADIR + '/AF342_LFPG-CYUL_30Jul2019_14-00z_OFP7_0_1_pdfminer.txt')

        self.assertEqual('pypdf2', ofp.workflow_version)
        wpt_coordinates = list(ofp.wpt_coordinates())
        self.assertEqual(28, len(wpt_coordinates))

    def test_wpt_coordinates_alternate(self):
        ofp = load_ofp(DATADIR + '/AF342_LFPG-CYUL_30Jul2019_14-00z_OFP7_0_1_pdfminer.txt')

        self.assertEqual('pypdf2', ofp.workflow_version)
        wpt_coordinates = list(ofp.wpt_coordinates_alternate())
        self.assertEqual(6, len(wpt_coordinates))

    def test_lido_route(self):
        ofp = load_ofp(DATADIR + '/AF342_LFPG-CYUL_30Jul2019_14-00z_OFP7_0_1_pdfminer.txt')

        self.assertEqual('pypdf2', ofp.workflow_version)
        route = ofp.lido_route
        expected = [u'LFPG', u'N4900.7E00221.7', u'N4902.3E00208.8', u'N4903.9E00137.7', u'EVX', u'UT300', u'SENLO', u'UN502', u'JSY', u'UN160', u'LIZAD', u'UL739', u'GAPLI', u'DCT', u'RODEL', u'DCT', u'51N020W', u'52N030W', u'52N040W', u'51N050W', u'DCT', u'ALLRY', u'N362A', u'MIILS', u'DCT', u'VLV', u'N4552.2W07129.0', u'N4549.0W07202.5', u'N4547.0W07222.9', u'N4545.3W07240.0', u'N4544.8W07245.7', u'N4543.5W07257.7', u'N4542.5W07307.4', u'N4538.0W07330.7', u'CYUL', u'KBGR', u'EINN', u'CYYR']
        self.assertEqual(expected, route)

    def test_tracks(self):
        ofp = load_ofp(DATADIR + '/AF342_LFPG-CYUL_30Jul2019_14-00z_OFP7_0_1_pdfminer.txt')

        tracks = list(ofp.tracks())
        self.assertEqual(len(tracks), 6)
        self.assertEqual(
            tracks[0],
            Route([
                GeoPoint((62.000000, -20.000000)),
                GeoPoint((63.000000, -30.000000)),
                GeoPoint((64.000000, -40.000000)),
                GeoPoint((63.000000, -50.000000))])
        )
        for p in tracks[0]:
            self.assertTrue(p.name)
        self.assertTrue(tracks[0].name.endswith('A'))
        self.assertTrue(tracks[-1].name.endswith('F'))
