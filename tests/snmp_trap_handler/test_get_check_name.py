import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler
from tests.fakes import FakeLogger


def test_check_name():
    logger = FakeLogger()

    target_type = 'target'
    trap_value = 'trap'
    expected = '{target_type}_instances:SNMPTRAP {trap}'.format(
        target_type=target_type,
        trap=trap_value,
    )

    result = snmp_trap_handler.get_check_name(target_type, trap_value, logger)

    assert result == expected

    assert logger.string_appears_in('debug',
                                    ('check name', 'is', expected.lower()))
