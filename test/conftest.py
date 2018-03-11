# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import json
import os
import shutil
import sys
import tempfile

import pytest
from mock import patch, Mock

patch.dict = patch.dict  # stops PyCharm complaining


def pytest_addoption(parser):
    parser.addoption("--offline", action="store_true", help="run online tests")


@pytest.fixture(scope='session')
def ofp_testfiles():
    _dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'data')
    return [f for f in os.listdir(_dir)
            if os.path.isfile(os.path.join(_dir, f)) and
            os.path.splitext(f)[1] == '.txt' and 'OFP' in f]


@pytest.fixture(scope='session')
def sigmets_testfiles():
    _dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'data')
    return [f for f in os.listdir(_dir)
            if os.path.isfile(os.path.join(_dir, f)) and
            os.path.splitext(f)[1] == '.json']


@pytest.fixture(scope='session', params=ofp_testfiles())
def ofp_filename(request):
    return request.param


@pytest.fixture(scope='session', params=sigmets_testfiles())
def sigmets_json(request):
    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datadir = os.path.join(os.path.join(module_dir, 'test'), 'data')
    with open(os.path.join(datadir, request.param), 'r') as f:
        return json.load(f)


@pytest.fixture(scope='session', params=ofp_testfiles())
def ofp_text(request):
    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datadir = os.path.join(os.path.join(module_dir, 'test'), 'data')
    with open(os.path.join(datadir, request.param), 'r') as f:
        return (f.read()).decode('utf-8')


@pytest.fixture(scope='session', params=[''] + ofp_testfiles())
def ofp_text_or_empty(request):
    if not request.param:
        return ''
    return ofp_text(request)


@pytest.fixture()
def mock_console(request):
    console = Mock()
    patcher = patch.dict(sys.modules, console=console)
    patcher.start()
    request.addfinalizer(patcher.stop)
    return console


@pytest.fixture()
def mock_editor(request):
    editor = Mock()
    patcher = patch.dict(sys.modules, editor=editor)
    patcher.start()
    request.addfinalizer(patcher.stop)
    return editor


@pytest.fixture()
def mock_dialogs(request):
    dialogs = Mock()
    patcher = patch.dict(sys.modules, dialogs=dialogs)
    patcher.start()
    request.addfinalizer(patcher.stop)
    return dialogs


@pytest.fixture()
def mock_clipboard(request):
    clipboard = Mock()
    patcher = patch.dict(sys.modules, clipboard=clipboard)
    patcher.start()
    request.addfinalizer(patcher.stop)
    return clipboard


@pytest.fixture()
def mock_workflow(request):
    workflow = Mock()
    patcher = patch.dict(sys.modules, workflow=workflow)
    patcher.start()
    request.addfinalizer(patcher.stop)
    return workflow


@pytest.fixture(scope="session")
def userdir(request):
    homedir = tempfile.mkdtemp()
    patcher = patch('os.path.expanduser', lambda x: homedir)
    patcher.start()

    def cleanup():
        shutil.rmtree(homedir)
        patcher.stop()
    request.addfinalizer(cleanup)


@pytest.fixture(scope='session')
def fishfile(request):
    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datadir = os.path.join(os.path.join(module_dir, 'test'), 'data')
    return os.path.join(datadir, 'WPTS_OCA.csv')
