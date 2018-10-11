import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler
from tests.fakes import FakeLogger


def test_generate_message_with_oid():
    logger = FakeLogger()

    trap_value = 'thetrap'
    expected_message_content = 'thismessage'
    action = {
        'oid_for_message': 'something'
    }
    details = {
        'something': expected_message_content
    }
    expected_prefix = snmp_trap_handler.TRAP_RECEIVED_PREFIX.format(
        oid=trap_value,
    ).lower()

    result = snmp_trap_handler.generate_check_message(
        trap_value, details, action, logger
    )

    result = result.lower()
    for component in (expected_prefix,
                      expected_message_content):
        assert component in result
        assert logger.string_appears_in('debug', component)


def test_generate_message_without_oid():
    logger = FakeLogger()

    trap_value = 'thetrap'
    action = {}
    details = {}
    expected_prefix = snmp_trap_handler.TRAP_RECEIVED_PREFIX.format(
        oid=trap_value,
    ).lower()

    result = snmp_trap_handler.generate_check_message(
        trap_value, details, action, logger
    )

    result = result.lower()
    for component in (expected_prefix,
                      'no message oid',
                      trap_value):
        assert component in result
        assert logger.string_appears_in('debug', component)
