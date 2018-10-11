import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler
from tests.fakes import FakeLogger, FakeStdin


def test_raw_trap_basic():
    logger = FakeLogger()

    details = [
        'Myhost\n',
        'UDP: [192.0.2.26]:58628->[192.0.2.214]:162\n',
    ]
    extra_details = [
        'system.sysUpTime.0 1234\n',
        'snmp.1.1.4.1.0 enterprises.52312.900.0.0.1\n',
    ]
    details.extend(extra_details)

    handle = FakeStdin(details)

    host, conn, raw = snmp_trap_handler.read_raw_trap(handle, logger)

    assert host == 'Myhost'
    assert conn == 'UDP: [192.0.2.26]:58628->[192.0.2.214]:162'
    assert raw == [
        {'raw_oid': 'system.sysUpTime.0', 'value': '1234'},
        {'raw_oid': 'snmp.1.1.4.1.0', 'value': 'enterprises.52312.900.0.0.1'},
    ]

    for line in logger.messages['debug']:
        if 'received' in line.lower():
            # Make sure debug log gives basic details
            assert host in line
            assert conn in line

    extra_details_logs = [
        message.split(':')[1].strip() for message in logger.messages['debug']
        if 'extra' in message.lower()
    ]
    for extra_detail in extra_details:
        assert extra_detail.strip() in extra_details_logs


def test_raw_trap_verbose():
    logger = FakeLogger()

    details = [
        'Myhost\n',
        'UDP: [192.0.2.26]:58628->[192.0.2.214]:162\n',
    ]
    extra_details = [
        'system.sysUpTime.0 5678\n',
        'snmp.1.1.4.1.0 enterprises.52312.900.0.0.2\n',
        'enterprises.52312.900.0.1.1 Testmessage\n',
        'enterprises.52312.900.0.1.2 Affected node is 192.0.2.48\n',
        'enterprises.52312.900.0.1.3 Some information that does not matter\n',
    ]
    details.extend(extra_details)

    handle = FakeStdin(details)

    host, conn, raw = snmp_trap_handler.read_raw_trap(handle, logger)

    assert host == 'Myhost'
    assert conn == 'UDP: [192.0.2.26]:58628->[192.0.2.214]:162'
    assert raw == [
        {'raw_oid': 'system.sysUpTime.0', 'value': '5678'},
        {'raw_oid': 'snmp.1.1.4.1.0', 'value': 'enterprises.52312.900.0.0.2'},
        {'raw_oid': 'enterprises.52312.900.0.1.1', 'value': 'Testmessage'},
        {'raw_oid': 'enterprises.52312.900.0.1.2',
         'value': 'Affected node is 192.0.2.48'},
        {'raw_oid': 'enterprises.52312.900.0.1.3',
         'value': 'Some information that does not matter'},
    ]

    for line in logger.messages['debug']:
        if 'received' in line.lower():
            # Make sure debug log gives basic details
            assert host in line
            assert conn in line

    extra_details_logs = [
        message.split(':')[1].strip() for message in logger.messages['debug']
        if 'extra' in message.lower()
    ]
    for extra_detail in extra_details:
        assert extra_detail.strip() in extra_details_logs
