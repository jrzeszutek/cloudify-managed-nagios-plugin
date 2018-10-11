import re

import mock
import pytest

import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler
from tests.fakes import FakeLogger, FakeOidLookup

CONF_PATH = 'tests/snmp_trap_handler/resources/actions/{oid}.json'
snmp_trap_handler.TRAP_CONFIG_PATH = CONF_PATH


def test_missing_action():
    logger = FakeLogger()
    config_name = 'missing'

    result = snmp_trap_handler.determine_action(
        oid=config_name,
        oid_lookup=mock.Mock(),
        logger=logger,
    )

    assert result is None

    expected_path = CONF_PATH.format(oid=config_name)
    assert logger.string_appears_in('debug', expected_path)

    assert 'not found' in logger.messages['warn'][-1]


def test_empty_action():
    logger = FakeLogger()
    config_name = 'empty'

    with pytest.raises(ValueError):
        snmp_trap_handler.determine_action(
            oid=config_name,
            oid_lookup=mock.Mock(),
            logger=logger,
        )

    expected_path = CONF_PATH.format(oid=config_name)
    assert logger.string_appears_in('debug', expected_path)

    assert 'not' in logger.messages['exception'][-1]
    assert 'JSON' in logger.messages['exception'][-1]
    assert 'empty' in logger.messages['exception'][-1]


def test_broken_instance():
    logger = FakeLogger()
    config_name = 'broken_instance'

    with pytest.raises(KeyError):
        snmp_trap_handler.determine_action(
            oid=config_name,
            oid_lookup=mock.Mock(),
            logger=logger,
        )

    expected_path = CONF_PATH.format(oid=config_name)
    assert logger.string_appears_in('debug', expected_path)

    assert logger.string_appears_in('debug', 'loading instance')


def test_just_instance():
    logger = FakeLogger()
    config_name = 'just_instance'
    oid_lookup = FakeOidLookup(default='looked_up_oid')

    result = snmp_trap_handler.determine_action(
        oid=config_name,
        oid_lookup=oid_lookup,
        logger=logger,
    )

    expected_path = CONF_PATH.format(oid=config_name)
    assert logger.string_appears_in('debug', expected_path)

    assert logger.string_appears_in('debug', 'loading instance')
    assert not logger.string_appears_in('debug', 'loading oid_for_message')

    assert result['instance']['oid'] == 'looked_up_oid'
    # This is expected to be a regex
    assert result['instance']['finder'] == re.compile(u'testregex')


def test_just_oid_for_message():
    logger = FakeLogger()
    config_name = 'just_oid_for_message'
    oid_lookup = FakeOidLookup(default='looked_up_message_oid')

    result = snmp_trap_handler.determine_action(
        oid=config_name,
        oid_lookup=oid_lookup,
        logger=logger,
    )

    expected_path = CONF_PATH.format(oid=config_name)
    assert logger.string_appears_in('debug', expected_path)

    assert not logger.string_appears_in('debug', 'loading instance')
    assert logger.string_appears_in('debug', 'loading oid_for_message')

    assert result['oid_for_message'] == 'looked_up_message_oid'


def test_oid_for_message_and_instance():
    logger = FakeLogger()
    config_name = 'instance_and_message_oid'
    lookups = {
        'instanceoid': 'lookedupinstance',
        'messageoid': 'lookedupmessage',
    }
    oid_lookup = FakeOidLookup(lookups=lookups)

    result = snmp_trap_handler.determine_action(
        oid=config_name,
        oid_lookup=oid_lookup,
        logger=logger,
    )

    expected_path = CONF_PATH.format(oid=config_name)
    assert logger.string_appears_in('debug', expected_path)

    assert logger.string_appears_in('debug', 'loading instance')
    assert logger.string_appears_in('debug', 'loading oid_for_message')

    assert result['instance'] == {
        'oid': lookups['instanceoid'],
        'finder': re.compile(u'testfinder'),
    }
    assert result['oid_for_message'] == lookups['messageoid']


def test_instance_oid_lookup_exception():
    logger = FakeLogger()
    config_name = 'just_instance'
    oid_lookup = mock.Mock()
    oid_lookup.get.side_effect = RuntimeError

    with pytest.raises(RuntimeError):
        snmp_trap_handler.determine_action(
            oid=config_name,
            oid_lookup=oid_lookup,
            logger=logger,
        )

    expected_path = CONF_PATH.format(oid=config_name)
    assert logger.string_appears_in('debug', expected_path)

    assert logger.string_appears_in('debug', 'loading instance')


def test_oid_for_message_lookup_exception():
    logger = FakeLogger()
    config_name = 'just_oid_for_message'
    oid_lookup = mock.Mock()
    oid_lookup.get.side_effect = RuntimeError

    with pytest.raises(RuntimeError):
        snmp_trap_handler.determine_action(
            oid=config_name,
            oid_lookup=oid_lookup,
            logger=logger,
        )

    expected_path = CONF_PATH.format(oid=config_name)
    assert logger.string_appears_in('debug', expected_path)

    assert logger.string_appears_in('debug', 'loading oid_for_message')
