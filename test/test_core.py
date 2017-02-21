# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import shutil
import tempfile
from distutils.version import StrictVersion
from unittest import TestCase
import mock
import pytest
import six


online = pytest.mark.skipif(
    pytest.config.getoption("--offline"),
    reason="remove --offline option to run"
)


class TestCore(TestCase):

    def test_raw_content_url_my_repo_tag(self):
        from editolido.core import raw_content_url
        self.assertEqual(
            raw_content_url(
                'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'),
            'https://raw.githubusercontent.com/flyingeek/editolido/master'
            '/editolido/bootstrap_editorial.py'
        )

    def test_raw_content_url_my_repo_branch(self):
        from editolido.core import raw_content_url
        self.assertEqual(
            raw_content_url(
                'https://github.com/flyingeek/editolido/archive/mybranch.zip',
                'test.json'),
            'https://raw.githubusercontent.com/flyingeek/editolido/mybranch'
            '/editolido/test.json'
        )

    def test_raw_content_url_another_repo_branch(self):
        from editolido.core import raw_content_url
        self.assertEqual(
            raw_content_url(
                'https://github.com/another/editolido2/archive/mybranch.zip'),
            'https://raw.githubusercontent.com/another/editolido2/mybranch'
            '/editolido2/bootstrap_editorial.py'
        )

    @mock.patch('editolido.core.logger')
    def test_raw_content_url_uses_latest_if_empty(self, logger):
        from editolido.core import raw_content_url
        self.assertEqual(
            raw_content_url(''),
            'https://raw.githubusercontent.com/flyingeek/editolido/master'
            '/editolido/bootstrap_editorial.py'
        )
        logger.info.assert_not_called()

    @mock.patch('editolido.core.logger')
    def test_raw_content_url_uses_default_if_invalid(self, logger):
        from editolido.core import raw_content_url
        self.assertEqual(
            raw_content_url('blabla'),
            'https://raw.githubusercontent.com/flyingeek/editolido/master'
            '/editolido/bootstrap_editorial.py'
        )
        logger.info.assert_called_with('using default bootstrap url')

    @mock.patch('editolido.core.logger')
    @online
    def test_get_latest_version_output_404_if_doesnotexists(self, logger):
        from editolido.core import get_latest_version_infos
        import requests
        with self.assertRaises(requests.exceptions.RequestException):
            get_latest_version_infos(
                'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip',
                'doesnotexists'
            )
        logger.error.assert_called_with('status code 404')

    @mock.patch('editolido.core.logger')
    @online
    def test_get_latest_version_infos(self, logger):
        from editolido.core import get_latest_version_infos
        from editolido.bootstrap_editorial import VERSION
        url = 'https://github.com/flyingeek/editolido/archive/{0}.zip'.format(
            VERSION)
        get_latest_version_infos(url)
        self.assertTrue(logger.info.called)
        self.assertFalse(logger.error.called)

    def test_needs_update_to_same_version(self):
        from editolido.core import needs_update, infos_from_giturl
        loc = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip')
        rem = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip')
        self.assertFalse(needs_update(loc, rem))

    def test_needs_update_to_same_version_another_owner(self):
        from editolido.core import needs_update, infos_from_giturl
        loc = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip')
        rem = infos_from_giturl(
            'https://github.com/eric/editolido/archive/1.0.0b7.zip')
        self.assertTrue(needs_update(loc, rem))

    def test_needs_update_to_lower_version(self):
        from editolido.core import needs_update, infos_from_giturl
        loc = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip')
        rem = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/1.0.0b6.zip')
        self.assertFalse(needs_update(loc, rem))

    def test_needs_update_to_greater_version(self):
        from editolido.core import needs_update, infos_from_giturl
        loc = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip')
        rem = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/1.0.0b8.zip')
        self.assertTrue(needs_update(loc, rem))

    def test_needs_update_to_branch(self):
        from editolido.core import needs_update, infos_from_giturl
        loc = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip')
        rem = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/master.zip')
        self.assertTrue(needs_update(loc, rem))

    def test_needs_update_from_branch(self):
        from editolido.core import needs_update, infos_from_giturl
        loc = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/master.zip')
        rem = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip')
        self.assertTrue(needs_update(loc, rem))

    def test_needs_update_to_same_branch(self):
        from editolido.core import needs_update, infos_from_giturl
        loc = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/master.zip')
        rem = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/master.zip')
        self.assertFalse(needs_update(loc, rem))

    def test_needs_update_to_other_branch(self):
        from editolido.core import needs_update, infos_from_giturl
        loc = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/master.zip')
        rem = infos_from_giturl(
            'https://github.com/flyingeek/editolido/archive/another.zip')
        self.assertTrue(needs_update(loc, rem))

    def test_read_local_config_utf8(self):
        from editolido.core import read_local_config
        json = '{"test": "éè"}'
        if six.PY2:
            json = json.encode('utf-8')
        with mock.patch('editolido.core.open',
                        mock.mock_open(read_data=json), create=True) as m:
            data = read_local_config()
        self.assertTrue(m.called)
        self.assertEqual(data['test'], 'éè')

    def test_read_local_config_null_version(self):
        from editolido.core import read_local_config
        json = '{"version": null}'
        with mock.patch('editolido.core.open',
                        mock.mock_open(read_data=json), create=True) as m:
            data = read_local_config()
        self.assertTrue(m.called)
        self.assertIs(data['version'], None)

    def test_read_local_config_strictversion(self):
        from editolido.core import read_local_config
        json = '{"version": "1.0b7"}'
        with mock.patch('editolido.core.open',
                        mock.mock_open(read_data=json), create=True) as m:
            data = read_local_config()
        self.assertTrue(m.called)
        self.assertEqual(data['version'], StrictVersion('1.0.0b7'))


