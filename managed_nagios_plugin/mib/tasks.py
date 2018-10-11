from cloudify.decorators import operation

from managed_nagios_plugin.utils import (
    download_and_deploy_file_from_blueprint,
    run,
)

MIB_PATH = '/usr/share/snmp/mibs/{mib_name}'
BLUEPRINT_MIB_PATH = 'mibs/{mib_name}'


@operation
def create(ctx):
    name = ctx.node.properties['name']

    ctx.logger.info('Deploying MIB file')
    download_and_deploy_file_from_blueprint(
        source=BLUEPRINT_MIB_PATH.format(mib_name=name),
        destination=MIB_PATH.format(mib_name=name),
        ownership='root.root',
        permissions='644',
        ctx=ctx,
    )


@operation
def delete(ctx):
    name = ctx.node.properties['name']

    ctx.logger.info('Removing MIB file')
    run(['rm', MIB_PATH.format(mib_name=name)],
        sudo=True)
