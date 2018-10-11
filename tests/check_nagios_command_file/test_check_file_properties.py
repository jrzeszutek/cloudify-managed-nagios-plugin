import mock
import nagios_plugin_utils

import tests.links.check_nagios_command_file as check_command_file


@mock.patch('tests.links.check_nagios_command_file.S_IMODE')
@mock.patch('tests.links.check_nagios_command_file.grp')
@mock.patch('tests.links.check_nagios_command_file.pwd')
@mock.patch('tests.links.check_nagios_command_file.selinux')
@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_check_file_props_healthy(
    mock_os, mock_print, exit, selinux, pwd, grp, stat_mode
):
    fake_stat = mock.Mock()
    fake_pwuid = mock.Mock()
    fake_grgid = mock.Mock()

    fake_stat.st_mode = check_command_file.S_IFIFO
    fake_pwuid.pw_name = check_command_file.EXPECTED_OWNER
    fake_grgid.gr_name = check_command_file.EXPECTED_GROUP

    mock_os.stat.return_value = fake_stat
    stat_mode.return_value = int(check_command_file.EXPECTED_MODE, 8)
    pwd.getpwuid.return_value = fake_pwuid
    grp.getgrgid.return_value = fake_grgid
    selinux.is_selinux_enabled.return_value = False

    check_command_file.check_file_properties('fakefilename')

    print_output = mock_print.call_args_list[0][0][0].lower()

    assert 'healthy' in print_output
    assert 'will not' not in print_output
    assert 'may not' not in print_output

    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_OK,
    )


@mock.patch('tests.links.check_nagios_command_file.S_IMODE')
@mock.patch('tests.links.check_nagios_command_file.grp')
@mock.patch('tests.links.check_nagios_command_file.pwd')
@mock.patch('tests.links.check_nagios_command_file.selinux')
@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_check_file_props_not_pipe(
    mock_os, mock_print, exit, selinux, pwd, grp, stat_mode
):
    fake_stat = mock.Mock()
    fake_pwuid = mock.Mock()
    fake_grgid = mock.Mock()

    fake_stat.st_mode = 0
    fake_pwuid.pw_name = check_command_file.EXPECTED_OWNER
    fake_grgid.gr_name = check_command_file.EXPECTED_GROUP

    mock_os.stat.return_value = fake_stat
    stat_mode.return_value = int(check_command_file.EXPECTED_MODE, 8)
    pwd.getpwuid.return_value = fake_pwuid
    grp.getgrgid.return_value = fake_grgid
    selinux.is_selinux_enabled.return_value = False

    check_command_file.check_file_properties('fakefilename')

    print_output = mock_print.call_args_list[0][0][0].lower()

    assert 'healthy' not in print_output
    assert 'will not' in print_output
    assert 'may not' not in print_output

    assert 'not a pipe' in print_output

    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_CRITICAL,
    )


@mock.patch('tests.links.check_nagios_command_file.S_IMODE')
@mock.patch('tests.links.check_nagios_command_file.grp')
@mock.patch('tests.links.check_nagios_command_file.pwd')
@mock.patch('tests.links.check_nagios_command_file.selinux')
@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_check_file_props_bad_permissions(
    mock_os, mock_print, exit, selinux, pwd, grp, stat_mode
):
    fake_stat = mock.Mock()
    fake_pwuid = mock.Mock()
    fake_grgid = mock.Mock()

    fake_stat.st_mode = check_command_file.S_IFIFO
    fake_pwuid.pw_name = check_command_file.EXPECTED_OWNER
    fake_grgid.gr_name = check_command_file.EXPECTED_GROUP

    mock_os.stat.return_value = fake_stat
    stat_mode.return_value = 0
    pwd.getpwuid.return_value = fake_pwuid
    grp.getgrgid.return_value = fake_grgid
    selinux.is_selinux_enabled.return_value = False

    check_command_file.check_file_properties('fakefilename')

    print_output = mock_print.call_args_list[0][0][0].lower()

    assert 'healthy' not in print_output
    assert 'will not' not in print_output
    assert 'may not' in print_output

    assert 'file permissions' in print_output

    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_WARNING,
    )


