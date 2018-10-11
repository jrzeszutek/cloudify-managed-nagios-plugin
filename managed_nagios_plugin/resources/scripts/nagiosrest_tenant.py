import os

from utils import (
    deploy_configuration_file,
    make_config_subdir,
)


def get_tenant_configuration_destination(tenant):
    return 'tenants/{tenant}.cfg'.format(tenant=tenant)


def configure_tenant_group(logger, tenant):
    destination = get_tenant_configuration_destination(tenant)
    name = 'tenant:{tenant}'.format(tenant=tenant)
    description = 'Monitored components for tenant {tenant}'.format(
        tenant=tenant,
    )

    make_config_subdir(os.path.dirname(destination))
    deploy_configuration_file(
        logger,
        source='hostgroup.template',
        destination=destination,
        template_params={
            'name': name,
            'description': description,
        },
        reload_service=False,
        use_pkg_data=False,
    )
