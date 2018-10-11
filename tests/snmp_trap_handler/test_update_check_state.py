import mock
import pytest

import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler
from tests.fakes import FakeLogger


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_services_for_host'
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_nagios_status',
    return_value='nagios status',
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'submit_passive_check_result'
)
def test_no_services(submit_result, get_status, get_services):
    logger = FakeLogger()

    message = 'themessage'
    trap_check_name = 'thetrapcheckname'
    instance = 'theinstance'

    get_services.return_value = []

    result = snmp_trap_handler.update_check_state(
        message=message,
        trap_check_name=trap_check_name,
        instance=instance,
        logger=logger,
    )

    assert result == 3

    assert logger.string_appears_in('warn',
                                    ('service', 'not found'))

    get_services.assert_called_once_with(instance, 'nagios status')


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_services_for_host'
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_nagios_status',
    return_value='nagios status',
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'submit_passive_check_result'
)
def test_only_wrong_services(submit_result, get_status, get_services):
    logger = FakeLogger()

    message = 'themessage'
    trap_check_name = 'thetrapcheckname'
    instance = 'theinstance'

    services = [
        {'service_description': 'notthis'},
        {'service_description': 'orthis'},
    ]
    get_services.return_value = services

    result = snmp_trap_handler.update_check_state(
        message=message,
        trap_check_name=trap_check_name,
        instance=instance,
        logger=logger,
    )

    assert result == 3

    for service in services:
        assert logger.string_appears_in(
            'debug',
            ('considering service', service['service_description']),
        )

    assert logger.string_appears_in('warn',
                                    ('service', 'not found'))

    get_services.assert_called_once_with(instance, 'nagios status')


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_services_for_host'
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_nagios_status',
    return_value='nagios status',
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'submit_passive_check_result'
)
def test_found_already_reacting(submit_result, get_status, get_services):
    logger = FakeLogger()

    message = 'themessage'
    trap_check_name = 'thetrapcheckname'
    instance = 'theinstance'

    services = [
        {'service_description': 'notthis'},
        {'service_description': trap_check_name,
         'current_state': '1'},
    ]
    get_services.return_value = services

    result = snmp_trap_handler.update_check_state(
        message=message,
        trap_check_name=trap_check_name,
        instance=instance,
        logger=logger,
    )

    assert result == 1

    assert logger.string_appears_in('debug', 'correct service found')
    assert logger.string_appears_in('warn', 'in progress')

    get_services.assert_called_once_with(instance, 'nagios status')


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_services_for_host'
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_nagios_status',
    return_value='nagios status',
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'submit_passive_check_result'
)
def test_found_already_notified(submit_result, get_status, get_services):
    logger = FakeLogger()

    message = 'themessage'
    trap_check_name = 'thetrapcheckname'
    instance = 'theinstance'

    services = [
        {'service_description': 'notthis'},
        {'service_description': trap_check_name,
         'current_state': '2'},
    ]
    get_services.return_value = services

    result = snmp_trap_handler.update_check_state(
        message=message,
        trap_check_name=trap_check_name,
        instance=instance,
        logger=logger,
    )

    assert result == 1

    assert logger.string_appears_in('debug', 'correct service found')
    assert logger.string_appears_in('warn', 'in progress')

    get_services.assert_called_once_with(instance, 'nagios status')


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_services_for_host'
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_nagios_status',
    return_value='nagios status',
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'submit_passive_check_result'
)
def test_not_yet_notified(submit_result, get_status, get_services):
    logger = FakeLogger()

    message = 'themessage'
    trap_check_name = 'thetrapcheckname'
    instance = 'theinstance'

    services = [
        {'service_description': trap_check_name,
         'current_state': '0'},
        {'service_description': 'notthis'},
    ]
    get_services.return_value = services

    result = snmp_trap_handler.update_check_state(
        message=message,
        trap_check_name=trap_check_name,
        instance=instance,
        logger=logger,
    )

    assert result == 0

    for expected in ('correct service found',
                     'submitting check',
                     'result submitted'):
        assert logger.string_appears_in('debug', expected)

    assert not logger.string_appears_in('warn', 'in progress')

    get_services.assert_called_once_with(instance, 'nagios status')
    submit_result.assert_called_once_with(
        host=instance,
        service=trap_check_name,
        status='2',
        output=message,
    )


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_services_for_host'
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'get_nagios_status',
    return_value='nagios status',
)
@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.'
    'submit_passive_check_result'
)
def test_notification_failure(submit_result, get_status, get_services):
    logger = FakeLogger()

    message = 'themessage'
    trap_check_name = 'thetrapcheckname'
    instance = 'theinstance'

    services = [
        {'service_description': trap_check_name,
         'current_state': '0'},
        {'service_description': 'notthis'},
    ]
    get_services.return_value = services

    submit_result.side_effect = RuntimeError

    with pytest.raises(RuntimeError):
        snmp_trap_handler.update_check_state(
            message=message,
            trap_check_name=trap_check_name,
            instance=instance,
            logger=logger,
        )

    for expected in ('correct service found',
                     'submitting check'):
        assert logger.string_appears_in('debug', expected)

    assert not logger.string_appears_in('warn', 'in progress')
