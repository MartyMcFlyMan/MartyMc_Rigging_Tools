
import maya.cmds as cmds
import sys

import rig_utils
reload(rig_utils)


def setup_fkik_arm(shoulder = None, elbow = None, wrist = None, *args):

    if cmds.objExists('scale_ctl'):
        cmds.parent('COG_jnt', w=True)
        cmds.delete('scale_ctl')

    # freeze all the joints'  to remove rotation info and scale info
    cmds.makeIdentity(shoulder, a=True, r=True, s=True)
    cmds.makeIdentity(elbow, a=True, r=True, s=True)
    cmds.makeIdentity(wrist, a=True, r=True, s=True)

    # get joints side prefix (it is the first character of the joint strings_
    side = shoulder[0] + '_'

    # get middle part of joints name
    def get_middle_name(jnt):
        full_name_list = jnt.split('|')
        short_name_list = full_name_list[-1].split('_')
        middle_name = short_name_list[-2]
        return middle_name

    def get_short_name(jnt):
        full_name_list = jnt.split('|')
        short_name = full_name_list[-1]
        return short_name

    shoulder_mid = get_middle_name(shoulder)
    arm_name = side + shoulder_mid.replace('shoulder', 'arm')
    hand_name = side + shoulder_mid.replace('shoulder', 'hand')

    shoulder_short = get_short_name(shoulder)
    elbow_short = get_short_name(elbow)
    wrist_short = get_short_name(wrist)

    # Part 2 : Make the IK/FK setup and switch
    # create FKIK switch not too far from the shoulder joint (3 units)

    switch_offset_x = -1
    switch_offset_z = -3

    # define on which side of the body we are
    axis = cmds.xform(wrist, q=True, t=True, ws=True)
    if axis[0] > 0:
        switch_offset_x = -switch_offset_x

    shoulder_pos = cmds.xform(shoulder, q=True, t=True, ws=True)

    fkik_loc = cmds.spaceLocator(n=arm_name + 'FKIK_switch', p=shoulder_pos, a=True)
    fkik_loc = ''.join(fkik_loc)
    cmds.xform(fkik_loc, cp=True)
    cmds.xform(fkik_loc, s=(0.5, 0.5, 0.5))

    rig_utils.colour_red(fkik_loc)
    cmds.xform(fkik_loc, r=True, t=(switch_offset_x, 0, switch_offset_z))

    # create IK hand controllers
    # get wrist joint position and orientation
    wrist_pos = tuple(cmds.xform(wrist, q=True, t=True, ws=True))
    wrist_rot = tuple(cmds.xform(wrist, q=True, ro=True, ws=True))

    cmds.circle(n=hand_name + '_IK_ctl', ch=False, d=1, s=4)
    cmds.xform(hand_name + '_IK_ctl', ro=(0, 90, 0))
    cmds.makeIdentity(hand_name + '_IK_ctl', a=True, r=True, s=True, t=True)
    cmds.group(n=hand_name + '_IK_offset')
    cmds.xform(hand_name + '_IK_offset', t=wrist_pos, ro=wrist_rot)

    rig_utils.colour_red(hand_name + '_IK_ctl')

    # Duplicate the arm joints twice (for IK and FK)
    cmds.duplicate(shoulder)
    cmds.duplicate(shoulder)

    # Rename the joints chains for IK and FK
    # FK
    shoulder_fk = cmds.rename(shoulder + '1', shoulder_short[:-4] + '_FK_jnt')
    elbow_fk = cmds.rename(shoulder_fk + '|' + elbow_short, elbow_short[:-4] + '_FK_jnt')
    wrist_fk = cmds.rename(elbow_fk + '|' + wrist_short, wrist_short[:-4] + '_FK_jnt')

    # IK
    shoulder_ik = cmds.rename(shoulder + '2', shoulder_short[:-4] + '_IK_jnt')
    elbow_ik = cmds.rename(shoulder_ik + '|' + elbow_short, elbow_short[:-4] + '_IK_jnt')
    wrist_ik = cmds.rename(elbow_ik + '|' + wrist_short, wrist_short[:-4] + '_IK_jnt')

    # constrain all the FK and IK joints to their respective skinning joint
    # IK
    shoulder_cst = cmds.parentConstraint(shoulder_ik, shoulder)
    shoulder_cst = ''.join(shoulder_cst)
    elbow_cst = cmds.parentConstraint(elbow_ik, elbow)
    elbow_cst = ''.join(elbow_cst)
    wrist_cst = cmds.parentConstraint(wrist_ik, wrist)
    wrist_cst = ''.join(wrist_cst)

    # FK
    cmds.parentConstraint(shoulder_fk, shoulder)
    cmds.parentConstraint(elbow_fk, elbow)
    cmds.parentConstraint(wrist_fk, wrist)

    # set all the constraints' interpolation type to 'shortest'
    cmds.setAttr(shoulder_cst + '.interpType', 2)
    cmds.setAttr(elbow_cst + '.interpType', 2)
    cmds.setAttr(wrist_cst + '.interpType', 2)

    # create the FKIK switch attribute on the locator
    cmds.addAttr(fkik_loc, ln='FKIKSwitch', sn='FKIK', at='float', min=0.0, max=1.0, dv=0.0, k=True)

    # We need to create the FK controllers to be able to hook up their visibility attribute with the FKIK switch
    # create a list of the FK joints where we need controllers (not toe)

    def create_fk_ctl(jnt_name):
        """create standard FK controller on location"""

        # get jnt coordinates
        part_pos = tuple(cmds.xform(jnt_name, q=True, t=True, ws=True))
        part_rot = tuple(cmds.xform(jnt_name, q=True, ro=True, ws=True))

        # create ctl
        ctl_name = cmds.circle(n=jnt_name[:-4] + '_ctl', ch=False)[0]
        cmds.xform(ctl_name, a=True, ro=(0, 90, 0))
        cmds.makeIdentity(ctl_name, t=True, r=True, s=True, a=True)

        # create offsetGrp
        grp_name = cmds.group(ctl_name, n=jnt_name[:-4] + '_offset')
        cmds.xform(grp_name, ro=part_rot, t=part_pos, a=True)

        # constrain ctl to jnt
        cmds.parentConstraint(ctl_name, jnt_name, mo=False)

    create_fk_ctl(shoulder_fk)
    create_fk_ctl(elbow_fk)
    create_fk_ctl(wrist_fk)

    # make FK controller hierarchy
    cmds.parent(wrist_fk[:-4] + '_offset', elbow_fk[:-4] + '_ctl')
    cmds.parent(elbow_fk[:-4] + '_offset', shoulder_fk[:-4] + '_ctl')

    # lets colors the new controllers Blue
    rig_utils.colour_blue(shoulder_fk[:-4] + '_ctl')
    rig_utils.colour_blue(elbow_fk[:-4] + '_ctl')
    rig_utils.colour_blue(wrist_fk[:-4] + '_ctl')

    # Now we need to hook up the FKIK switch to the constraints and controllers visibility using driven keys

    cmds.setDrivenKeyframe(shoulder_cst + '.' + shoulder_fk + 'W1',
                           cd=fkik_loc + '.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(shoulder_cst + '.' + shoulder_fk + 'W1',
                           cd=fkik_loc + '.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(shoulder_cst + '.' + shoulder_ik + 'W0',
                           cd=fkik_loc + '.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(shoulder_cst + '.' + shoulder_ik + 'W0',
                           cd=fkik_loc + '.FKIKSwitch', dv=1, v=0)

    cmds.setDrivenKeyframe(elbow_cst + '.' + elbow_fk + 'W1',
                           cd=fkik_loc + '.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(elbow_cst + '.' + elbow_fk + 'W1',
                           cd=fkik_loc + '.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(elbow_cst + '.' + elbow_ik + 'W0',
                           cd=fkik_loc + '.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(elbow_cst + '.' + elbow_ik + 'W0',
                           cd=fkik_loc + '.FKIKSwitch', dv=1, v=0)

    cmds.setDrivenKeyframe(wrist_cst + '.' + wrist_fk + 'W1',
                           cd=fkik_loc + '.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(wrist_cst + '.' + wrist_fk + 'W1',
                           cd=fkik_loc + '.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(wrist_cst + '.' + wrist_ik + 'W0',
                           cd=fkik_loc + '.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(wrist_cst + '.' + wrist_ik + 'W0',
                           cd=fkik_loc + '.FKIKSwitch', dv=1, v=0)

    # IK controller
    cmds.setDrivenKeyframe(hand_name + '_IK_ctl.v', cd=fkik_loc + '.FKIKSwitch',
                           dv=0, v=1)
    cmds.setDrivenKeyframe(hand_name + '_IK_ctl.v', cd=fkik_loc + '.FKIKSwitch',
                           dv=1, v=0)

    # FK controllers
    cmds.setDrivenKeyframe(wrist_fk[:-4] + '_ctl.v', cd=fkik_loc + '.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(wrist_fk[:-4] + '_ctl.v', cd=fkik_loc + '.FKIKSwitch',
                           dv=1, v=1)

    cmds.setDrivenKeyframe(elbow_fk[:-4] + '_ctl.v', cd=fkik_loc + '.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(elbow_fk[:-4] + '_ctl.v', cd=fkik_loc + '.FKIKSwitch',
                           dv=1, v=1)

    cmds.setDrivenKeyframe(shoulder_fk[:-4] + '_ctl.v', cd=fkik_loc + '.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(shoulder_fk[:-4] + '_ctl.v', cd=fkik_loc + '.FKIKSwitch',
                           dv=1, v=1)

    # set preferred angle on shoulders
    cmds.joint(shoulder, e=True, spa=True)

    # create IK handle on right arm
    ik_name = cmds.ikHandle(n=arm_name + '_ikHandle', sj=shoulder_ik,
                            ee=wrist_ik, sol='ikRPsolver')
    cmds.setAttr(arm_name + '_ikHandle.snapEnable', 0)
    cmds.rename(ik_name[1], arm_name + '_effector')

    # constraint wrist orientation to ikHandle orientation
    cmds.orientConstraint(arm_name + '_ikHandle', wrist_ik, mo=True)

    # Now we need pole vectors
    # first we will need the location of the elbow joints and their orientations
    elbow_pos = cmds.xform(elbow, t=True, ws=True, q=True)
    elbow_orient = cmds.xform(elbow, ro=True, ws=True, q=True)

    # we create the pole vector controllers, we place them using the elbow joints' orientations
    pv_ctl = cmds.circle(n=arm_name + 'PV_ctl', d=1, s=3, ch=False)
    cmds.xform(pv_ctl[0], s=(0.5, 0.5, 0.5))
    cmds.makeIdentity(pv_ctl[0], a=True, t=True, r=True, s=True)

    cmds.group(n=arm_name + 'PV_offset')
    cmds.xform(arm_name + 'PV_offset', t=tuple(elbow_pos), ro=tuple(elbow_orient))
    cmds.xform(arm_name + 'PV_offset', t=(0, 2.5, 0), r=True, os=True)

    axis = cmds.xform(wrist, q=True, t=True, ws=True)
    if axis[0] > 0:
        cmds.xform(arm_name + 'PV_offset', t=(0, -5, 0), r=True, os=True)

    # reset armPV offset group rotations so the conrollers sit nicely in place with world axis
    cmds.xform(arm_name + 'PV_offset', ro=(0, 0, 0))

    # color the armPV controllers
    rig_utils.colour_yellow(arm_name + 'PV_ctl')

    # create Pole vector constraints
    cmds.poleVectorConstraint(arm_name + 'PV_ctl', arm_name + '_ikHandle')

    # hide the FKIK joints (I only hide the top joint so the rest disappears with it)
    rig_utils.hide(shoulder_fk)
    rig_utils.hide(shoulder_ik)
    rig_utils.hide(arm_name + '_ikHandle')

    # parent ikHandle to ik control
    cmds.parent(arm_name + '_ikHandle', hand_name + '_IK_ctl')
