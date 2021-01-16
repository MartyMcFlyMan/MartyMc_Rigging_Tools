
import maya.cmds as cmds
import sys

import rig_utils
reload(rig_utils)


def setup_fkik_arm(side, *args):

    # Part 1 : Verify required objects
    # make a list of all the required objects and verify they exist
    required_objects = [
        '_shoulder_jnt',
        '_elbow_jnt',
        '_wrist_jnt',
    ]
    # make cancel switch to abort the script if an object is missing
    missing_object = False

    # make an empty list of missing objects
    missing_list = []

    for item in required_objects:
        if cmds.objExists(side + item):
            continue
        else:
            missing_object = True
            missing_list.append(item)

    if missing_object:
        print 'The scene must contain the following objects:\n' \
            'A joint chain containing the following: shoulder, elbow, wrist\n' \
            'You do not have all the required items\n' \
            'The following objects are missing: {}\n'.format(missing_list)
        sys.exit('Missing objects: {}\n'.format(missing_list))

    else:
        print 'all required objects confirmed\n'

    # From here, if the code still runs, it means we have all we need to proceed

    if cmds.objExists('scale_ctl'):
        cmds.parent('COG_jnt', w=True)
        cmds.delete('scale_ctl')

    # freeze all the joints'  to remove rotation info and scale info
    for item in required_objects:
        cmds.makeIdentity(side + item, a=True, r=True, s=True)

    # Part 2 : Make the IK/FK setup and switch
    # create FKIK switch not too far from the shoulder joint (3 units)

    switch_offset_x = -1
    switch_offset_z = -3

    # define on which side of the body we are
    axis = cmds.xform(side + '_wrist_jnt', q=True, t=True, ws=True)
    if axis[0] > 0:
        switch_offset_x = -switch_offset_x

    shoulder_pos = cmds.xform(side + '_shoulder_jnt', q=True, t=True, ws=True)

    fkik_loc = cmds.spaceLocator(n=side + '_arm_FKIK_switch', p=shoulder_pos, a=True)
    cmds.xform(fkik_loc, cp=True)
    cmds.xform(fkik_loc, s=(0.5, 0.5, 0.5))

    rig_utils.colour_red(side + '_arm_FKIK_switch')
    cmds.xform(side + '_arm_FKIK_switch', r=True, t=(switch_offset_x, 0, switch_offset_z))

    # create IK hand controllers
    # get wrist joint position and orientation
    wrist_pos = tuple(cmds.xform(side + '_wrist_jnt', q=True, t=True, ws=True))
    wrist_rot = tuple(cmds.xform(side + '_wrist_jnt', q=True, ro=True, ws=True))

    cmds.circle(n=side + '_hand_IK_ctl', ch=False, d=1, s=3)
    cmds.xform(side + '_hand_IK_ctl', ro=(0, 90, 0))
    cmds.makeIdentity(side + '_hand_IK_ctl', a=True, r=True, s=True, t=True)
    cmds.group(n=side + '_hand_IK_offset')
    cmds.xform(side + '_hand_IK_offset', t=wrist_pos, ro=wrist_rot)

    rig_utils.colour_red(side + '_hand_IK_ctl')

    # Duplicate the arm joints twice (for IK and FK)
    cmds.duplicate(side + '_shoulder_jnt')
    cmds.duplicate(side + '_shoulder_jnt')

    # Rename the joints chains for IK and FK
    # FK
    cmds.rename(side + '_shoulder_jnt1', side + '_shoulder_FK_jnt')
    cmds.rename(side + '_shoulder_FK_jnt|' + side + '_elbow_jnt', side + '_elbow_FK_jnt')
    cmds.rename(side + '_elbow_FK_jnt|' + side + '_wrist_jnt', side + '_wrist_FK_jnt')

    # IK
    cmds.rename(side + '_shoulder_jnt2', side + '_shoulder_IK_jnt')
    cmds.rename(side + '_shoulder_IK_jnt|' + side + '_elbow_jnt', side + '_elbow_IK_jnt')
    cmds.rename(side + '_elbow_IK_jnt|' + side + '_wrist_jnt', side + '_wrist_IK_jnt')

    # constrain all the FK and IK joints to their respective skinning joint
    # IK
    cmds.parentConstraint(side + '_shoulder_IK_jnt', side + '_shoulder_jnt')
    cmds.parentConstraint(side + '_elbow_IK_jnt', side + '_elbow_jnt')
    cmds.parentConstraint(side + '_wrist_IK_jnt', side + '_wrist_jnt')

    # FK
    cmds.parentConstraint(side + '_shoulder_FK_jnt', side + '_shoulder_jnt')
    cmds.parentConstraint(side + '_elbow_FK_jnt', side + '_elbow_jnt')
    cmds.parentConstraint(side + '_wrist_FK_jnt', side + '_wrist_jnt')

    # set all the constraints' interpolation type to 'shortest'
    cmds.setAttr(side + '_shoulder_jnt_parentConstraint1' + '.interpType', 2)
    cmds.setAttr(side + '_elbow_jnt_parentConstraint1' + '.interpType', 2)
    cmds.setAttr(side + '_wrist_jnt_parentConstraint1' + '.interpType', 2)

    # create the FKIK switch attribute on the locator
    cmds.addAttr(side + '_arm_FKIK_switch', ln='FKIKSwitch', sn='FKIK', at='float', min=0.0, max=1.0, dv=0.0, k=True)

    # We need to create the FK controllers to be able to hook up their visibility attribute with the FKIK switch
    # create a list of the FK joints where we need controllers (not toe)

    def create_fk_ctl(part):
        """create standard FK controller on location"""

        # get jnt name
        jnt_name = side + '_' + part + '_FK_jnt'

        # get jnt coordinates
        part_pos = tuple(cmds.xform(jnt_name, q=True, t=True, ws=True))
        part_rot = tuple(cmds.xform(jnt_name, q=True, ro=True, ws=True))

        # create ctl
        ctl_name = cmds.circle(n=side + '_' + part + '_FK_ctl', ch=False)[0]
        cmds.xform(ctl_name, a=True, ro=(0, 90, 0))
        cmds.makeIdentity(ctl_name, t=True, r=True, s=True, a=True)

        # create offsetGrp
        grp_name = cmds.group(ctl_name, n=side + '_' + part + '_FK_offset')
        cmds.xform(grp_name, ro=part_rot, t=part_pos, a=True)

        # constrain ctl to jnt
        cmds.parentConstraint(ctl_name, jnt_name, mo=False)

    create_fk_ctl('shoulder')
    create_fk_ctl('elbow')
    create_fk_ctl('wrist')

    # make FK controller hierarchy
    cmds.parent(side + '_wrist_FK_offset', side + '_elbow_FK_ctl')
    cmds.parent(side + '_elbow_FK_offset', side + '_shoulder_FK_ctl')

    # lets colors the new controllers Blue
    rig_utils.colour_blue(side + '_shoulder_FK_ctl')
    rig_utils.colour_blue(side + '_elbow_FK_ctl')
    rig_utils.colour_blue(side + '_wrist_FK_ctl')

    # Now we need to hook up the FKIK switch to the constraints and controllers visibility using driven keys

    cmds.setDrivenKeyframe(side + '_shoulder_jnt_parentConstraint1.' + side + '_shoulder_FK_jntW1',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_shoulder_jnt_parentConstraint1.' + side + '_shoulder_FK_jntW1',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_shoulder_jnt_parentConstraint1.' + side + '_shoulder_IK_jntW0',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(side + '_shoulder_jnt_parentConstraint1.' + side + '_shoulder_IK_jntW0',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=1, v=0)

    cmds.setDrivenKeyframe(side + '_elbow_jnt_parentConstraint1.' + side + '_elbow_FK_jntW1',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_elbow_jnt_parentConstraint1.' + side + '_elbow_FK_jntW1',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_elbow_jnt_parentConstraint1.' + side + '_elbow_IK_jntW0',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(side + '_elbow_jnt_parentConstraint1.' + side + '_elbow_IK_jntW0',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=1, v=0)

    cmds.setDrivenKeyframe(side + '_wrist_jnt_parentConstraint1.' + side + '_wrist_FK_jntW1',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_wrist_jnt_parentConstraint1.' + side + '_wrist_FK_jntW1',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_wrist_jnt_parentConstraint1.' + side + '_wrist_IK_jntW0',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(side + '_wrist_jnt_parentConstraint1.' + side + '_wrist_IK_jntW0',
                           cd=side + '_arm_FKIK_switch.FKIKSwitch', dv=1, v=0)

    # IK controller
    cmds.setDrivenKeyframe(side + '_hand_IK_ctl.v', cd=side + '_arm_FKIK_switch.FKIKSwitch',
                           dv=0, v=1)
    cmds.setDrivenKeyframe(side + '_hand_IK_ctl.v', cd=side + '_arm_FKIK_switch.FKIKSwitch',
                           dv=1, v=0)

    # FK controllers
    cmds.setDrivenKeyframe(side + '_wrist_FK_ctl.v', cd=side + '_arm_FKIK_switch.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_wrist_FK_ctl.v', cd=side + '_arm_FKIK_switch.FKIKSwitch',
                           dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_elbow_FK_ctl.v', cd=side + '_arm_FKIK_switch.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_elbow_FK_ctl.v', cd=side + '_arm_FKIK_switch.FKIKSwitch',
                           dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_shoulder_FK_ctl.v', cd=side + '_arm_FKIK_switch.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_shoulder_FK_ctl.v', cd=side + '_arm_FKIK_switch.FKIKSwitch',
                           dv=1, v=1)

    # set preferred angle on shoulders
    cmds.joint(side + '_shoulder_jnt', e=True, spa=True)

    # create IK handle on right arm
    ik_name = cmds.ikHandle(n=side + '_arm_ikHandle', sj=side + '_shoulder_IK_jnt',
                            ee=side + '_wrist_IK_jnt', sol='ikRPsolver')
    cmds.setAttr(side + '_arm_ikHandle.snapEnable', 0)
    cmds.rename(ik_name[1], side + '_arm_effector')

    # constraint wrist orientation to ikHandle orientation
    cmds.orientConstraint(side + '_arm_ikHandle', side + '_wrist_IK_jnt', mo=True)

    # Now we need pole vectors
    # first we will need the location of the elbow joints and their orientations
    elbow_pos = cmds.xform(side + '_elbow_jnt', t=True, ws=True, q=True)
    elbow_orient = cmds.xform(side + '_elbow_jnt', ro=True, ws=True, q=True)

    # we create the pole vector controllers, we place them using the elbow joints' orientations
    pv_ctl = cmds.circle(n=side + '_armPV_ctl', d=1, s=3, ch=False)
    cmds.xform(pv_ctl[0], s=(0.5, 0.5, 0.5))
    cmds.makeIdentity(pv_ctl[0], a=True, t=True, r=True, s=True)

    cmds.group(n=side + '_armPV_offset')
    cmds.xform(side + '_armPV_offset', t=tuple(elbow_pos), ro=tuple(elbow_orient))
    cmds.xform(side + '_armPV_offset', t=(0, 2.5, 0), r=True, os=True)

    axis = cmds.xform(side + '_wrist_jnt', q=True, t=True, ws=True)
    if axis[0] > 0:
        cmds.xform(side + '_armPV_offset', t=(0, -5, 0), r=True, os=True)

    # reset armPV offset group rotations so the conrollers sit nicely in place with world axis
    cmds.xform(side + '_armPV_offset', ro=(0, 0, 0))

    # color the armPV controllers
    rig_utils.colour_yellow(side + '_armPV_ctl')

    # create Pole vector constraints
    cmds.poleVectorConstraint(side + '_armPV_ctl', side + '_arm_ikHandle')

    # hide the FKIK joints (I only hide the top joint so the rest disappears with it)
    rig_utils.hide(side + '_shoulder_IK_jnt')
    rig_utils.hide(side + '_shoulder_FK_jnt')
    rig_utils.hide(side + '_arm_ikHandle')

    # parent ikHandle to ik control
    cmds.parent(side + '_arm_ikHandle', side + '_hand_IK_ctl')
