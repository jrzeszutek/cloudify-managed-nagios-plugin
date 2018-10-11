import mock

from tests.fakes import FakeOpener
import tests.links.update_notify_cloudify_configuration as update_config


@mock.patch('tests.links.update_notify_cloudify_configuration.json')
def test_save(mock_json):
    opener = FakeOpener()
    update_config.open = opener.open

    config = {'someconfig': 'yes'}

    update_config.save_config(config)

    assert opener.write_paths == [update_config.NOTIFY_PLUGIN_CONFIG]

    mock_json.dump.assert_called_once_with(
        fp=opener,
        obj=config,
    )
