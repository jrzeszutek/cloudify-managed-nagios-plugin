from __future__ import print_function
from base64 import urlsafe_b64encode
from cloudify_rest_client import CloudifyClient
import os
import time

from cloudify_cli import utils as cli_utils
import yaml


MONITORED_VM_INPUTS = (
    'image',
    'flavor',
    'management_network_name',
    'key_name',
)
NAGIOS_INPUTS = MONITORED_VM_INPUTS + ('floating_network_id',)
CONFIG_SECRETS = (
    'keystone_url',
    'keystone_username',
    'keystone_password',
    'keystone_tenant_name',
    'region',
    'cloudify_manager_username',
    'cloudify_manager_password',
)
DEFAULT_MANAGED_NAGIOS_VERSION = "1.0.4"
DEFAULT_NAGIOSREST_VERSION = "1.1.0"
DEFAULT_OPENSTACK_VERSION = "2.0.1"


def get_rest_client(address, username, password, tenant, cert_path=None):
    return CloudifyClient(
        host=address,
        port=443 if cert_path else 80,
        protocol='https' if cert_path else 'http',
        headers={
            'Authorization': 'Basic {authstring}'.format(
                authstring=urlsafe_b64encode(username + ':' + password),
            ),
            'Tenant': tenant,
        },
        cert=cert_path,
    )


def deploy_nagios(blueprint_path, inputs, client):
    install_blueprint(blueprint_path, inputs, 'nagios', client)
    update_nagios_secrets(client)


def update_nagios_secrets(client):
    outputs = client.deployments.outputs.get('nagios')['outputs']
    secrets = {
        'nagiosrest_address': outputs['internal_address'],
        'nagiosrest_user': outputs['nagios_web_username'],
        'nagiosrest_pass': outputs['nagios_web_password'],
        'nagiosrest_certificate': outputs['nagios_ssl_certificate'],
    }

    create_secrets(secrets, client)


def delete_nagios_secrets(client):
    delete_secrets(
        (
            'nagiosrest_address',
            'nagiosrest_user',
            'nagiosrest_pass',
            'nagiosrest_certificate',
        ),
        client,
    )


def get_nagios_internal_ip(client):
    outputs = client.deployments.outputs.get('nagios')['outputs']
    return outputs['internal_address']


def remove_nagios(client):
    secrets = ['nagiosrest_{0}'.format(entry) for entry in
               ('address', 'user', 'pass', 'certificate')]
    delete_secrets(secrets, client)

    remove_deployment('nagios', client)

    delete_blueprint('nagios', client)


def install_blueprint(blueprint_path, inputs, name, client):
    client.blueprints.upload(path=blueprint_path, entity_id=name)
    client.deployments.create(blueprint_id=name, deployment_id=name,
                              inputs=inputs)

    # Wait for the deployment env to be created
    deployment_env_created = False
    while not deployment_env_created:
        for execution in client.executions.list(
            deployment_id=name,
            _include=['workflow_id', 'status'],
        ):
            if (
                execution['workflow_id'] == 'create_deployment_environment'
                and execution['status'] == 'terminated'
            ):
                deployment_env_created = True
            else:
                time.sleep(3)

    execute(name, 'install', client)


def remove_deployment(name, client):
    execute(name, 'uninstall', client)
    client.deployments.delete(name)

    deployment_deleted = False
    while not deployment_deleted:
        deployments = [
            deployment['id']
            for deployment in client.deployments.list()
        ]
        if name in deployments:
            print(
                'Waiting for {dep} deployment to be deleted...'.format(
                    dep=name,
                )
            )
            time.sleep(3)
        else:
            deployment_deleted = True


def delete_blueprint(name, client):
    client.blueprints.delete(name)


def execute(deployment_id, workflow_name, client,
            wait=True, parameters=None, force=False):
    execution = client.executions.start(deployment_id=deployment_id,
                                        workflow_id=workflow_name,
                                        parameters=parameters,
                                        force=force)
    if wait:
        wait_for_execution(execution['id'], client)
    execution = client.executions.get(execution['id'])
    return execution


class ExecutionStateError(Exception):
    pass


def wait_for_execution(execution_id, client, poll_interval=3):
    while True:
        execution = client.executions.get(execution_id)
        if execution['status'] == 'terminated':
            print('Execution {exc} complete.'.format(exc=execution_id))
            return execution
        elif (
            execution['status'] == 'started'
            or execution['status'] == 'pending'
        ):
            print('Execution {exc} still running...'.format(exc=execution_id))
            time.sleep(poll_interval)
        else:
            raise ExecutionStateError(
                'Execution {exc} in unexpected state {state}'.format(
                    exc=execution_id,
                    state=execution['status'],
                )
            )


