# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import json
from distutils.version import StrictVersion
import os
import re
import shutil
import requests

try:
    import workflow  # in Editorial
except ImportError:
    from editolido.workflows.editorial.workflow import Workflow
    workflow = Workflow()


class Logger(object):

    @staticmethod
    def log(message, level=0):
        threshold = workflow.get_parameters().get('Log', 2)
        if level == 0 or (threshold and threshold >= level):
            print(message)

    def info(self, message):
        self.log(message, 2)

    def error(self, message):
        self.log(message, 1)

logger = Logger()
VERSION = '1.3.14'
DOCUMENTS = os.path.join(os.path.expanduser('~'), 'Documents')
AUTO_UPDATE_KEY = 'Mise à jour auto'

try:
    import console  # in Editorial
except ImportError:
    from editolido.workflows.editorial.console import Console
    console = Console(logger)


def download_package(github_url, zip_folder, install_dir, name="editolido",
                     timeout=None, fake=False):
    """
    Download a zip package and install it
    :param github_url: url to the github zip release
    :param zip_folder: folder to extract from the zip archive
    :param install_dir: where to install the extracted folder
    :param name: name of the extracted folder in install_dir
    :param timeout: float, tuple or None. see requests documentation
    :param fake: if True perform a dry run (no write to disk)
    :return:
    """
    import zipfile
    from contextlib import closing
    from io import BytesIO
    logger.info('downloading %s' % github_url)
    try:
        r = requests.get(github_url, verify=True, stream=True, timeout=timeout)
        r.raise_for_status()
        with closing(r), zipfile.ZipFile(BytesIO(r.content)) as z:
            base = '%s/%s/' % (zip_folder, name)
            logger.info('extracting data')
            if not fake:
                z.extractall(
                    os.getcwd(),
                    filter(lambda m: m.startswith(base), z.namelist()))
    except requests.HTTPError:  # pragma no cover
        # noinspection PyUnboundLocalVariable
        logger.error('status code %s' % r.status_code)
        raise
    except requests.Timeout:  # pragma no cover
        logger.error('download timeout... aborting update')
        raise
    except requests.ConnectionError:  # pragma no cover
        logger.error('download connection error... aborting update')
        raise
    except requests.TooManyRedirects:  # pragma no cover
        logger.error('too many redirects... aborting update')
        raise
    except requests.exceptions.RequestException:  # pragma no cover
        logger.error('download fail... aborting update')
        raise
    else:
        logger.info('installing %s' % name)
        if not os.path.exists(install_dir):  # pragma no cover
            logger.info('creating directory %s' % install_dir)
            os.makedirs(install_dir)
        dest = os.path.join(install_dir, name)
        try:
            if dest and name and os.path.exists(dest):
                shutil.rmtree(dest)
        except OSError:
            logger.error('could not remove %s' % dest)
            raise
        if zip_folder and not fake:
            shutil.move(os.path.join(zip_folder, name), install_dir)
            if not os.path.exists(os.path.join(install_dir, name)):
                logger.error('%s/%s directory missing' % (install_dir, name))
            logger.info('cleaning')
            try:
                shutil.rmtree(zip_folder)
            except OSError:
                logger.error('could not remove %s/%s'
                             % (os.getcwd(), zip_folder))
                raise


def get_install_dir():
    return DOCUMENTS


def get_local_config_filepath(filename='editolido.local.cfg.json',
                              module_name=None):
    """
    return the .local.cfg filename
    :param filename: the filename...
    :param module_name: useful only when loading bootstrap from github
    :return:
    """
    _dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
    if get_install_dir() in _dir:
        fp = os.path.join(_dir, filename)
    else:
        # bootstrap loaded and executed from github
        if module_name is None:
            module_name = 'editolido'
        fp = os.path.join(get_install_dir(), module_name)
        fp = os.path.join(fp, 'data')
        fp = os.path.join(fp, filename)
    return fp


def save_local_config(data, module_name=None):
    if isinstance(data['version'], StrictVersion):
        data['version'] = str(data['version'])
    filename = get_local_config_filepath(module_name=module_name)
    logger.info('saving to %s: %s' % (filename, data))
    with open(filename, 'w') as fd:
        json.dump(data, fd)


