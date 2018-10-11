import json
import subprocess

from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError

from managed_nagios_plugin.snmp_utils import OIDLookup
from managed_nagios_plugin.utils import (
    deploy_file,
    run,
)

TRAP_CONFIGURATION_PATH = '/etc/nagios/objects/snmp_traps/{oid}.json'

oid_lookup = OIDLookup()


@operation
def create(ctx):
    try:
        run(['systemctl', 'status', 'snmptrapd'])
    except subprocess.CalledProcessError:
        raise NonRecoverableError(
            'SNMP trap checks cannot be used if snmptrapd has not been '
            'configured. trap_community should be set on the '
            'cloudify.nagios.nodes.Nagios managed nagios node.'
        )

    trap_oid = oid_lookup.get(ctx.node.properties['trap_oid'])
    instance_oid = ctx.node.properties['instance_oid']
    instance_finder = ctx.node.properties['instance_finder']
    oid_for_message = ctx.node.properties['oid_for_message']

    trap_configuration = {}

    if instance_oid:
        trap_configuration['instance'] = {
            'oid': oid_lookup.get(instance_oid),
            'finder': instance_finder,
        }

    if oid_for_message:
        trap_configuration['oid_for_message'] = oid_for_message

    ctx.logger.info('Deploying trap configuration')
    deploy_file(
        data=json.dumps(trap_configuration),
        destination=TRAP_CONFIGURATION_PATH.format(oid=trap_oid),
        sudo=True,
    )


@operation
def delete(ctx):
    trap_oid = oid_lookup.get(ctx.node.properties['trap_oid'])

    ctx.logger.info('Removing trap configuration')
    run(['rm', '-f', TRAP_CONFIGURATION_PATH.format(oid=trap_oid)],
        sudo=True)
