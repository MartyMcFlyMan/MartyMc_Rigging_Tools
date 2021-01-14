import maya.cmds as cmds

import rig_utils
reload(rig_utils)


def create_rfs(side, *args):

    """Create mySKEL rig reverse foot setup, argument is leg side L or R"""

    # create single chain ik handles from:
    # ankle to ball
    ankle_eff_name = cmds.ikHandle(n=side + '_ball_ikHandle', sj=side + '_ankle_IK_jnt',
                                   ee=side + '_ball_IK_jnt', sol='ikSCsolver', s='sticky')
    cmds.rename(ankle_eff_name[1], side + '_ball_effector')

    # ball to toe
    ball_eff_name = cmds.ikHandle(n=side + '_toe_ikHandle', sj=side + '_ball_IK_jnt',
                                  ee=side + '_toe_IK_jnt', sol='ikSCsolver', s='sticky')
    cmds.rename(ball_eff_name[1], side + '_toe_effector')

    # create groups for RFS on the joints (query joints info then create and place groups)
    heel_pos = tuple(cmds.xform(side + '_heel_jnt', q=True, t=True, ws=True))
    toe_pos = tuple(cmds.xform(side + '_toe_jnt', q=True, t=True, ws=True))
    ball_pos = tuple(cmds.xform(side + '_ball_jnt', q=True, t=True, ws=True))
    ankle_pos = tuple(cmds.xform(side + '_ankle_jnt', q=True, t=True, ws=True))

    heel_grp = cmds.group(n=side + '_heel_RFS_grp', w=True, em=True)
    cmds.xform(heel_grp, t=heel_pos, ws=True)
    toe_grp = cmds.group(n=side + '_toe_RFS_grp', em=True, p=heel_grp)
    cmds.xform(toe_grp, t=toe_pos, ws=True)
    ball_grp = cmds.group(n=side + '_ball_RFS_grp', em=True, p=toe_grp)
    cmds.xform(ball_grp, t=ball_pos, ws=True)
    ankle_grp = cmds.group(n=side + '_ankle_RFS_grp', em=True, p=ball_grp)
    cmds.xform(ankle_grp, t=ankle_pos, ws=True)

    # Make a Parent RFS group
    cmds.group(n=side + '_foot_RFS_grp', em=True, w=True)
    cmds.xform(side + '_foot_RFS_grp', ws=True, t=ankle_pos)

    cmds.parent(side + '_heel_RFS_grp', side + '_foot_RFS_grp')

    # place it under the foot controllers
    cmds.parent(side + '_leg_ikHandle', side + '_foot_IK_ctl')

    # put the pole vector controllers under the IK foot controllers
    cmds.parent(side + '_legPV_offset', side + '_foot_IK_ctl')

    # create heel, toe and ball controls, rotated 90 degrees, frozen and grouped
    def create_rfs_ctl(part):

        # get jnt name
        jnt_name = side + '_' + part + '_IK_jnt'

        # get joint position
        part_pos = tuple(cmds.xform(jnt_name, q=True, t=True, ws=True))

        # create controls
        ctl_name = cmds.circle(n=side + '_' + part + '_RFS_ctl', ch=False)[0]
        cmds.xform(ctl_name, ro=(0, 90, 0))
        cmds.makeIdentity(ctl_name, a=True, r=True, s=True, t=True)
        rig_utils.colour_red(ctl_name)

        # create groups
        grp_name = cmds.group(n=side + '_' + part + '_RFS_offset')
        cmds.xform(grp_name, t=part_pos, ws=True)

        return None

    create_rfs_ctl('heel')
    create_rfs_ctl('ball')
    create_rfs_ctl('toe')

    # place everything in a working hierachy, groups, ikHandles and controllers
    cmds.parent(side + '_leg_ikHandle', side + '_ankle_RFS_grp')
    cmds.parent(side + '_ball_ikHandle', side + '_ball_RFS_grp')
    cmds.parent(side + '_toe_ikHandle', side + '_toe_RFS_grp')

    cmds.parent(side + '_foot_RFS_grp', side + '_foot_IK_ctl')

    cmds.parent(side + '_heel_RFS_offset', side + '_foot_RFS_grp')
    cmds.parent(side + '_heel_RFS_grp', side + '_heel_RFS_ctl')

    cmds.parent(side + '_toe_RFS_offset', side + '_heel_RFS_grp')
    cmds.parent(side + '_toe_RFS_grp', side + '_toe_RFS_ctl')

    cmds.parent(side + '_ball_RFS_offset', side + '_toe_RFS_grp')
    cmds.parent(side + '_ball_RFS_grp', side + '_ball_RFS_ctl')

    # hide all the ikHandles
    rig_utils.hide(side + '_leg_ikHandle')
    rig_utils.hide(side + '_ball_ikHandle')
    rig_utils.hide(side + '_toe_ikHandle')
