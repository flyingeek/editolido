# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six
import pytest
import mock

from editolido.workflows.lido2mapsme import lido2mapsme, lido2avenza, save_kml,\
    load_or_save, save_document, load_document, copy_lido_route
import editolido.constants as constants

filename = '{flight}_{departure}-{destination}_{date}_{datetime:%H:%M}z_' \
           'OFP_{ofp}.txt'

kml_params_all = {  # Pour tout afficher
    'Point Route': constants.PIN_PURPLE,
    'Repère NAT': constants.PIN_YELLOW,
    'Position repère': constants.NAT_POSITION_ENTRY,
    'Afficher NAT': True,
    'Afficher Ortho': True,
    'Afficher Ogimet': True,
    'Afficher Dégagement': True,
    'Point Dégagement': constants.PIN_PINK,
}


def test_lido2mapsme_output_is_kml(ofp_text):
    output = lido2mapsme(ofp_text, kml_params_all, debug=False)
    assert '<kml ' in output


def test_lido2avenza_output_is_kml(ofp_text):
    output = lido2avenza(ofp_text, kml_params_all, debug=False)
    assert '<kml ' in output


def test_load_document(mock_editor):
    mock_editor.get_file_contents.return_value = 'content éè'.encode('utf-8')
    out = load_document('', '')
    assert type(out) == six.text_type
    assert out == 'content éè'
    mock_editor.get_file_contents.return_value = None
    out = load_document('', '')
    assert type(out) == six.text_type
    assert out == ''


@pytest.mark.usefixtures('userdir')
def test_save_document(mock_editor, monkeypatch):
    monkeypatch.setattr('os.makedirs', lambda x: True)
    reldir = 'mydir/subdir/'
    name = 'filename / with slash'
    save_document('unicode éè', reldir, name)
    relpath, content = mock_editor.set_file_contents.call_args[0]
    basename = relpath.replace(reldir, '')
    assert basename == 'filename _ with slash'  # no more
    assert type(content) == six.binary_type


@pytest.mark.usefixtures('userdir')
@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize("content", ['', 'my content'])
def test_save_kml(ofp_text_or_empty, save, content, mock_editor):
    out = save_kml(content,
                   save=save,
                   reldir='mydir',
                   filename=filename,
                   workflow_in=ofp_text_or_empty)
    if content and save:
        mock_editor.set_file_contents.assert_called_once_with(
            mock.ANY, content.encode('utf-8'))
    else:
        assert not mock_editor.set_file_contents.called
    assert out == content


@pytest.mark.usefixtures('userdir', 'mock_console', 'mock_dialogs')
@pytest.mark.parametrize("save", [True, False])
def test_save(ofp_text, save, mock_editor):
    reldir = 'mydir'
    out = load_or_save(ofp_text,
                       save=save,
                       reldir=reldir,
                       filename=filename)
    if save:
        mock_editor.set_file_contents.assert_called_once_with(
            mock.ANY, ofp_text.encode('utf-8'))
    else:
        assert not mock_editor.called
    assert out == ofp_text


@pytest.mark.usefixtures('userdir', 'mock_console', 'mock_dialogs')
@pytest.mark.parametrize("save", [True, False])
def test_save_invalid_ofp(save, mock_editor, capsys):
    reldir = 'mydir'
    with pytest.raises(KeyboardInterrupt):
        load_or_save('invalid ofp',
                     save=save,
                     reldir=reldir,
                     filename=filename)
    mock_editor.set_file_contents.assert_called_once_with(
        reldir + '/_ofp_non_reconnu_.kml', 'invalid ofp'.encode('utf-8'))
    out, _ = capsys.readouterr()
    assert out


@pytest.mark.usefixtures('userdir', 'mock_dialogs')
@pytest.mark.parametrize("save", [True, False])
def test_load_no_backup(save, mock_editor, mock_console, monkeypatch):
    monkeypatch.setattr('os.listdir', lambda x: False)
    reldir = 'mydir'
    with pytest.raises(KeyboardInterrupt):
        load_or_save('',
                     save=save,
                     reldir=reldir,
                     filename=filename)
    assert not mock_editor.set_file_contents.called
    assert mock_console.alert.called


@pytest.mark.usefixtures('userdir')
@pytest.mark.parametrize("save", [True, False])
def test_load_with_backup_aborted_dialog(save, mock_editor, mock_console,
                                         mock_dialogs, monkeypatch,
                                         ofp_testfiles):
    monkeypatch.setattr('os.listdir', lambda x: ofp_testfiles)
    mock_dialogs.list_dialog.return_value = False
    with pytest.raises(KeyboardInterrupt):
        load_or_save('',
                     save=save,
                     reldir='mydir',
                     filename=filename)
    assert not mock_editor.set_file_contents.called
    assert not mock_console.alert.called
    assert mock_dialogs.list_dialog.called
    assert not mock_editor.get_file_contents.called


@pytest.mark.usefixtures('userdir')
@pytest.mark.parametrize("save", [True, False])
def test_load_with_backup(save, mock_editor, mock_console,
                          mock_dialogs, monkeypatch, ofp_testfiles):
    monkeypatch.setattr('os.listdir', lambda x: ofp_testfiles)
    choice = ofp_testfiles[0]
    reldir = 'mydir'
    mock_dialogs.list_dialog.return_value = choice
    load_or_save('',
                 save=save,
                 reldir=reldir,
                 filename=filename)
    assert not mock_editor.set_file_contents.called
    assert not mock_console.alert.called
    assert mock_dialogs.list_dialog.called
    assert mock_editor.get_file_contents.called_once_with(reldir, choice)


@pytest.mark.parametrize("copy", [True, False])
def test_copy_lido_route(ofp_text, copy, mock_clipboard, mock_console):
    params = {
        'Copier': copy,
        'Durée': 1,
        'Notification': 'notification'
    }
    out = copy_lido_route(ofp_text, params)
    assert out == ofp_text
    if copy:
        assert mock_clipboard.set.called
        assert mock_console.hud_alert.called
