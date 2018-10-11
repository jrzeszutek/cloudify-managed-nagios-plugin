import mock

import nagios_plugin_utils
from tests.fakes import FakeLogger


@mock.patch('nagios_plugin_utils.sys.exit')
@mock.patch('nagios_plugin_utils.print')
def test_no_thresholds(mock_print, exit):
    logger = FakeLogger()
    low_warning = ""
    low_critical = ""
    high_warning = ""
    high_critical = ""

    result = nagios_plugin_utils.validate_and_structure_thresholds(
        low_warning, low_critical,
        high_warning, high_critical,
        logger,
    )

    assert result['low']['warning'] == low_warning
    assert result['low']['critical'] == low_critical
    assert result['high']['warning'] == high_warning
    assert result['high']['critical'] == high_critical

    assert mock_print.call_count == 0
    assert exit.call_count == 0


@mock.patch('nagios_plugin_utils.sys.exit')
@mock.patch('nagios_plugin_utils.print')
def test_values(mock_print, exit):
    logger = FakeLogger()
    low_warning = 10.4
    low_critical = 16.6
    high_warning = 80.1
    high_critical = 90.2

    result = nagios_plugin_utils.validate_and_structure_thresholds(
        low_warning, low_critical,
        high_warning, high_critical,
        logger,
    )

    assert result['low']['warning'] == low_warning
    assert result['low']['critical'] == low_critical
    assert result['high']['warning'] == high_warning
    assert result['high']['critical'] == high_critical

    assert mock_print.call_count == 0
    assert exit.call_count == 0


@mock.patch('nagios_plugin_utils.sys.exit')
@mock.patch('nagios_plugin_utils.print')
def test_low_higher_than_high(mock_print, exit):
    logger = FakeLogger()
    low_warning = 42
    low_critical = 42
    high_warning = 32
    high_critical = 32

    nagios_plugin_utils.validate_and_structure_thresholds(
        low_warning, low_critical,
        high_warning, high_critical,
        logger,
    )

    mock_print_arg = mock_print.call_args_list[0][0][0]
    assert 'must be higher' in mock_print_arg
    logger.string_appears_in('error', 'must be higher')

    exit.assert_called_once_with(nagios_plugin_utils.STATUS_UNKNOWN)
