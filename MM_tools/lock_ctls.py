import rig_utils
reload(rig_utils)


def lock_leg_ctls(side, *args):

    """Lock attributes on controls"""
    # IK controls
    rig_utils.lock_attr(side + '_legPV_ctl', 's', 'rx', 'ry', 'rz')
    rig_utils.lock_attr(side + '_foot_IK_ctl', 's')
    rig_utils.lock_attr(side + '_heel_RFS_ctl', 's', 'tx', 'ty', 'tz')
    rig_utils.lock_attr(side + '_ball_RFS_ctl', 's', 'tx', 'ty', 'tz')
    rig_utils.lock_attr(side + '_toe_RFS_ctl', 's', 'tx', 'ty', 'tz')

    # FK controls
    rig_utils.lock_attr(side + '_hip_FK_ctl', 's', 'tx', 'ty', 'tz')
    rig_utils.lock_attr(side + '_knee_FK_ctl', 's', 'tx', 'ty', 'tz')
    rig_utils.lock_attr(side + '_ankle_FK_ctl', 's', 'tx', 'ty', 'tz')
    rig_utils.lock_attr(side + '_ball_FK_ctl', 's', 'tx', 'ty', 'tz')
