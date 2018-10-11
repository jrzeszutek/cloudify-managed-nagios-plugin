import mock

import tests.links.update_notify_cloudify_configuration as update_config


@mock.patch('tests.links.update_notify_cloudify_configuration.run')
def test_copy_cert(run):
    expected_source_path = 'thepathwewant'
    config = {
        'something': 'yes',
        'local_rest_cert_file': expected_source_path,
        'other': 'no',
    }

    update_config.copy_ssl_cert(config)

    run_args = run.call_args_list[0][0][0]

    assert expected_source_path in run_args
    assert update_config.NOTIFY_PLUGIN_CERT in run_args
