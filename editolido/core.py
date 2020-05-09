# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import sys
# noinspection PyUnresolvedReferences
from distutils.version import StrictVersion

import requests

import editolido
from editolido.bootstrap_editorial import logger, infos_from_giturl, \
    download_package, check_old_install, get_install_dir, auto_update_is_set,\
    latest_release, get_local_config_filepath, save_local_config


def raw_content_url(url, filename='bootstrap_editorial.py',
                    branch_or_tag=None):
    """
    Determine the github raw content url from the URL parameter of the action
    :param filename: the filename to access
    :param url: The URL parameter of the action
    :param branch_or_tag: optional branch or tag to force
    :return:
    """
    tpl = 'https://raw.githubusercontent.com/{owner}/{name}/{tag}' \
          '/{name}/' + filename
    if url:
        infos = infos_from_giturl(url)
    else:
        infos, url = latest_release(url)
    if branch_or_tag:
        infos['tag'] = branch_or_tag
    elif infos['branch']:
        infos['tag'] = infos['branch']
    else:
        logger.info('using default bootstrap url')
        infos = dict(owner='flyingeek', name='editolido', tag='master')
    return tpl.format(**infos)


def reload_editolido(install_dir, name='editolido'):
    try:
        from importlib import reload
    except ImportError:
        from imp import reload
    queue = []
    for module in sys.modules.values():
        try:
            if os.path.realpath(module.__file__).startswith(
                    os.path.join(install_dir, name) + '/'):  # pragma no cover
                if module.__name__ == name:
                    queue.append(module)
                else:
                    raise ImportError
        except AttributeError:
            pass
        except ImportError:  # pragma no cover
            logger.info('deleting module %s' % module.__name__)
            del sys.modules[module.__name__]
    for module in queue:  # pragma no cover
        reload(module)
        logger.info('Reloaded %s' % module.__name__)


def get_latest_version_infos(url, filename='data/.editolido.cfg.json'):
    infos = infos_from_giturl(url)
    jsonurl = raw_content_url(url, filename, branch_or_tag=infos['branch'])
    logger.info('downloading %s' % jsonurl)
    try:
        r = requests.get(jsonurl, verify=True, timeout=(3.1, 27))
        r.raise_for_status()
        data = r.json()
        r.close()
    except requests.HTTPError:
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
    return data


def log_local_version(version, branch=None):
    if branch:
        logger.info('local code version is %s' % version)
        try:
            local_infos = read_local_config()
        except IOError:
            logger.info('local branch status unknown, [%s] expected'
                        % branch)
        else:
            if branch == local_infos['branch_release']:
                logger.info('local branch is [%s]' % branch)
            else:
                logger.error('local branch is [%s] but [%s] expected'
                             % (local_infos['branch_release'], branch))
    else:
        logger.info('local version is %s' % version)


def log_fatal_error(message):
    logger.log(message)
    logger.log("Effacez le dossier editolido s'il existe.")
    logger.log("Redémarrez Editorial après l'avoir \"tué\"")
    logger.log("Recommencez et signalez le problème.")


def needs_update(local_infos, remote_infos):
    for k, v in remote_infos.items():
        if k in ('version', 'tag'):
            continue
        if v != local_infos[k]:
            return True

    if local_infos['version'] is None and remote_infos['version'] is None:
        if local_infos['tag'] == remote_infos['tag']:
            # same branch to same branch does not update
            return False

    if not local_infos['version']:
        return True
    elif not remote_infos['version']:
        return True
    if local_infos['version'] < remote_infos['version']:
        return True
    return False


def read_local_config():
    with open(get_local_config_filepath(), 'r') as fd:
        data = json.load(fd)
    if data.get('version', None):
        data['version'] = StrictVersion(data['version'])
    return data


# noinspection PyUnusedLocal
def update_editolido(url, *args, **kwargs):
    check_old_install()
    del args  # To avoid PyCharm complaining
    del kwargs  # used to keep signature always valid
    if not auto_update_is_set():
        logger.info('auto update is disabled')
    install_dir = get_install_dir()
    if url:
        params_infos = infos_from_giturl(url)
    else:
        params_infos, url = latest_release(url)
    branch = params_infos['branch_release']
    zipball_url = url
    try:
        local_infos = read_local_config()
    except IOError:
        logger.error('could not read %s' % get_local_config_filepath())
        local_infos, _ = latest_release(url)
        local_infos['version'] = StrictVersion(editolido.__version__)
        local_infos['tag'] = editolido.__version__
    infos = params_infos
    if branch:
        # it's a branch, no need to fetch remote data
        pass
    elif auto_update_is_set():
        try:
            data = get_latest_version_infos(url)
            try:
                json_url = data['url']
                json_infos = infos_from_giturl(json_url)
                if json_infos['version'] is None:
                    raise ValueError
            except (ValueError, AttributeError, KeyError):
                # either download is corrupt
                # or there is a mistake in the json file
                # so we ignore the json
                logger.error('json rejected: %s' % data)
            else:
                # if params_version greater than json_version
                # respect params_version (even if it is probably a typo)
                # otherwise use json
                if (params_infos['version'] and
                        json_infos['version'] > params_infos['version']):
                    infos = json_infos
                    zipball_url = json_url
        except requests.exceptions.RequestException:
            pass

    logger.info('remote version: %s' % infos['tag'])
    logger.info('remote zipball url: %s' % zipball_url)

    if not infos['tag'] or not infos['name']:
        logger.error('invalid url %s' % zipball_url)
        logger.info('local version is %s' % editolido.__version__)
    else:
        # download when local < remote
        # or when remote is a branch (master, beta...)
        if ((branch and auto_update_is_set()) or
                needs_update(local_infos, infos)):
            zipfolder = '%s-%s' % (infos['name'], infos['tag'])
            try:
                download_package(
                    zipball_url,
                    zipfolder,
                    install_dir,
                    name=infos['name'],
                )
            except requests.exceptions.RequestException:
                log_local_version(editolido.__version__,
                                  branch=local_infos['branch_release'])
            except (IOError, OSError):
                logger.error('attempted to install: %s' % zipball_url)
                logger.error('zipfolder: %s' % zipfolder)
                logger.error('install_dir: %s' % install_dir)
                logger.error('infos: %s' % infos)
                log_fatal_error('install failed')
                raise
            else:
                try:
                    reload_editolido(install_dir, infos['name'])
                except (ImportError, AttributeError, NameError):
                    logger.error('unable to reload editolido')
                    log_fatal_error('python error')
                try:
                    # noinspection PyPackageRequirements
                    import console  # in Editorial
                except ImportError:
                    from editolido.workflows.editorial.console import Console
                    console = Console(logger)
                save_local_config(infos)
                if branch:
                    logger.info('editolido [%s] %s installed'
                                % (branch, editolido.__version__))
                    console.hud_alert('editolido [%s] %s installé'
                                      % (branch, editolido.__version__))
                else:
                    logger.info('editolido module %s installed'
                                % editolido.__version__)
                    console.hud_alert('module editolido %s installé'
                                      % editolido.__version__)
        else:
            log_local_version(editolido.__version__, branch=branch)
