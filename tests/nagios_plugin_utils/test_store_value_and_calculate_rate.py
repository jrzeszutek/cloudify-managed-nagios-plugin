import mock
import pytest

import nagios_plugin_utils
from tests.fakes import FakeOpener, FakeLogger


@mock.patch('nagios_plugin_utils.run')
@mock.patch('nagios_plugin_utils.time.time')
@mock.patch('nagios_plugin_utils.sys.exit',
            side_effect=SystemExit)
@mock.patch('nagios_plugin_utils.print')
def test_ioerror_opening_previous(mock_print, mock_exit, mock_time, run):
    mock_time.return_value = 100
    logger = FakeLogger()

    value = 42
    path = 'something'

    opener = FakeOpener(read_error=IOError)
    opener.write = mock.Mock()
    nagios_plugin_utils.open = opener.open

    with pytest.raises(SystemExit):
        nagios_plugin_utils.store_value_and_calculate_rate(
            logger, value, path,
        )

    mock_print_arg = mock_print.call_args_list[0][0][0].lower()
    assert 'could not open' in mock_print_arg
    assert 'previous' in mock_print_arg

    mock_exit.assert_called_once_with(nagios_plugin_utils.STATUS_UNKNOWN)


@mock.patch('nagios_plugin_utils.run')
@mock.patch('nagios_plugin_utils.time.time')
@mock.patch('nagios_plugin_utils.sys.exit',
            side_effect=SystemExit)
@mock.patch('nagios_plugin_utils.print')
def test_valueerror_opening_previous(mock_print, mock_exit, mock_time, run):
    mock_time.return_value = 100
    logger = FakeLogger()

    value = 42
    path = 'something'

    opener = FakeOpener(read_error=ValueError)
    opener.write = mock.Mock()
    nagios_plugin_utils.open = opener.open

    with pytest.raises(SystemExit):
        nagios_plugin_utils.store_value_and_calculate_rate(
            logger, value, path,
        )

    mock_print_arg = mock_print.call_args_list[0][0][0].lower()
    assert 'previous data' in mock_print_arg
    assert 'unknown' in mock_print_arg
    assert 'cannot calculate' in mock_print_arg

    mock_exit.assert_called_once_with(nagios_plugin_utils.STATUS_UNKNOWN)


@mock.patch('nagios_plugin_utils.json')
@mock.patch('nagios_plugin_utils.run')
@mock.patch('nagios_plugin_utils.time.time')
@mock.patch('nagios_plugin_utils.sys.exit',
            side_effect=SystemExit)
@mock.patch('nagios_plugin_utils.print')
def test_incomplete_opening_previous(mock_print, mock_exit, mock_time, run,
                                     mock_json):
    mock_time.return_value = 100
    logger = FakeLogger()

    value = 42
    path = 'something'

    opener = FakeOpener()
    opener.write = mock.Mock()
    nagios_plugin_utils.open = opener.open

    mock_json.load.return_value = {}

    with pytest.raises(SystemExit):
        nagios_plugin_utils.store_value_and_calculate_rate(
            logger, value, path,
        )

    mock_print_arg = mock_print.call_args_list[0][0][0].lower()
    assert 'previous' in mock_print_arg
    assert 'incomplete' in mock_print_arg
    assert 'cannot calculate' in mock_print_arg

    mock_exit.assert_called_once_with(nagios_plugin_utils.STATUS_UNKNOWN)


@mock.patch('nagios_plugin_utils.json')
@mock.patch('nagios_plugin_utils.run')
@mock.patch('nagios_plugin_utils.time.time')
@mock.patch('nagios_plugin_utils.sys.exit',
            side_effect=SystemExit)
@mock.patch('nagios_plugin_utils.print')
def test_too_fast(mock_print, mock_exit, mock_time, run, mock_json):
    mock_time.return_value = 100
    logger = FakeLogger()

    value = 42
    path = 'something'

    opener = FakeOpener()
    opener.write = mock.Mock()
    nagios_plugin_utils.open = opener.open

    mock_json.load.return_value = {
        'timestamp': 100,
        'result': 52,
    }

    with pytest.raises(SystemExit):
        nagios_plugin_utils.store_value_and_calculate_rate(
            logger, value, path,
        )

    mock_print_arg = mock_print.call_args_list[0][0][0].lower()
    assert 'too recently' in mock_print_arg
    assert 'cannot calculate' in mock_print_arg

    mock_exit.assert_called_once_with(nagios_plugin_utils.STATUS_UNKNOWN)


@mock.patch('nagios_plugin_utils.json')
@mock.patch('nagios_plugin_utils.run')
@mock.patch('nagios_plugin_utils.time.time')
@mock.patch('nagios_plugin_utils.sys.exit',
            side_effect=SystemExit)
@mock.patch('nagios_plugin_utils.print')
def test_get_good_rate(mock_print, mock_exit, mock_time, run, mock_json):
    mock_time.return_value = 100
    logger = FakeLogger()

    value = 42
    path = 'something'

    opener = FakeOpener()
    opener.write = mock.Mock()
    nagios_plugin_utils.open = opener.open

    mock_json.load.return_value = {
        'timestamp': 90,
        'result': 32,
    }

    expected = 1.0

    result = nagios_plugin_utils.store_value_and_calculate_rate(
        logger, value, path,
    )

    assert mock_exit.call_count == 0
    assert mock_print.call_count == 0

    assert result == expected