@mock.patch('tests.links.check_nagios_command_file.S_IMODE')
@mock.patch('tests.links.check_nagios_command_file.grp')
@mock.patch('tests.links.check_nagios_command_file.pwd')
@mock.patch('tests.links.check_nagios_command_file.selinux')
@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_check_file_props_bad_owner(
    mock_os, mock_print, exit, selinux, pwd, grp, stat_mode
):
    fake_stat = mock.Mock()
    fake_pwuid = mock.Mock()
    fake_grgid = mock.Mock()

    fake_stat.st_mode = check_command_file.S_IFIFO
    fake_pwuid.pw_name = check_command_file.EXPECTED_OWNER + 'bad'
    fake_grgid.gr_name = check_command_file.EXPECTED_GROUP

    mock_os.stat.return_value = fake_stat
    stat_mode.return_value = int(check_command_file.EXPECTED_MODE, 8)
    pwd.getpwuid.return_value = fake_pwuid
    grp.getgrgid.return_value = fake_grgid
    selinux.is_selinux_enabled.return_value = False

    check_command_file.check_file_properties('fakefilename')

    print_output = mock_print.call_args_list[0][0][0].lower()

    assert 'healthy' not in print_output
    assert 'will not' not in print_output
    assert 'may not' in print_output

    assert 'should be owned' in print_output

    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_WARNING,
    )


@mock.patch('tests.links.check_nagios_command_file.S_IMODE')
@mock.patch('tests.links.check_nagios_command_file.grp')
@mock.patch('tests.links.check_nagios_command_file.pwd')
@mock.patch('tests.links.check_nagios_command_file.selinux')
@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_check_file_props_bad_group(
    mock_os, mock_print, exit, selinux, pwd, grp, stat_mode
):
    fake_stat = mock.Mock()
    fake_pwuid = mock.Mock()
    fake_grgid = mock.Mock()

    fake_stat.st_mode = check_command_file.S_IFIFO
    fake_pwuid.pw_name = check_command_file.EXPECTED_OWNER
    fake_grgid.gr_name = check_command_file.EXPECTED_GROUP + 'bad'

    mock_os.stat.return_value = fake_stat
    stat_mode.return_value = int(check_command_file.EXPECTED_MODE, 8)
    pwd.getpwuid.return_value = fake_pwuid
    grp.getgrgid.return_value = fake_grgid
    selinux.is_selinux_enabled.return_value = False

    check_command_file.check_file_properties('fakefilename')

    print_output = mock_print.call_args_list[0][0][0].lower()

    assert 'healthy' not in print_output
    assert 'will not' not in print_output
    assert 'may not' in print_output

    assert 'group should be' in print_output

    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_WARNING,
    )


@mock.patch('tests.links.check_nagios_command_file.S_IMODE')
@mock.patch('tests.links.check_nagios_command_file.grp')
@mock.patch('tests.links.check_nagios_command_file.pwd')
@mock.patch('tests.links.check_nagios_command_file.selinux')
@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_check_file_props_bad_selinux(
    mock_os, mock_print, exit, selinux, pwd, grp, stat_mode
):
    fake_stat = mock.Mock()
    fake_pwuid = mock.Mock()
    fake_grgid = mock.Mock()

    fake_stat.st_mode = check_command_file.S_IFIFO
    fake_pwuid.pw_name = check_command_file.EXPECTED_OWNER
    fake_grgid.gr_name = check_command_file.EXPECTED_GROUP

    mock_os.stat.return_value = fake_stat
    stat_mode.return_value = int(check_command_file.EXPECTED_MODE, 8)
    pwd.getpwuid.return_value = fake_pwuid
    grp.getgrgid.return_value = fake_grgid
    selinux.is_selinux_enabled.return_value = True

    check_command_file.check_file_properties('fakefilename')

    print_output = mock_print.call_args_list[0][0][0].lower()

    assert 'healthy' not in print_output
    assert 'will not' not in print_output
    assert 'may not' in print_output

    assert 'selinux context should be' in print_output

    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_WARNING,
    )


