import pytest

import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler
from tests.fakes import FakeLogger

CONF_PATH = 'tests/snmp_trap_handler/resources/reactions/{target_type}.json'
snmp_trap_handler.REACTION_CONFIG_PATH = CONF_PATH


def test_missing_action():
    logger = FakeLogger()
    target_type = 'missing'
    trap_value = 'sometrap'

    result = snmp_trap_handler.determine_reaction(
        target_type=target_type,
        trap_value=trap_value,
        logger=logger,
    )

    assert result is None

    expected_path = CONF_PATH.format(target_type=target_type)
    assert logger.string_appears_in('debug', expected_path)

    assert 'not found' in logger.messages['warn'][-1]


def test_empty_action():
    logger = FakeLogger()
    target_type = 'empty'
    trap_value = 'sometrap'

    with pytest.raises(ValueError):
        snmp_trap_handler.determine_reaction(
            target_type=target_type,
            trap_value=trap_value,
            logger=logger,
        )

    expected_path = CONF_PATH.format(target_type=target_type)
    assert logger.string_appears_in('debug', expected_path)

    assert 'not' in logger.messages['exception'][-1]
    assert 'JSON' in logger.messages['exception'][-1]
    assert 'empty' in logger.messages['exception'][-1]


def test_reaction_found():
    logger = FakeLogger()
    target_type = 'onetrap'
    trap_value = 'test_trap'

    result = snmp_trap_handler.determine_reaction(
        target_type=target_type,
        trap_value=trap_value,
        logger=logger,
    )

    expected_path = CONF_PATH.format(target_type=target_type)
    assert logger.string_appears_in('debug', expected_path)

    assert logger.string_appears_in('debug', 'loading reaction')

    assert result == 'expectedreaction'


def test_no_reaction_found():
    logger = FakeLogger()
    target_type = 'notrap'
    trap_value = 'test_trap'

    result = snmp_trap_handler.determine_reaction(
        target_type=target_type,
        trap_value=trap_value,
        logger=logger,
    )

    expected_path = CONF_PATH.format(target_type=target_type)
    assert logger.string_appears_in('debug', expected_path)

    assert logger.string_appears_in('debug', 'loading reaction')

    assert result is None


def test_missing_traps():
    logger = FakeLogger()
    target_type = 'missingtraps'
    trap_value = 'test_trap'

    with pytest.raises(KeyError):
        snmp_trap_handler.determine_reaction(
            target_type=target_type,
            trap_value=trap_value,
            logger=logger,
        )

    expected_path = CONF_PATH.format(target_type=target_type)
    assert logger.string_appears_in('debug', expected_path)

    assert logger.string_appears_in('debug', 'loading reaction')
