from copy import deepcopy

import mock

import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler
from tests.fakes import FakeLogger, FakeOidLookup, FakeStdin


REACT_PATH = 'tests/snmp_trap_handler/resources/reactions/{target_type}.json'
ACT_PATH = 'tests/snmp_trap_handler/resources/actions/{oid}.json'
snmp_trap_handler.REACTION_CONFIG_PATH = REACT_PATH
snmp_trap_handler.TRAP_CONFIG_PATH = ACT_PATH

BASIC_NOTIFICATION_TRAP_VALUE = 'enterprises.52312.900.0.0.1'
VERBOSE_NOTIFICATION_TRAP_VALUE = 'enterprises.52312.900.0.0.2'
NOTIFICATION_SOURCE = '192.0.2.26'
VERBOSE_SOURCE = 'thetruesource'
BASIC_NOTIFICATION = [
    'Myhost',
    'UDP: [{source}]:58628->[192.0.2.214]:162'.format(
        source=NOTIFICATION_SOURCE,
    ),
    'system.sysUpTime.0 1234',
    'snmp.1.1.4.1.0 {trap_value}'.format(
        trap_value=BASIC_NOTIFICATION_TRAP_VALUE,
    ),
]
VERBOSE_NOTIFICATION = [
    'Myhost',
    'UDP: [{source}]:58628->[192.0.2.214]:162'.format(
        source=NOTIFICATION_SOURCE,
    ),
    'system.sysUpTime.0 1234',
    'snmp.1.1.4.1.0 {trap_value}'.format(
        trap_value=VERBOSE_NOTIFICATION_TRAP_VALUE,
    ),
    'enterprises.52312.900.0.1.1 Testmessage',
    'enterprises.52312.900.0.1.2 12345{node_address}12345'.format(
        node_address=VERBOSE_SOURCE,
    ),
    'enterprises.52312.900.0.1.3 Some information you do not care about',
]

BASE_LOOKUPS = {
    'system.sysUpTime.0': 'uptime',
    snmp_trap_handler.SNMP_TRAP_OID: 'snmptrap',
    'snmp.1.1.4.1.0': 'snmptrap',
    'enterprises.52312.900.0.1.1': 'message',
    'enterprises.52312.900.0.1.2': 'node',
    'enterprises.52312.900.0.1.3': 'other',
}


@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.logging_utils')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.snmp_utils')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.sys.exit')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.nagios_utils')
def test_trap_not_defined(nagios_utils, exit, snmp_utils, logging_utils):
    trap_name = 'missing'
    lookups = deepcopy(BASE_LOOKUPS)
    lookups[BASIC_NOTIFICATION_TRAP_VALUE] = trap_name

    logger = FakeLogger()
    oid_lookup = FakeOidLookup(lookups=lookups)
    stdin = FakeStdin(deepcopy(BASIC_NOTIFICATION))

    logging_utils.Logger.return_value = logger
    snmp_utils.OIDLookup.return_value = oid_lookup
    snmp_trap_handler.sys.stdin = stdin

    snmp_trap_handler.main()

    logging_utils.Logger.assert_called_once_with(
        'cloudify_nagios_snmp_trap_handler'
    )

    assert logger.string_appears_in('info', (
        'trap', trap_name,
        'from', NOTIFICATION_SOURCE,
    ))

    assert logger.string_appears_in('info', 'no action')