class TestCoreUpdateAutoMode(TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        def clean_dir():
            shutil.rmtree(self.test_dir)
        self.addCleanup(clean_dir)

        patcher1 = mock.patch('editolido.core.get_install_dir')
        self.get_install_dir = patcher1.start()
        self.get_install_dir.return_value = self.test_dir
        self.addCleanup(patcher1.stop)
        patcher2 = mock.patch('editolido.core.download_package')
        self.download_package = patcher2.start()
        self.addCleanup(patcher2.stop)
        patcher3 = mock.patch('editolido.core.get_latest_version_infos')
        self.json = patcher3.start()
        self.addCleanup(patcher3.stop)
        patcher4 = mock.patch('editolido.core.save_local_config')
        self.cfg_write = patcher4.start()
        self.addCleanup(patcher4.stop)
        patcher5 = mock.patch('editolido.core.logger')
        self.logger = patcher5.start()
        self.addCleanup(patcher5.stop)
        patcher6 = mock.patch('editolido.bootstrap_editorial.workflow')
        self.workflow = patcher6.start()
        patcher7 = mock.patch('editolido.core.read_local_config')
        self.cfg = patcher7.start()
        self.addCleanup(patcher7.stop)
        from editolido.bootstrap_editorial import AUTO_UPDATE_KEY
        self.workflow.get_parameters.return_value = {AUTO_UPDATE_KEY: True}
        self.addCleanup(patcher6.stop)

    def filename(self, filename):
        kall = self.download_package.mock_calls[0]
        _, args, kwargs = kall
        return args[0], filename

    def test_get_install_dir(self):
        from editolido.core import get_install_dir
        self.assertEqual(get_install_dir(), self.test_dir)

    def test_reload_editolido(self):
        from editolido.core import reload_editolido
        reload_editolido(self.test_dir)

    def test_update_editolido_empty_url_up_to_date(self):
        from editolido.core import update_editolido, infos_from_giturl
        from editolido.bootstrap_editorial import VERSION
        local = ('https://github.com/flyingeek/editolido/archive/%s.zip'
                 % VERSION)
        remote = local
        param = ''
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.logger.error.assert_not_called()
        self.download_package.assert_not_called()  # up to date

    def test_update_editolido_empty_url_needs_update(self):
        from editolido.core import update_editolido, infos_from_giturl
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        remote = 'https://github.com/flyingeek/editolido/archive/1.0.0b8.zip'
        param = ''
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.assertTrue(self.download_package.called)
        self.logger.error.assert_not_called()

    def test_update_editolido_bad_url(self):
        from editolido.core import update_editolido, infos_from_giturl
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        remote = 'https://github.com/flyingeek/editolido/archive/1.0.0b8.zip'
        param = 'http://www.example.com'
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.download_package.assert_not_called()
        self.logger.error.assert_called_with(
            'invalid url http://www.example.com')

    def test_update_editolido_bad_json(self):
        from editolido.core import update_editolido, infos_from_giturl
        from editolido.bootstrap_editorial import VERSION
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        remote = 'https://github.com/flyingeek/editolido/archive/invalid.zip'
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b6.zip'
        call = mock.call
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.assertIn('json rejected', repr(self.logger.error.call_args))
        expected = [
            call('remote version: 1.0.0b6'),
            call('remote zipball url: https://github.com/flyingeek'
                 '/editolido/archive/1.0.0b6.zip'),
            call(u'local version is %s' % VERSION)]
        self.assertEqual(self.logger.info.mock_calls, expected)
        self.download_package.assert_not_called()

    def test_update_editolido_json_greater(self):
        from editolido.core import update_editolido, infos_from_giturl
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        remote = 'https://github.com/flyingeek/editolido/archive/1.0.0b8.zip'
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b6.zip'
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.logger.info.assert_any_call('remote version: 1.0.0b8')
        self.logger.error.assert_not_called()
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(remote))

    def test_update_editolido_same_version(self):
        from editolido.core import update_editolido, infos_from_giturl
        from editolido.bootstrap_editorial import VERSION
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        remote = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b6.zip'
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.logger.info.assert_any_call('remote version: 1.0.0b7')
        # consider up to date if same version
        self.logger.info.assert_any_call('local version is %s'
                                         % VERSION)
        self.download_package.assert_not_called()
        self.logger.error.assert_not_called()

    def test_update_editolido_url_param_greater(self):
        from editolido.core import update_editolido, infos_from_giturl
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        remote = 'https://github.com/flyingeek/editolido/archive/1.0.0b8.zip'
        param = "https://github.com/flyingeek/editolido/archive/1.0.0b8.zip"
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.logger.info.assert_any_call('remote version: 1.0.0b8')
        self.logger.error.assert_not_called()
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(param))

    def test_update_editolido_params_greater_json(self):
        from editolido.core import update_editolido, infos_from_giturl
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        remote = "https://github.com/flyingeek/editolido/archive/1.0.0b7.zip"
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b9.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.logger.info.assert_any_call('remote version: 1.0.0b9')
        self.logger.error.assert_not_called()
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(param))

    def test_update_editolido_to_branch(self):
        from editolido.bootstrap_editorial import VERSION
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/99.99.99.zip"
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        param = 'https://github.com/flyingeek/editolido/archive/master.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.logger.info.assert_any_call('editolido [master] %s installed'
                                         % VERSION)
        self.assertTrue(self.download_package.called)
        self.logger.error.assert_not_called()
        self.logger.info.assert_any_call('remote version: master')
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(param))

    def test_update_lido_logic_same_branch(self):
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/99.99.99.zip"
        local = 'https://github.com/flyingeek/editolido/archive/master.zip'
        param = 'https://github.com/flyingeek/editolido/archive/master.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.logger.info.assert_any_call('remote version: master')
        self.logger.error.assert_not_called()
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(param))

    def test_update_lido_logic_from_branch(self):
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/99.99.99.zip"
        local = 'https://github.com/flyingeek/editolido/archive/master.zip'
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.assertTrue(self.download_package.called)
        self.assertTrue(self.download_package.called)
        self.logger.info.assert_any_call('remote version: 99.99.99')
        self.logger.error.assert_not_called()
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(remote))


