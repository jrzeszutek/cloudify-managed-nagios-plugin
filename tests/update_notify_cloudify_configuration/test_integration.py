from copy import deepcopy
import json

import mock

from tests.fakes import FakeOpener
import tests.links.update_notify_cloudify_configuration as update_config

EXPECTED_CONFIG = {
    'rest_host': 'something',
    'cluster': [],
    'rest_port': 1234,
}
EXPECTED_CERT_PATH = 'somecertpath'
INPUT_DATA = deepcopy(EXPECTED_CONFIG)
INPUT_DATA['local_rest_cert_file'] = EXPECTED_CERT_PATH
INPUT_DATA = json.dumps(INPUT_DATA)


@mock.patch('tests.links.update_notify_cloudify_configuration.json')
@mock.patch('tests.links.update_notify_cloudify_configuration.run')
def test_non_cluster(run, mock_json):
    mock_json.load = json.load
    config_path = '/path/to/theconfig'

    opener = FakeOpener(INPUT_DATA)
    update_config.open = opener.open

    update_config.main(config_path)

    assert opener.read_paths == [config_path]
    assert opener.write_paths == [update_config.NOTIFY_PLUGIN_CONFIG]

    mock_json.dump.assert_called_once_with(
        fp=opener,
        obj=EXPECTED_CONFIG,
    )

    chown_calls = [
        call[0][0] for call in run.call_args_list
        if 'chown' in call[0][0]
    ]
    chmod_calls = [
        call[0][0] for call in run.call_args_list
        if 'chmod' in call[0][0]
    ]
    cp_calls = [
        call[0][0] for call in run.call_args_list
        if 'cp' in call[0][0]
    ]

    for path in (update_config.NOTIFY_PLUGIN_CERT,
                 update_config.NOTIFY_PLUGIN_CONFIG):
        assert any(path in call for call in chown_calls)
        assert any(path in call for call in chmod_calls
                   if '440' in call)

    assert len(cp_calls) == 1
    assert EXPECTED_CERT_PATH in cp_calls[0]
    assert update_config.NOTIFY_PLUGIN_CERT in cp_calls[0]


@mock.patch('tests.links.update_notify_cloudify_configuration.json')
@mock.patch('tests.links.update_notify_cloudify_configuration.run')
def test_cluster(run, mock_json):
    mock_json.load = json.load
    config_path = '/path/to/cluster-theconfig'
    expected_config_path = '/path/to/theconfig'

    opener = FakeOpener(INPUT_DATA)
    update_config.open = opener.open

    update_config.main(config_path)

    assert opener.read_paths == [expected_config_path]
    assert opener.write_paths == [update_config.NOTIFY_PLUGIN_CONFIG]

    mock_json.dump.assert_called_once_with(
        fp=opener,
        obj=EXPECTED_CONFIG,
    )

    chown_calls = [
        call[0][0] for call in run.call_args_list
        if 'chown' in call[0][0]
    ]
    chmod_calls = [
        call[0][0] for call in run.call_args_list
        if 'chmod' in call[0][0]
    ]
    cp_calls = [
        call[0][0] for call in run.call_args_list
        if 'cp' in call[0][0]
    ]

    for path in (update_config.NOTIFY_PLUGIN_CERT,
                 update_config.NOTIFY_PLUGIN_CONFIG):
        assert any(path in call for call in chown_calls)
        assert any(path in call for call in chmod_calls
                   if '440' in call)

    assert len(cp_calls) == 1
    assert EXPECTED_CERT_PATH in cp_calls[0]
    assert update_config.NOTIFY_PLUGIN_CERT in cp_calls[0]
