import mock
import pytest

import nagios_plugin_utils


@mock.patch('nagios_plugin_utils.output_and_exit',
            side_effect=SystemExit)
def test_no_thresholds(output_and_exit):
    value = 42
    perfdata = 'abc123'
    rate_check = 'ignored'
    thresholds = {
        'high': {
            'warning': "",
            'critical': "",
        },
        'low': {
            'warning': "",
            'critical': "",
        },
    }

    with pytest.raises(SystemExit):
        nagios_plugin_utils.check_thresholds_and_exit(value, thresholds,
                                                      perfdata, rate_check)

    output_and_exit.assert_called_once_with(
        value, perfdata, 'OK', None, rate_check, False,
    )


@mock.patch('nagios_plugin_utils.output_and_exit',
            side_effect=SystemExit)
def test_low_warning(output_and_exit):
    value = 42
    perfdata = 'abc123'
    rate_check = 'ignored'
    thresholds = {
        'high': {
            'warning': "",
            'critical': "",
        },
        'low': {
            'warning': 50,
            'critical': "",
        },
    }

    with pytest.raises(SystemExit):
        nagios_plugin_utils.check_thresholds_and_exit(value, thresholds,
                                                      perfdata, rate_check)

    output_and_exit.assert_called_once_with(
        value, perfdata, 'WARNING', 'LOW', rate_check, False,
    )


@mock.patch('nagios_plugin_utils.output_and_exit',
            side_effect=SystemExit)
def test_low_critical(output_and_exit):
    value = 42
    perfdata = 'abc123'
    rate_check = 'ignored'
    thresholds = {
        'high': {
            'warning': "",
            'critical': "",
        },
        'low': {
            'warning': 50,
            'critical': 45,
        },
    }

    with pytest.raises(SystemExit):
        nagios_plugin_utils.check_thresholds_and_exit(value, thresholds,
                                                      perfdata, rate_check)

    output_and_exit.assert_called_once_with(
        value, perfdata, 'CRITICAL', 'LOW', rate_check, False,
    )


@mock.patch('nagios_plugin_utils.output_and_exit',
            side_effect=SystemExit)
def test_high_warning(output_and_exit):
    value = 42
    perfdata = 'abc123'
    rate_check = 'ignored'
    thresholds = {
        'high': {
            'warning': 30,
            'critical': "",
        },
        'low': {
            'warning': "",
            'critical': "",
        },
    }

    with pytest.raises(SystemExit):
        nagios_plugin_utils.check_thresholds_and_exit(value, thresholds,
                                                      perfdata, rate_check)

    output_and_exit.assert_called_once_with(
        value, perfdata, 'WARNING', 'HIGH', rate_check, False,
    )


@mock.patch('nagios_plugin_utils.output_and_exit',
            side_effect=SystemExit)
def test_high_critical(output_and_exit):
    value = 42
    perfdata = 'abc123'
    rate_check = 'ignored'
    thresholds = {
        'high': {
            'warning': 30,
            'critical': 15,
        },
        'low': {
            'warning': "",
            'critical': "",
        },
    }

    with pytest.raises(SystemExit):
        nagios_plugin_utils.check_thresholds_and_exit(value, thresholds,
                                                      perfdata, rate_check)

    output_and_exit.assert_called_once_with(
        value, perfdata, 'CRITICAL', 'HIGH', rate_check, False,
    )
