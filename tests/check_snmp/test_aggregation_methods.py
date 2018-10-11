import tests.links.check_snmp_aggregate as check_snmp_aggregate


def test_calculate_mean():
    inputs = 1, 2.0, 3
    expected = 2.0

    result = check_snmp_aggregate.calculate_mean(inputs)
    assert result == expected


def test_calculate_mean_approach():
    expected = check_snmp_aggregate.calculate_mean
    assert check_snmp_aggregate.APPROACHES['arithmetic_mean'] == expected


def test_calculate_sum():
    inputs = 1, 2.0, 3
    expected = 6.0

    result = check_snmp_aggregate.calculate_sum(inputs)
    assert result == expected


def test_calculate_sum_approach():
    expected = check_snmp_aggregate.calculate_sum
    assert check_snmp_aggregate.APPROACHES['sum'] == expected
