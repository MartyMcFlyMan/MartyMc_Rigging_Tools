import maya.cmds as cmds

import rig_utils
reload(rig_utils)


def setup_ik_leg(side, *args):

    """Creates the IK leg and pole vector setup for mySKEL rigging setup tool"""

    # set preferred angle on hips
    cmds.joint(side + '_hip_jnt', e=True, spa=True)

    # create IK handle on right leg
    ik_name = cmds.ikHandle(n=side+ '_leg_ikHandle', sj=side+ '_hip_IK_jnt',
                            ee=side+ '_ankle_IK_jnt', sol='ikRPsolver', s='sticky')
    cmds.setAttr(side + '_leg_ikHandle.snapEnable', 0)
    cmds.rename(ik_name[1], side + '_leg_effector')

    # constraint ankle orientation to ikHandle orientation
    cmds.orientConstraint(side + '_leg_ikHandle', side + '_ankle_IK_jnt', mo=True)

    # Now we need pole vectors
    # first we will need the location of the knee joints and their orientations
    knee_pos = cmds.xform(side + '_knee_jnt', t=True, ws=True, q=True)
    knee_orient = cmds.xform(side + '_knee_jnt', ro=True, ws=True, q=True)

    #  we create the pole vector controllers, we place them using the knee joints' orientations
    pv_ctl = cmds.circle(n=side + '_legPV_ctl', d=1, s=3, ch=False)
    cmds.xform(pv_ctl[0], s=(0.5, 0.5, 0.5))
    cmds.makeIdentity(pv_ctl[0], a=True, t=True, r=True, s=True)

    cmds.group(n=side + '_legPV_offset')
    cmds.xform(side + '_legPV_offset', t=tuple(knee_pos), ro=tuple(knee_orient))
    cmds.xform(side + '_legPV_offset', t=(0, 5, 0), r=True, os=True)

    leg_pv_pos = cmds.xform(side + '_legPV_offset', t=True, q=True)

    if leg_pv_pos[2] < 0:
        cmds.xform(side + '_legPV_offset', t=(0, -10, 0), r=True, os=True)

    # reset legPV offset group rotations so the conrollers sit nicely in place with world axis
    cmds.xform(side + '_legPV_offset', ro=(0, 0, 0))

    # color the legPV controllers
    rig_utils.colour_yellow(side + '_legPV_ctl')

    # create Pole vector constraints
    cmds.poleVectorConstraint(side + '_legPV_ctl', side + '_leg_ikHandle')

    # hide the FKIK joints (I only hide the top joint so the rest disappears with it)
    rig_utils.hide(side + '_hip_IK_jnt')
    rig_utils.hide(side + '_hip_FK_jnt')

    # parent ikhandle under foot ctl
    cmds.parent(side + '_leg_ikHandle', side + '_foot_IK_ctl')