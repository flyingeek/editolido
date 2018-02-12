# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from unittest import TestCase
import mock
import os

from editolido.fishpoint import get_missing_fishpoints, find_fishfile, sort_fishfiles

DATADIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
FISHFILE = os.path.join(DATADIR, 'WPTS_OCA.csv')

# noinspection PyUnresolvedReferences
patch_object = mock.patch.object


class TestFishpoint(TestCase):
    def test_get_missing_fishpoints(self):
        fishpoints = get_missing_fishpoints(['RESNO', 'JOBOC'], fishfile=FISHFILE)
        self.assertTrue(len(fishpoints) == 2)
        self.assertEqual(fishpoints['JOBOC'], ('40.12', '-67.00'))
        self.assertEqual(fishpoints['RESNO'], ('55.00', '-15.00'))

    def test_find_fishfile(self):
        self.assertEqual(find_fishfile(path=DATADIR), os.path.join(DATADIR, 'WPTS_OCA.csv'))

    def test_sort_fishfiles(self):
        l = ['WPTS_OCA_1802.csv', 'WPTS_OCA_1803.csv', 'WPTS_OCA.csv']
        self.assertEqual(sort_fishfiles(l), ['WPTS_OCA_1803.csv', 'WPTS_OCA_1802.csv', 'WPTS_OCA.csv'])
