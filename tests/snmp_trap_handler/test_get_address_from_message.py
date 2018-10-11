import tests.links.cloudify_nagios_snmp_trap_handler as snmp_trap_handler


def test_ipv4():
    result = snmp_trap_handler.get_address_from_message(
        'UDP: [192.0.2.26]:58628->[192.0.2.214]:162'
    )
    assert result == '192.0.2.26'


def test_ipv6():
    result = snmp_trap_handler.get_address_from_message(
        'UDP: [2001:DB8::1:1]:58628->[2001:DB8::2:45]:162'
    )
    assert result == '2001:DB8::1:1'
