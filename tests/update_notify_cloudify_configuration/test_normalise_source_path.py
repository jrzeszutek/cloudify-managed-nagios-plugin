import tests.links.update_notify_cloudify_configuration as update_config


def test_not_cluster():
    expected_result = '/path/to/thefilename'

    result = update_config.normalise_source_path(expected_result)

    assert result == expected_result


def test_cluster():
    expected_result = '/path/to/thefilename'
    input_string = '/path/to/cluster-thefilename'

    result = update_config.normalise_source_path(input_string)

    assert result == expected_result