def is_branch(tagname):
    if not tagname:
        return True
    try:
        _ = StrictVersion(tagname)
    except (ValueError, AttributeError):
        return True
    return False


def check_old_install():
    path = 'site-packages/editolido'
    old_install_dir = os.path.join(DOCUMENTS, path)
    if os.path.exists(old_install_dir):
        logger.log('répertoire %s détecté' % path)
        shutil.rmtree(old_install_dir)
        logger.log('répertoire %s effacé' % path)
        logger.log('Veuillez quitter (tuer) puis relancer Editorial')
        raise KeyboardInterrupt


def auto_update_is_set():
    return workflow.get_parameters().get(AUTO_UPDATE_KEY, False)


def infos_from_giturl(url):
    """
    retrieve the tag or branch from the URL parameter of the action
    :param url: The URL parameter of the action
    :return: tag or branch
    """
    pattern = re.compile(
        r'/(?P<owner>[^/]+)/(?P<name>[^/]+)/archive/(?P<tag>[^/]+)\.zip')
    m = pattern.search(url)
    if m:
        d = m.groupdict()
        if is_branch(d['tag']):
            d['branch'] = d['tag']
            d['version'] = None
            d['branch_release'] = d['tag']
        else:
            d['branch'] = 'master'
            d['branch_release'] = False
            d['version'] = StrictVersion(d['tag'])
    else:
        d = dict(owner=None, name=None, tag=None,
                 branch=None, branch_release=None, version=None)
    return d


def latest_release(url):
    """
    Return the last release version and the zipball_url
    It looks silly but this file is loaded from remote so it might be
    a more recent version than the one included in the editolido module.
    We use regex replace here to allow url from a different repo
    :param url: The URL parameter of the action
    :return: version, url
    """
    infos = infos_from_giturl(url)
    tagname = infos['tag']
    if tagname:
        # replace first occurence from right to left
        url = url[::-1].replace(tagname[::-1], VERSION[::-1], 1)[::-1]
        return infos_from_giturl(url), url
    if not url:
        url = "https://github.com/flyingeek/editolido/archive/{0}.zip".format(
            VERSION
        )
        return infos_from_giturl(url), url
    logger.log('could not determine the latest release')
    return infos, url


def install_editolido(url, *args, **kwargs):
    """
    Download and install editolido module, will overwrite if module already
    exists. Checks and display installed version.
    :param url: url to the editolido zip github release (required)
    :return:
    """
    check_old_install()
    del args  # otherwise PyCharm complains not used
    del kwargs  # otherwise PyCharm complains not used
    if url:
        infos, zipball_url = infos_from_giturl(url), url
        if infos['version'] and auto_update_is_set():
            infos, zipball_url = latest_release(url)
    else:
        infos, zipball_url = latest_release(url)
    try:
        if infos['tag']:
                download_package(
                    zipball_url,
                    '%s-%s' % (infos['name'], infos['tag']),
                    get_install_dir(),
                    name=infos['name'],
                )
        else:
            logger.log('invalid url %s' % url)
            raise IOError
    except (IOError, OSError):
        logger.log('install failed')
    except requests.exceptions.RequestException:
        logger.error('install aborted')
    else:
        try:
            # noinspection PyUnresolvedReferences
            import editolido
            try:
                from importlib import reload
            except ImportError:
                # noinspection PyUnresolvedReferences
                from imp import reload
            reload(editolido)
        except ImportError:  # pragma no cover
            console.alert(
                'Module editolido manquant',
                "Assurez vous d'avoir une connexion internet et recommencez "
                "pour tenter un nouveau téléchargement",
                'OK',
                hide_cancel_button=True, )
            raise KeyboardInterrupt
        else:
            save_local_config(infos, module_name=infos['name'])
            if infos['version'] is None:
                console.hud_alert(
                    'editolido [%s] %s installé'
                    % (infos['branch'], editolido.__version__))
            else:
                console.hud_alert(
                    'module editolido %s installé' % editolido.__version__)
