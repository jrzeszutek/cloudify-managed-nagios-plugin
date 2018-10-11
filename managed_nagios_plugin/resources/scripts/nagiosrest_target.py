import os

from utils import (
    deploy_configuration_file,
    get_node_id,
    make_config_subdir,
)
from nagiosrest_tenant import configure_tenant_group


def get_target_configuration_destination(name):
    return 'targets/{name}.cfg'.format(name=name)


def get_node_configuration_destination(tenant, deployment, node):
    return 'deployments/{tenant}/{deployment}/{node}.cfg'.format(
        tenant=tenant,
        deployment=deployment,
        node=node,
    )


def get_tenant_deployment_configuration_destination(tenant, deployment):
    return 'deployments/{tenant}/{deployment}.cfg'.format(
        tenant=tenant,
        deployment=deployment,
    )


def get_tenant_target_type_configuration_destination(tenant, target_type):
    return 'target_types/{tenant}/{target_type}.cfg'.format(
        tenant=tenant,
        target_type=target_type,
    )


def create_target(logger,
                  instance_id, instance_ip,
                  tenant, deployment,
                  target_type):
    configure_tenant_group(logger, tenant)
    supporting_hostgroups = [
        {
            'params': {
                'tenant': tenant,
                'deployment': deployment,
            },
            'destmethod': get_tenant_deployment_configuration_destination,
            'name': 'tenant:{tenant}/deployment:{deployment}',
            'description': (
                'Monitored hosts in deployment {deployment} for tenant '
                '{tenant}'
            ),
        },
        {
            'params': {
                'tenant': tenant,
                'target_type': target_type,
            },
            'destmethod': get_tenant_target_type_configuration_destination,
            'name': 'tenant:{tenant}/target_type:{target_type}',
            'description': (
                'Monitored hosts of type {target_type} for tenant {tenant}'
            ),
        },
    ]

    for hostgroup in supporting_hostgroups:
        params = hostgroup['params']
        hostgroup_destination = hostgroup['destmethod'](**params)
        hostgroup_name = hostgroup['name'].format(**params)
        hostgroup_description = hostgroup['description'].format(**params)

        make_config_subdir(os.path.dirname(hostgroup_destination))

        deploy_configuration_file(
            logger,
            source='hostgroup.template',
            destination=hostgroup_destination,
            template_params={
                'name': hostgroup_name,
                'description': hostgroup_description,
            },
            reload_service=False,
            use_pkg_data=False,
        )

    node = get_node_id(instance_id)
    node_destination = get_node_configuration_destination(
        tenant,
        deployment,
        node,
    )
    make_config_subdir(os.path.dirname(node_destination))

    # Deploy node pseudo host
    deploy_configuration_file(
        logger,
        source='node.template',
        destination=node_destination,
        template_params={
            'node_id': node,
            'deployment': deployment,
            'tenant': tenant,
            'target_type': target_type,
        },
        reload_service=False,
        use_pkg_data=False,
    )

    deploy_configuration_file(
        logger,
        source='target.template',
        destination=get_target_configuration_destination(instance_id),
        template_params={
            'instance_id': instance_id,
            'instance_ip': instance_ip,
            'deployment': deployment,
            'tenant': tenant,
            'target_type': target_type,
        },
        use_pkg_data=False,
    )
