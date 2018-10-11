import time
import utils


def test_scale_down_on_group_threshold_breach():
    tenant = 'test_group_breach_scale_down'
    config = utils.load_config()
    main_client = utils.get_rest_client_using_config(
        config,
        tenant='default_tenant',
    )

    main_client.tenants.create(tenant)
    client = utils.get_rest_client_using_config(
        config,
        tenant=tenant,
    )

    utils.upload_config_secrets(config, client)
    installed_plugins = utils.upload_required_plugins(client)

    utils.deploy_nagios(
        utils.get_examples_blueprint_path('nagios-groups.yaml'),
        utils.get_nagios_inputs(config),
        client,
    )
    utils.install_blueprint(
        utils.get_examples_blueprint_path('basegroup1.yaml'),
        utils.get_monitored_vms_inputs(config),
        'basegroup1',
        client,
    )
    utils.install_blueprint(
        utils.get_examples_blueprint_path('basegroup2.yaml'),
        utils.get_monitored_vms_inputs(config),
        'basegroup2',
        client,
    )

    utils.execute_arbitrary_command(
        'basegroup1',
        'echo 2 > /tmp/cloudifytestinteger',
        client,
    )
    utils.execute_arbitrary_command(
        'basegroup1',
        'echo {time_now}:2.0 > /tmp/cloudifytestcounter'.format(
            time_now=int(time.time()),
        ),
        client,
    )

    # Confirm the expected workflow runs
    utils.wait_for_execution_on_deployment('scale',
                                           'basegroup1',
                                           client)

    utils.remove_deployment('basegroup1', client)
    utils.delete_blueprint('basegroup1', client)
    utils.remove_deployment('basegroup2', client)
    utils.delete_blueprint('basegroup2', client)

    utils.remove_nagios(client)
    utils.delete_plugins(installed_plugins, client)
    utils.remove_config_secrets(client)

    main_client.tenants.delete(tenant)


def test_scale_down_on_metagroup_threshold_breach():
    tenant = 'test_metagroup_breach_scale_down'
    config = utils.load_config()
    main_client = utils.get_rest_client_using_config(
        config,
        tenant='default_tenant',
    )

    main_client.tenants.create(tenant)
    client = utils.get_rest_client_using_config(
        config,
        tenant=tenant,
    )

    utils.upload_config_secrets(config, client)
    installed_plugins = utils.upload_required_plugins(client)

    utils.deploy_nagios(
        utils.get_examples_blueprint_path('nagios-groups.yaml'),
        utils.get_nagios_inputs(config),
        client,
    )
    utils.install_blueprint(
        utils.get_examples_blueprint_path('basemetagroup1.yaml'),
        utils.get_monitored_vms_inputs(config),
        'basemetagroup1',
        client,
    )
    utils.install_blueprint(
        utils.get_examples_blueprint_path('basemetagroup2.yaml'),
        utils.get_monitored_vms_inputs(config),
        'basemetagroup2',
        client,
    )

    utils.execute_arbitrary_command(
        'basemetagroup2',
        'echo {time_now}:0 > /tmp/cloudifytestcounter'.format(
            time_now=int(time.time()),
        ),
        client,
    )

    # Confirm the expected workflow runs
    utils.wait_for_execution_on_deployment('scale',
                                           'basemetagroup1',
                                           client)

    utils.remove_deployment('basemetagroup1', client)
    utils.delete_blueprint('basemetagroup1', client)
    utils.remove_deployment('basemetagroup2', client)
    utils.delete_blueprint('basemetagroup2', client)

    utils.remove_nagios(client)
    utils.delete_plugins(installed_plugins, client)
    utils.remove_config_secrets(client)

    main_client.tenants.delete(tenant)