@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.logging_utils')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.snmp_utils')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.sys.exit')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.nagios_utils')
def test_reaction_not_defined(nagios_utils, exit, snmp_utils, logging_utils):
    target_type = 'missing'
    trap_name = 'just_oid_for_message'

    lookups = deepcopy(BASE_LOOKUPS)
    lookups[BASIC_NOTIFICATION_TRAP_VALUE] = trap_name

    logger = FakeLogger()
    oid_lookup = FakeOidLookup(lookups=lookups)
    stdin = FakeStdin(deepcopy(BASIC_NOTIFICATION))

    logging_utils.Logger.return_value = logger
    snmp_utils.OIDLookup.return_value = oid_lookup
    snmp_trap_handler.sys.stdin = stdin
    nagios_utils.get_target_type_for_instance.return_value = target_type

    snmp_trap_handler.main()

    logging_utils.Logger.assert_called_once_with(
        'cloudify_nagios_snmp_trap_handler'
    )

    assert logger.string_appears_in('info', (
        'trap', trap_name,
        'from', NOTIFICATION_SOURCE,
    ))

    assert logger.string_appears_in('debug', 'looking up target type')
    assert logger.string_appears_in('debug', ('target type', target_type))
    assert logger.string_appears_in('info', 'no reaction')


@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.get_check_name')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.logging_utils')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.snmp_utils')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.sys.exit')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.nagios_utils')
def test_reaction(nagios_utils, exit, snmp_utils, logging_utils,
                  get_check_name):
    target_type = 'test_main'
    trap_name = 'just_oid_for_message'
    check_name = 'thecheck'

    lookups = deepcopy(BASE_LOOKUPS)
    lookups[BASIC_NOTIFICATION_TRAP_VALUE] = trap_name

    logger = FakeLogger()
    oid_lookup = FakeOidLookup(lookups=lookups)
    stdin = FakeStdin(deepcopy(BASIC_NOTIFICATION))

    logging_utils.Logger.return_value = logger
    snmp_utils.OIDLookup.return_value = oid_lookup
    snmp_trap_handler.sys.stdin = stdin
    nagios_utils.get_target_type_for_instance.return_value = target_type
    get_check_name.return_value = check_name
    nagios_utils.get_services_for_host.return_value = [{
        "service_description": check_name, "current_state": "0",
    }]

    snmp_trap_handler.main()

    logging_utils.Logger.assert_called_once_with(
        'cloudify_nagios_snmp_trap_handler'
    )

    assert logger.string_appears_in('info', (
        'trap', trap_name,
        'from', NOTIFICATION_SOURCE,
    ))

    assert logger.string_appears_in('debug', 'looking up target type')
    assert logger.string_appears_in('debug', ('target type', target_type))
    assert logger.string_appears_in('info',
                                    ('reaction defined', 'updating', 'check'))

    exit.assert_called_once_with(0)


@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.get_check_name')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.logging_utils')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.snmp_utils')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.sys.exit')
@mock.patch('tests.links.cloudify_nagios_snmp_trap_handler.nagios_utils')
def test_verbose_reaction(nagios_utils, exit, snmp_utils, logging_utils,
                          get_check_name):
    target_type = 'test_main_instance'
    trap_name = 'test_main_instance'
    check_name = 'thecheck'

    lookups = deepcopy(BASE_LOOKUPS)
    lookups[VERBOSE_NOTIFICATION_TRAP_VALUE] = trap_name

    logger = FakeLogger()
    oid_lookup = FakeOidLookup(lookups=lookups)
    stdin = FakeStdin(deepcopy(VERBOSE_NOTIFICATION))

    logging_utils.Logger.return_value = logger
    snmp_utils.OIDLookup.return_value = oid_lookup
    snmp_trap_handler.sys.stdin = stdin
    nagios_utils.get_target_type_for_instance.return_value = target_type
    get_check_name.return_value = check_name
    nagios_utils.get_services_for_host.return_value = [{
        "service_description": check_name, "current_state": "0",
    }]

    snmp_trap_handler.main()

    logging_utils.Logger.assert_called_once_with(
        'cloudify_nagios_snmp_trap_handler'
    )

    assert logger.string_appears_in('info', (
        'trap', trap_name,
        'from', NOTIFICATION_SOURCE,
    ))

    assert logger.string_appears_in('debug', 'looking up target type')
    assert logger.string_appears_in('debug', ('target type', target_type))
    assert logger.string_appears_in('info',
                                    ('reaction defined', 'updating', 'check'))

    exit.assert_called_once_with(0)
