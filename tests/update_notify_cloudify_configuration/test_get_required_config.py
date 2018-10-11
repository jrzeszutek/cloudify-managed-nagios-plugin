from copy import deepcopy

import tests.links.update_notify_cloudify_configuration as update_config


def test_config_values_present():
    expected_config = {
        'cluster': 'something',
        'rest_host': 'other',
        'rest_port': 'another',
    }

    input_config = deepcopy(expected_config)
    input_config['another_key'] = 'shouldbemissing'

    result = update_config.get_required_config(input_config)

    assert result == expected_config


def test_missing_values_no_error():
    expected_config = {
        'cluster': None,
        'rest_host': None,
        'rest_port': None,
    }

    input_config = {}

    result = update_config.get_required_config(input_config)

    assert result == expected_config
