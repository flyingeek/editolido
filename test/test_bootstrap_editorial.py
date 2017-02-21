# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.version import StrictVersion

import mock
import os
import pytest
import shutil
import tempfile
import six
from unittest import TestCase

online = pytest.mark.skipif(
    pytest.config.getoption("--offline"),
    reason="remove --offline option to run"
)


class TestBootstrapEditorial(TestCase):
    def test_infos_from_giturl_valid_version(self):
        from editolido.bootstrap_editorial import infos_from_giturl
        self.assertDictEqual(
            infos_from_giturl(
                'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'),
            dict(owner="flyingeek", name='editolido', tag="1.0.0b7",
                 version=StrictVersion('1.0.0b7'), branch='master',
                 branch_release=False)
        )

    def test_infos_from_giturl_valid_branch(self):
        from editolido.bootstrap_editorial import infos_from_giturl
        self.assertDictEqual(
            infos_from_giturl(
                'https://github.com/flyingeek/editolido/archive/master.zip'),
            dict(owner="flyingeek", name='editolido', tag="master",
                 version=None, branch='master', branch_release='master')
        )

    def test_infos_from_giturl_another_valid_branch(self):
        from editolido.bootstrap_editorial import infos_from_giturl
        self.assertEqual(
            infos_from_giturl(
                'https://github.com/another/editolido2/archive/master.zip'),
            dict(owner="another", name='editolido2', tag="master",
                 version=None, branch='master', branch_release='master')
        )

    def test_infos_from_giturl_invalid_url(self):
        from editolido.bootstrap_editorial import infos_from_giturl
        self.assertEqual(
            infos_from_giturl(
                'https://github.com/another/editolido2/data.py'),
            dict(owner=None, name=None, tag=None,  # TODO: partial extract ?
                 version=None, branch=None, branch_release=None)
        )

    def test_latest_release_current_version(self):
        from editolido.bootstrap_editorial import latest_release, VERSION,\
            infos_from_giturl
        url = 'https://github.com/flyingeek/editolido/archive/%s.zip' % VERSION
        expected_url = 'https://github.com/flyingeek/editolido/archive/%s.zip'\
                       % VERSION
        self.assertEqual(
            latest_release(url),
            (infos_from_giturl(expected_url), expected_url)
        )

    def test_latest_release_current_version_another(self):
        from editolido.bootstrap_editorial import latest_release, VERSION,\
            infos_from_giturl
        url = 'https://github.com/avatar/editolido2/archive/%s.zip' % VERSION
        expected_url = 'https://github.com/avatar/editolido2/archive/%s.zip'\
                       % VERSION
        self.assertEqual(
            latest_release(url),
            (infos_from_giturl(expected_url), expected_url)
        )

    def test_latest_release_old_version(self):
        from editolido.bootstrap_editorial import latest_release, VERSION,\
            infos_from_giturl
        url = 'https://github.com/flyingeek/editolido/archive/1.0.0b5.zip'
        expected_url = 'https://github.com/flyingeek/editolido/archive/%s.zip'\
                       % VERSION
        self.assertEqual(
            latest_release(url),
            (infos_from_giturl(expected_url), expected_url)
        )

    def test_latest_release_branch(self):
        from editolido.bootstrap_editorial import latest_release, VERSION, \
            infos_from_giturl
        url = 'https://github.com/flyingeek/editolido/archive/master.zip'
        expected_url = 'https://github.com/flyingeek/editolido/archive/%s.zip'\
                       % VERSION
        self.assertEqual(
            latest_release(url),
            (infos_from_giturl(expected_url), expected_url)
        )

    def test_latest_release_branch_another(self):
        from editolido.bootstrap_editorial import latest_release, VERSION, \
            infos_from_giturl
        url = 'https://github.com/avatar/editolido2/archive/master.zip'
        expected_url = 'https://github.com/avatar/editolido2/archive/%s.zip' \
                       % VERSION
        self.assertEqual(
            latest_release(url),
            (infos_from_giturl(expected_url), expected_url)
        )

    @mock.patch('editolido.bootstrap_editorial.logger')
    def test_latest_release_bad_url(self, logger):
        from editolido.bootstrap_editorial import latest_release,\
            infos_from_giturl
        url = 'http://www.google.fr'
        self.assertEqual(
            latest_release('http://www.google.fr'),
            (infos_from_giturl(url), url)
        )
        logger.log.assert_called_with('could not determine the latest release')

    def test_get_install_dir(self):
        from editolido.bootstrap_editorial import DOCUMENTS, get_install_dir
        self.assertEqual(get_install_dir(), DOCUMENTS)

    def test_is_branch(self):
        from editolido.bootstrap_editorial import is_branch
        self.assertFalse(is_branch('1.0.0b7'))
        self.assertFalse(is_branch('1.0.0'))
        self.assertTrue(is_branch('master'))
        self.assertTrue(is_branch(''))

    @mock.patch('editolido.bootstrap_editorial.logger')
    @online
    def test_download_package(self, logger):
        from editolido.bootstrap_editorial import download_package
        call = mock.call
        current_dir = os.getcwd()
        extract_dir = tempfile.mkdtemp()
        os.chdir(extract_dir)
        install_dir = tempfile.mkdtemp()
        download_package(
            'https://github.com/flyingeek/editolido/archive/master.zip',
            install_dir=install_dir,
            zip_folder='editolido-master',
            name='editolido',
        )
        os.chdir(current_dir)
        shutil.rmtree(extract_dir)
        shutil.rmtree(install_dir)
        expected = [
            call.info(u'downloading https://github.com/flyingeek/editolido'
                      u'/archive/master.zip'),
            call.info(u'extracting data'),
            call.info(u'installing editolido'),
            call.info(u'cleaning')]
        self.assertEqual(logger.mock_calls, expected)


