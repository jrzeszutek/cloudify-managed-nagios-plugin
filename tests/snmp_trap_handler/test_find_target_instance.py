import re

import mock
import pytest

import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler
from tests.fakes import FakeLogger


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.get_host_name_from_address'
)
def test_instance_finder_gives_name(get_host_name):
    logger = FakeLogger()

    expected_name = 'thename'

    action = {
        'instance': {
            'finder': re.compile("^(?P<name>[a-z]+)$"),
            'oid': 'something',
        },
    }

    details = {
        'something': expected_name,
        'unimportant': 'notthis',
    }

    result = snmp_trap_handler.find_target_instance(
        action=action,
        details=details,
        message_source='notimportant',
        logger=logger,
    )

    assert result == expected_name

    assert not logger.string_appears_in('debug', ('look up', 'name'))
    assert logger.string_appears_in('debug', 'details finder found')


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.get_host_name_from_address'
)
def test_instance_finder_address_can_find_name(get_host_name):
    logger = FakeLogger()

    expected_name = 'thename'

    action = {
        'instance': {
            'finder': re.compile("^(?P<address>[a-z]+)$"),
            'oid': 'something',
        },
    }

    details = {
        'something': 'anything',
        'unimportant': 'notthis',
    }

    get_host_name.return_value = expected_name

    result = snmp_trap_handler.find_target_instance(
        action=action,
        details=details,
        message_source='notimportant',
        logger=logger,
    )

    assert result == expected_name

    assert logger.string_appears_in('debug', ('look up', 'name'))
    assert logger.string_appears_in('debug', 'details finder found')


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.get_host_name_from_address'
)
def test_instance_finder_address_cannot_find_name(get_host_name):
    logger = FakeLogger()

    action = {
        'instance': {
            'finder': re.compile("^(?P<address>[a-z]+)$"),
            'oid': 'something',
        },
    }

    details = {
        'something': 'anything',
        'unimportant': 'notthis',
    }

    get_host_name.return_value = None

    with pytest.raises(snmp_trap_handler.MonitoredHostNotFoundError):
        snmp_trap_handler.find_target_instance(
            action=action,
            details=details,
            message_source='notimportant',
            logger=logger,
        )

    assert logger.string_appears_in('debug', ('look up', 'name'))
    assert logger.string_appears_in('debug', 'details finder found')
    assert logger.string_appears_in('error', 'no host found')


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.get_host_name_from_address'
)
def test_instance_finder_oid_not_present(get_host_name):
    logger = FakeLogger()

    action = {
        'instance': {
            'finder': re.compile("^(?P<address>[a-z]+)$"),
            'oid': 'missing',
        },
    }

    details = {
        'something': 'anything',
        'unimportant': 'notthis',
    }

    get_host_name.return_value = None

    with pytest.raises(snmp_trap_handler.MonitoredHostNotFoundError):
        snmp_trap_handler.find_target_instance(
            action=action,
            details=details,
            message_source='notimportant',
            logger=logger,
        )

    assert logger.string_appears_in('error', ('oid', 'not found'))


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.get_host_name_from_address'
)
def test_no_instance_finder_can_find_name(get_host_name):
    logger = FakeLogger()

    expected_name = 'thename'
    source_address = 'thesource'

    action = {}

    details = {
        'unimportant': 'notthis',
    }

    get_host_name.return_value = expected_name

    result = snmp_trap_handler.find_target_instance(
        action=action,
        details=details,
        message_source=source_address,
        logger=logger,
    )

    assert result == expected_name

    assert logger.string_appears_in('debug', ('look up', 'name'))
    assert not logger.string_appears_in('debug', 'details finder found')

    get_host_name.assert_called_once_with(source_address)


@mock.patch(
    'tests.links.'
    'cloudify_nagios_snmp_trap_handler.'
    'nagios_utils.get_host_name_from_address'
)
def test_no_instance_finder_cannot_find_name(get_host_name):
    logger = FakeLogger()

    source_address = 'thesource'

    action = {}

    details = {
        'unimportant': 'notthis',
    }

    get_host_name.return_value = None

    with pytest.raises(snmp_trap_handler.MonitoredHostNotFoundError):
        snmp_trap_handler.find_target_instance(
            action=action,
            details=details,
            message_source=source_address,
            logger=logger,
        )

    assert logger.string_appears_in('debug', ('look up', 'name'))
    assert not logger.string_appears_in('debug', 'details finder found')
    assert logger.string_appears_in('error', 'no host found')

    get_host_name.assert_called_once_with(source_address)