def upload_required_plugins(
    client,
    managed_nagios_version=DEFAULT_MANAGED_NAGIOS_VERSION,
    nagiosrest_version=DEFAULT_NAGIOSREST_VERSION,
    openstack_version=DEFAULT_OPENSTACK_VERSION,
):
    plugin_wagon = (
        'http://repository.cloudifysource.org/cloudify/wagons/{plugin}/'
        '{version}/{plugin_underscore}-{version}-py27-none-linux_x86_64-'
        'centos-Core.wgn'
    )
    plugin_yaml = (
        'http://www.getcloudify.org/spec/{plugin}/{version}/plugin.yaml'
    )

    required_plugins = (
        (
            plugin_wagon.format(
                plugin='cloudify-managed-nagios-plugin',
                plugin_underscore='cloudify_managed_nagios_plugin',
                version=managed_nagios_version,
            ),
            plugin_yaml.format(
                plugin='managed-nagios-plugin',
                version=managed_nagios_version,
            )
        ),
        (
            plugin_wagon.format(
                plugin='cloudify-nagiosrest-plugin',
                plugin_underscore='cloudify_nagiosrest_plugin',
                version=nagiosrest_version,
            ),
            plugin_yaml.format(
                plugin='nagiosrest-plugin',
                version=nagiosrest_version,
            )
        ),
        (
            plugin_wagon.format(
                plugin='cloudify-openstack-plugin',
                plugin_underscore='cloudify_openstack_plugin',
                version=openstack_version,
            ),
            plugin_yaml.format(
                plugin='openstack-plugin',
                version=openstack_version,
            )
        ),
        (
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'examples', 'plugins',
                'arbitrary_command_plugin-0.1.2-py27-none-any.wgn'
            ),
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'examples', 'plugins',
                'arbitrary-command-plugin.yaml',
            )
        ),
    )

    installed_plugins = []

    for wagon, plugin_yaml in required_plugins:
        print(
            'Attempting to install wagon {wagon} '
            'with plugin yaml {plugin_yaml}...'.format(
                wagon=wagon,
                plugin_yaml=plugin_yaml,
            )
        )
        installed_plugins.append(
            upload_plugin(wagon, plugin_yaml, client)
        )

    return installed_plugins


def delete_plugins(plugin_ids, client):
    for plugin in plugin_ids:
        client.plugins.delete(plugin)


def upload_plugin(plugin_path, yaml_path, client):
    wagon_path = cli_utils.get_local_path(plugin_path, create_temp=True)
    yaml_path = cli_utils.get_local_path(yaml_path, create_temp=True)
    zip_path = cli_utils.zip_files([wagon_path, yaml_path])

    try:
        plugin = client.plugins.upload(zip_path)
    finally:
        os.remove(wagon_path)
        os.remove(yaml_path)
        os.remove(zip_path)

    return plugin.id


def create_secrets(secrets, client):
    for key, value in list(secrets.items()):
        client.secrets.create(key=key, value=value, is_hidden_value=True)


def delete_secrets(secrets, client):
    for secret in secrets:
        client.secrets.delete(secret)


def get_monitored_vms_inputs(config):
    return {
        entry: config[entry]
        for entry in MONITORED_VM_INPUTS
    }


def get_nagios_inputs(config):
    return {
        entry: config[entry]
        for entry in NAGIOS_INPUTS
    }


def upload_config_secrets(config, client):
    secrets = {
        entry: config[entry]
        for entry in CONFIG_SECRETS
    }

    with open(config['private_key_path']) as key_handle:
        secrets['agent_key_private'] = key_handle.read()

    create_secrets(secrets, client)


def remove_config_secrets(client):
    delete_secrets(
        CONFIG_SECRETS + ('agent_key_private',),
        client,
    )


def get_rest_client_using_config(config, tenant='default_tenant'):
    client = get_rest_client(
        address=config['cloudify_address'],
        username=config['cloudify_manager_username'],
        password=config['cloudify_manager_password'],
        tenant=tenant,
        cert_path=config.get('cloudify_certificate'),
    )
    # Fail fast if the settings are wrong, rather than failing in another
    # method later and letting someone dig into that method for an hour
    # before realising they got one of the connection settings wrong
    client.manager.get_status()
    return client


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path) as config_handle:
        config = yaml.load(config_handle.read())
    return config


def execute_arbitrary_command(deployment, command, client, target=None):
    execute(
        deployment, 'execute_operation', client,
        parameters={
            'node_ids': ['command'],
            'operation': 'cloudify.interfaces.execute.command',
            'allow_kwargs_override': True,
            'operation_kwargs': {
                'command': command,
                'run_on': target,
            },
        },
    )

    node_instances = list(client.node_instances.list(
        deployment_id=deployment,
        node_name='command',
        _include=['runtime_properties', 'host_id'],
    ))
    print(node_instances)

    if target:
        for instance in node_instances:
            if instance['host_id'] == target:
                return instance['runtime_properties']
    else:
        return node_instances[0]['runtime_properties']


class ExecutionNotStarted(Exception):
    pass


def wait_for_execution_on_deployment(workflow,
                                     deployment,
                                     client,
                                     max_wait_for_start=90,
                                     retry_interval=3,
                                     wait_for_completion=True):
    waited = 0
    while True:
        executions = client.executions.list(
            deployment_id=deployment,
            _include=['workflow_id', 'id'],
        )

        for execution in executions:
            if execution['workflow_id'] == workflow:
                print(
                    'Execution {workflow} started on {dep}...'.format(
                        workflow=workflow,
                        dep=deployment,
                    )
                )
                if wait_for_completion:
                    return wait_for_execution(execution['id'], client)
                else:
                    return execution
            else:
                if waited > max_wait_for_start:
                    raise ExecutionNotStarted(
                        'Execution {workflow} on {dep} did not start within '
                        '{max_wait} seconds.'.format(
                            workflow=workflow,
                            dep=deployment,
                            max_wait=max_wait_for_start,
                        )
                    )
                else:
                    print(
                        'Waiting for execution {workflow} on {dep}...'.format(
                            workflow=workflow,
                            dep=deployment,
                        )
                    )

                    # This does mean we can wait slightly longer than
                    # specified for the execution to start, but the
                    # alternative is making it possible to wait too little
                    waited += retry_interval
                    time.sleep(retry_interval)


def get_first_node_instance(node, deployment, client):
    return client.node_instances.list(
        node_name=node,
        deployment_id=deployment,
        _include=['id']
    )[0]['id']


def get_examples_blueprint_path(blueprint_name):
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'examples',
        'blueprints',
        blueprint_name,
    )


def get_first_node_instance_ip(node, deployment, client):
    instance = client.node_instances.list(
        deployment_id=deployment,
        node_name=node,
    )[0]

    return instance['runtime_properties']['ip']
