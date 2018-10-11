from cloudify.exceptions import NonRecoverableError


def get_all_relationship_targets(ctx, target_relation_type,
                                 no_target_error=None):
    target_relation_type = 'cloudify.nagios.' + target_relation_type
    targets = []
    for relationship in ctx.instance.relationships:
        if relationship.type == target_relation_type:
            targets.append(relationship.target)

    if no_target_error and not targets:
        raise NonRecoverableError(no_target_error.format(
            target_relation_type=target_relation_type,
        ))
    return targets


def get_relationship_target(ctx, target_relation_type,
                            no_target_error=None,
                            multiple_target_error=None):
    targets = get_all_relationship_targets(ctx, target_relation_type,
                                           no_target_error)

    if len(targets) > 1 and multiple_target_error:
        raise NonRecoverableError(multiple_target_error.format(
            target_relation_type=target_relation_type,
        ))
    elif not targets:
        # This will only trigger if no_target_error is not set
        return None
    else:
        return targets[0]