class TestCoreUpdateAutoOFF(TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        def clean_dir():
            shutil.rmtree(self.test_dir)

        self.addCleanup(clean_dir)

        patcher1 = mock.patch('editolido.core.get_install_dir')
        self.get_install_dir = patcher1.start()
        self.get_install_dir.return_value = self.test_dir
        self.addCleanup(patcher1.stop)
        patcher2 = mock.patch('editolido.core.download_package')
        self.download_package = patcher2.start()
        self.addCleanup(patcher2.stop)
        patcher3 = mock.patch('editolido.core.get_latest_version_infos')
        self.json = patcher3.start()
        self.addCleanup(patcher3.stop)
        patcher4 = mock.patch('editolido.core.save_local_config')
        self.cfg_write = patcher4.start()
        self.addCleanup(patcher4.stop)
        patcher5 = mock.patch('editolido.core.logger')
        self.logger = patcher5.start()
        self.addCleanup(patcher5.stop)
        patcher6 = mock.patch('editolido.bootstrap_editorial.workflow')
        self.workflow = patcher6.start()
        patcher7 = mock.patch('editolido.core.read_local_config')
        self.cfg = patcher7.start()
        self.addCleanup(patcher7.stop)
        from editolido.bootstrap_editorial import AUTO_UPDATE_KEY
        self.workflow.get_parameters.return_value = {AUTO_UPDATE_KEY: False}
        self.addCleanup(patcher6.stop)

    def filename(self, filename):
        kall = self.download_package.mock_calls[0]
        _, args, kwargs = kall
        return args[0], filename

    def test_update_editolido_empty_url_up_to_date(self):
        from editolido.core import update_editolido, infos_from_giturl
        from editolido.bootstrap_editorial import VERSION
        local = ('https://github.com/flyingeek/editolido/archive/%s.zip'
                 % VERSION)
        remote = ('https://github.com/flyingeek/editolido/archive/%s.zip'
                  % VERSION)
        param = ''
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.download_package.assert_not_called()
        self.logger.error.assert_not_called()

    def test_update_editolido_empty_url_needs_update(self):
        from editolido.core import update_editolido, infos_from_giturl
        from editolido.bootstrap_editorial import VERSION
        local = ('https://github.com/flyingeek/editolido/archive/%s.zip'
                 % VERSION)
        remote = 'https://github.com/flyingeek/editolido/archive/99.99.99.zip'
        param = ''
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.download_package.assert_not_called()
        self.logger.error.assert_not_called()

    def test_update_editolido_bad_url(self):
        from editolido.core import update_editolido, infos_from_giturl
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        remote = 'https://github.com/flyingeek/editolido/archive/1.0.0b8.zip'
        param = 'http://www.example.com'
        self.json.return_value = dict(url=remote)
        self.cfg.return_value = infos_from_giturl(local)
        update_editolido(param)
        self.download_package.assert_not_called()
        self.logger.error.assert_called_with(
            'invalid url http://www.example.com')

    def test_update_editolido_same_version(self):
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/1.0.0b7.zip"
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b6.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.download_package.assert_not_called()
        self.logger.error.assert_not_called()

    def test_update_editolido_url_param_greater(self):
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/1.0.0b8.zip"
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b8.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.logger.error.assert_not_called()
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(param))

    def test_update_editolido_params_greater_json(self):
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/1.0.0b8.zip"
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b9.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.logger.error.assert_not_called()
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(param))

    def test_update_editolido_json_greater_version(self):
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/1.0.0b8.zip"
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b6.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.download_package.assert_not_called()
        self.logger.error.assert_not_called()

    def test_update_editolido_to_branch(self):
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/99.99.99.zip"
        local = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        param = 'https://github.com/flyingeek/editolido/archive/master.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(param))
        self.logger.info.assert_any_call('remote version: master')
        self.logger.error.assert_not_called()

    def test_update_editolido_same_branch(self):
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/99.99.99.zip"
        local = 'https://github.com/flyingeek/editolido/archive/master.zip'
        param = 'https://github.com/flyingeek/editolido/archive/master.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.assertFalse(self.download_package.called)
        self.logger.error.assert_not_called()
        call = mock.call
        from editolido.bootstrap_editorial import VERSION
        expected = [
            call(u'auto update is disabled'),
            call('remote version: master'),
            call('remote zipball url: https://github.com/flyingeek'
                 '/editolido/archive/master.zip'),
            call(u'local code version is %s' % VERSION),
            call(u'local branch is [master]'), ]
        self.assertEqual(self.logger.info.mock_calls, expected)

    def test_update_editolido_from_branch(self):
        from editolido.core import update_editolido, infos_from_giturl
        remote = "https://github.com/flyingeek/editolido/archive/99.99.99.zip"
        local = 'https://github.com/flyingeek/editolido/archive/master.zip'
        param = 'https://github.com/flyingeek/editolido/archive/1.0.0b7.zip'
        self.cfg.return_value = infos_from_giturl(local)
        self.json.return_value = dict(url=remote)
        update_editolido(param)
        self.logger.error.assert_not_called()
        self.logger.info.assert_any_call('remote version: 1.0.0b7')
        self.assertTrue(self.download_package.called)
        self.assertIn(*self.filename(param))
