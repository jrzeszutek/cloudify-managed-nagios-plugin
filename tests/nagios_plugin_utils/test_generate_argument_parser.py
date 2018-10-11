import nagios_plugin_utils


def test_generated_parser():
    expected_args = [
        '--target-type',
        '--low-warning',
        '--low-critical',
        '--high-warning',
        '--high-critical',
        '--rate',
    ]

    usage = nagios_plugin_utils.get_argument_parser('').format_usage()

    for arg in expected_args:
        assert arg in usage
