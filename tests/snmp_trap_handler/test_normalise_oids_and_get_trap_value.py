import mock
import pytest

import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler
from tests.fakes import FakeLogger, FakeOidLookup


def test_no_trap():
    logger = FakeLogger()
    lookups = {
        'system.sysUpTime.0': 'uptime',
    }
    oid_lookup = FakeOidLookup(lookups=lookups)

    raw_details = [
        {'raw_oid': 'system.sysUpTime.0', 'value': '1234'},
    ]

    result = snmp_trap_handler.normalise_oids_and_get_trap_value(
        raw_details=raw_details,
        oid_lookup=oid_lookup,
        logger=logger,
    )

    assert result == (None, {lookups['system.sysUpTime.0']: '1234'})

    assert not logger.string_appears_in('debug', 'trap identity')
    assert logger.string_appears_in('debug', ('uptime', '1234'))


def test_trap_in_details():
    logger = FakeLogger()
    lookups = {
        'system.sysUpTime.0': 'uptime',
        'enterprises.52312.900.0.0.1': 'cloudifything',
        snmp_trap_handler.SNMP_TRAP_OID: 'snmptrap',
        'snmp.1.1.4.1.0': 'snmptrap',
    }
    oid_lookup = FakeOidLookup(lookups=lookups)

    raw_details = [
        {'raw_oid': 'system.sysUpTime.0', 'value': '1234'},
        {'raw_oid': 'snmp.1.1.4.1.0', 'value': 'enterprises.52312.900.0.0.1'},
    ]

    result = snmp_trap_handler.normalise_oids_and_get_trap_value(
        raw_details=raw_details,
        oid_lookup=oid_lookup,
        logger=logger,
    )

    assert result == (
        'cloudifything',
        {
            lookups['system.sysUpTime.0']: '1234',
            lookups['snmp.1.1.4.1.0']: 'enterprises.52312.900.0.0.1',
        },
    )

    assert logger.string_appears_in('debug',
                                    ('trap identity', 'cloudifything'))
    assert logger.string_appears_in('debug', ('uptime', '1234'))


def test_pre_seed():
    logger = FakeLogger()
    oid_lookup = mock.Mock()
    oid_lookup.get.side_effect = RuntimeError

    raw_details = [
        {'raw_oid': 'system.sysUpTime.0', 'value': '1234'},
        {'raw_oid': 'snmp.1.1.4.1.0', 'value': 'enterprises.52312.900.0.0.1'},
    ]

    with pytest.raises(RuntimeError):
        snmp_trap_handler.normalise_oids_and_get_trap_value(
            raw_details=raw_details,
            oid_lookup=oid_lookup,
            logger=logger,
        )

    oid_lookup.get.assert_called_once_with([
        snmp_trap_handler.SNMP_TRAP_OID,
        'system.sysUpTime.0',
        'snmp.1.1.4.1.0',
    ])
