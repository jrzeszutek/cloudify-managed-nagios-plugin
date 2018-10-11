import pytest

import nagios_plugin_utils


def test_empty():
    expected = ""
    value = ""

    result = nagios_plugin_utils.float_or_empty(value)

    assert result == expected


def test_integer_becomes_float():
    expected = 1.0
    value = "1"

    result = nagios_plugin_utils.float_or_empty(value)

    assert result == expected


def test_float():
    expected = 5.3
    value = "5.3"

    result = nagios_plugin_utils.float_or_empty(value)

    assert result == expected


def test_none():
    value = None

    with pytest.raises(TypeError):
        nagios_plugin_utils.float_or_empty(value)


def test_badinput():
    value = "six"

    with pytest.raises(ValueError):
        nagios_plugin_utils.float_or_empty(value)