class TestBoostrapEditorialOldInstall(TestCase):
    def setUp(self):
        patcher1 = mock.patch('editolido.bootstrap_editorial.os.path.exists')
        self.path_checker = patcher1.start()
        self.path_checker.return_value = True
        self.addCleanup(patcher1.stop)
        patcher2 = mock.patch('editolido.bootstrap_editorial.shutil.rmtree')
        self.rmtree = patcher2.start()
        self.addCleanup(patcher2.stop)

    @mock.patch('editolido.bootstrap_editorial.logger')
    def test_check_old_install(self, logger):
        from editolido.bootstrap_editorial import check_old_install, DOCUMENTS
        self.path_checker.assert_not_called()
        self.rmtree.assert_not_called()
        expected_old_dir = os.path.join(DOCUMENTS, 'site-packages/editolido')
        with self.assertRaises(KeyboardInterrupt):
            check_old_install()
        self.path_checker.assert_called_with(expected_old_dir)
        self.path_checker.assert_called_with(expected_old_dir)
        self.assertTrue(logger.log.called)


class TestBoostrapEditorialInstall(TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        def clean_dir():
            shutil.rmtree(self.test_dir)

        self.addCleanup(clean_dir)

        patcher1 = mock.patch('editolido.bootstrap_editorial.get_install_dir')
        self.get_install_dir = patcher1.start()
        self.get_install_dir.return_value = self.test_dir
        self.addCleanup(patcher1.stop)
        patcher2 = mock.patch('editolido.bootstrap_editorial.download_package')
        self.download_package = patcher2.start()
        self.addCleanup(patcher2.stop)
        patcher3 = mock.patch(
            'editolido.bootstrap_editorial.save_local_config')
        self.cfg = patcher3.start()
        self.addCleanup(patcher3.stop)

    def test_get_install_dir(self):
        from editolido.core import get_install_dir
        self.assertEqual(get_install_dir(), self.test_dir)

    @mock.patch('editolido.bootstrap_editorial.console')
    def test_install_editolido_branch(self, console):
        from editolido.bootstrap_editorial import install_editolido, VERSION
        install_editolido(
            'https://github.com/flyingeek/editolido/archive/master.zip',
        )
        self.assertTrue(self.download_package.called)
        console.hud_alert.assert_called_with('editolido [master] %s installé'
                                             % VERSION)

    @mock.patch('editolido.bootstrap_editorial.console')
    def test_install_editolido_tag(self, console):
        from editolido.bootstrap_editorial import install_editolido, VERSION
        install_editolido(
            'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip',
        )
        self.assertTrue(self.download_package.called)
        console.hud_alert.assert_called_with(
            'module editolido %s installé' % VERSION)\


    @mock.patch('editolido.bootstrap_editorial.console')
    @mock.patch('editolido.bootstrap_editorial.logger')
    def test_install_editolido_empty_url(self, logger, console):
        from editolido.bootstrap_editorial import install_editolido, VERSION
        install_editolido('')
        logger.assert_not_called()
        self.assertTrue(self.download_package.called)
        console.hud_alert.assert_called_with(
            'module editolido %s installé' % VERSION)

    @mock.patch('editolido.bootstrap_editorial.logger')
    def test_install_editolido_bad_url(self, logger):
        from editolido.bootstrap_editorial import install_editolido
        install_editolido('example.com')
        self.download_package.assert_not_called()
        logger.log.assert_any_call('invalid url example.com')
        logger.log.assert_any_call('install failed')


class TestLogger(TestCase):
    def setUp(self):
        if six.PY2:
            patcher = mock.patch('__builtin__.print')
        else:
            patcher = mock.patch('builtins.print')
        self.mock_print = patcher.start()
        self.addCleanup(patcher.stop)
        patcher2 = mock.patch('editolido.bootstrap_editorial.workflow')
        self.workflow = patcher2.start()
        self.addCleanup(patcher2.stop)

    def test_log_none(self):
        from editolido.bootstrap_editorial import Logger
        self.workflow.get_parameters.return_value = dict(Log=0)
        logger = Logger()
        logger.error('test_error')
        self.mock_print.assert_not_called()
        logger.info('test_info')
        self.mock_print.assert_not_called()
        logger.log('test_log')
        self.mock_print.assert_called_with('test_log')

    def test_log_error(self):
        from editolido.bootstrap_editorial import Logger
        self.workflow.get_parameters.return_value = dict(Log=1)
        logger = Logger()
        logger.error('test_error')
        self.mock_print.assert_called_with('test_error')
        self.mock_print.reset_mock()
        logger.info('test_info')
        self.mock_print.assert_not_called()
        logger.log('test_log')
        self.mock_print.assert_called_with('test_log')

    def test_log_info(self):
        from editolido.bootstrap_editorial import Logger
        self.workflow.get_parameters.return_value = dict(Log=2)
        logger = Logger()
        logger.error('test_error')
        self.mock_print.assert_called_with('test_error')
        self.mock_print.reset_mock()
        logger.info('test_info')
        self.mock_print.assert_called_with('test_info')
        self.mock_print.reset_mock()
        logger.log('test_log')
        self.mock_print.assert_called_with('test_log')


class TestBootstrapEditorialLocalConfig(TestCase):
    def setUp(self):
        patcher1 = mock.patch('editolido.bootstrap_editorial.logger')
        self.logger = patcher1.start()
        self.addCleanup(patcher1.stop)

    def test_get_local_config_filepath(self):
        from editolido.bootstrap_editorial import get_local_config_filepath
        self.assertTrue(get_local_config_filepath())

    def test_save_local_config_tag(self):
        from editolido.bootstrap_editorial import save_local_config,\
            infos_from_giturl
        m = mock.mock_open()
        with mock.patch('editolido.bootstrap_editorial.open', m, create=True):
            data = infos_from_giturl(
                'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip')
            save_local_config(data)
        self.assertTrue(m.called)
        handle = m()
        handle.write.assert_any_call('"1.0b7"')

    def test_save_local_config_branch(self):
        from editolido.bootstrap_editorial import save_local_config,\
            infos_from_giturl
        m = mock.mock_open()
        with mock.patch('editolido.bootstrap_editorial.open', m, create=True):
            data = infos_from_giturl(
                'https://github.com/flyingeek/editolido/archive/master.zip')
            save_local_config(data)
        self.assertTrue(m.called)
        handle = m()
        handle.write.assert_any_call('"master"')
        handle.write.assert_any_call('null')