@mock.patch('tests.links.check_nagios_command_file.S_IMODE')
@mock.patch('tests.links.check_nagios_command_file.grp')
@mock.patch('tests.links.check_nagios_command_file.pwd')
@mock.patch('tests.links.check_nagios_command_file.selinux')
@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_check_file_props_selinux_good_context(
    mock_os, mock_print, exit, selinux, pwd, grp, stat_mode
):
    fake_stat = mock.Mock()
    fake_pwuid = mock.Mock()
    fake_grgid = mock.Mock()

    fake_stat.st_mode = check_command_file.S_IFIFO
    fake_pwuid.pw_name = check_command_file.EXPECTED_OWNER
    fake_grgid.gr_name = check_command_file.EXPECTED_GROUP

    mock_os.stat.return_value = fake_stat
    stat_mode.return_value = int(check_command_file.EXPECTED_MODE, 8)
    pwd.getpwuid.return_value = fake_pwuid
    grp.getgrgid.return_value = fake_grgid
    selinux.is_selinux_enabled.return_value = True
    selinux.getfilecon.return_value = (None,
                                       check_command_file.EXPECTED_CONTEXT)

    check_command_file.check_file_properties('fakefilename')

    print_output = mock_print.call_args_list[0][0][0].lower()

    assert 'healthy' in print_output
    assert 'will not' not in print_output
    assert 'may not' not in print_output

    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_OK,
    )


@mock.patch('tests.links.check_nagios_command_file.S_IMODE')
@mock.patch('tests.links.check_nagios_command_file.grp')
@mock.patch('tests.links.check_nagios_command_file.pwd')
@mock.patch('tests.links.check_nagios_command_file.selinux')
@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_check_file_props_multiple_errors_including_critical(
    mock_os, mock_print, exit, selinux, pwd, grp, stat_mode
):
    fake_stat = mock.Mock()
    fake_pwuid = mock.Mock()
    fake_grgid = mock.Mock()

    fake_stat.st_mode = 0
    fake_pwuid.pw_name = check_command_file.EXPECTED_OWNER + 'not'
    fake_grgid.gr_name = check_command_file.EXPECTED_GROUP + 'not'

    mock_os.stat.return_value = fake_stat
    stat_mode.return_value = 0
    pwd.getpwuid.return_value = fake_pwuid
    grp.getgrgid.return_value = fake_grgid
    selinux.is_selinux_enabled.return_value = True

    check_command_file.check_file_properties('fakefilename')

    print_output = mock_print.call_args_list[0][0][0].lower()

    assert 'healthy' not in print_output
    assert 'will not' in print_output
    assert 'may not' not in print_output

    for fail in (
        'not a pipe',
        'file permissions',
        'should be owned',
        'group should be',
        'selinux context should be',
    ):
        assert fail in print_output

    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_CRITICAL,
    )


@mock.patch('tests.links.check_nagios_command_file.S_IMODE')
@mock.patch('tests.links.check_nagios_command_file.grp')
@mock.patch('tests.links.check_nagios_command_file.pwd')
@mock.patch('tests.links.check_nagios_command_file.selinux')
@mock.patch('tests.links.check_nagios_command_file.sys.exit')
@mock.patch('tests.links.check_nagios_command_file.print')
@mock.patch('tests.links.check_nagios_command_file.os')
def test_check_file_props_multiple_errors_non_critical(
    mock_os, mock_print, exit, selinux, pwd, grp, stat_mode
):
    fake_stat = mock.Mock()
    fake_pwuid = mock.Mock()
    fake_grgid = mock.Mock()

    fake_stat.st_mode = check_command_file.S_IFIFO
    fake_pwuid.pw_name = check_command_file.EXPECTED_OWNER + 'not'
    fake_grgid.gr_name = check_command_file.EXPECTED_GROUP + 'not'

    mock_os.stat.return_value = fake_stat
    stat_mode.return_value = 0
    pwd.getpwuid.return_value = fake_pwuid
    grp.getgrgid.return_value = fake_grgid
    selinux.is_selinux_enabled.return_value = True

    check_command_file.check_file_properties('fakefilename')

    print_output = mock_print.call_args_list[0][0][0].lower()

    assert 'healthy' not in print_output
    assert 'will not' not in print_output
    assert 'may not' in print_output

    for fail in (
        'file permissions',
        'should be owned',
        'group should be',
        'selinux context should be',
    ):
        assert fail in print_output

    exit.assert_called_once_with(
        nagios_plugin_utils.STATUS_WARNING,
    )
