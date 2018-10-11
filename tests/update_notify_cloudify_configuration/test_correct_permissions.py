import mock

import tests.links.update_notify_cloudify_configuration as update_config


@mock.patch('tests.links.update_notify_cloudify_configuration.run')
def test_correct_permissions(run):
    update_config.correct_permissions()

    chown_calls = [
        call[0][0] for call in run.call_args_list
        if 'chown' in call[0][0]
    ]
    chmod_calls = [
        call[0][0] for call in run.call_args_list
        if 'chmod' in call[0][0]
    ]

    for path in (update_config.NOTIFY_PLUGIN_CERT,
                 update_config.NOTIFY_PLUGIN_CONFIG):
        assert any(path in call for call in chown_calls)
        assert any(path in call for call in chmod_calls
                   if '440' in call)
