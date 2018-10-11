import mock
import nagios_plugin_utils

import tests.links.check_nagios_command_file as check_command_file


@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_exists(mock_os, mock_print, exit):
    mock_os.path.exists.return_value = True

    result = check_command_file.check_file_exists('fakefilename')

    assert result is None

    mock_print.assert_not_called()
    exit.assert_not_called()


@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_does_not_exist(mock_os, mock_print, exit):
    mock_os.path.exists.return_value = False

    check_command_file.check_file_exists('fakefilename')

    assert 'does not exist' in mock_print.call_args_list[0][0][0]
    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_CRITICAL,
    )
