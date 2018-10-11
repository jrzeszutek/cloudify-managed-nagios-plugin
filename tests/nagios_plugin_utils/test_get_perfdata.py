import nagios_plugin_utils


def test_get_perfdata():
    input_data = 'something | this | is | it\n'
    expected = ' this | is | it'

    perfdata = nagios_plugin_utils.get_perfdata(input_data)

    assert perfdata == expected
