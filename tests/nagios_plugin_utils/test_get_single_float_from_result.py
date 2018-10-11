import nagios_plugin_utils


def test_get_one_float():
    input_data = 'SNMP OK - 4.2 | perfdata\n'
    expected = 4.2

    result = nagios_plugin_utils.get_single_float_from_result(input_data)

    assert result == expected


def test_do_not_get_multiple_floats():
    input_data = 'SNMP OK - 4.2 6.1 | perfdata\n'
    expected = 4.2

    result = nagios_plugin_utils.get_single_float_from_result(input_data)

    assert result == expected
