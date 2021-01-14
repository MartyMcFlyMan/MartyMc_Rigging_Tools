
import maya.cmds as cmds
import sys

import rig_utils
reload(rig_utils)


def create_fkik_leg(side, *args):

    # Part 1 : Verify required objects
    # make a list of all the required objects and verify they exist
    required_objects = [
        '_hip_jnt',
        '_knee_jnt',
        '_ankle_jnt',
        '_ball_jnt',
        '_toe_jnt',
        '_heel_jnt'
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
            'A joint chain containing the following: hip, knee, ankle, ball, toe, heel\n' \
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
    # create FKIK switch not too far from the hip joint (3 units)

    switch_offset = 4

    axis = cmds.xform(side + '_ankle_jnt', q=True, t=True, ws=True)
    if axis[0] > 0:
        switch_offset = -switch_offset

    hip_pos = cmds.xform(side + '_hip_jnt', q=True, t=True, ws=True)

    fkik_loc = cmds.spaceLocator(n=side + '_leg_FKIK_switch', p=hip_pos, a=True)
    cmds.xform(fkik_loc, cp=True)
    cmds.xform(fkik_loc, s=(0.5, 0.5, 0.5))

    rig_utils.colour_red(side + '_leg_FKIK_switch')
    cmds.xform(side + '_leg_FKIK_switch', r=True, t=(switch_offset, 0, 0))

    # create IK foot controllers
    # get ankle joint position and orientation
    ankle_pos = tuple(cmds.xform(side + '_ankle_jnt', q=True, t=True, ws=True))
    ankle_rot = tuple(cmds.xform(side + '_ankle_jnt', q=True, ro=True, ws=True))

    cmds.circle(n=side + '_foot_IK_ctl', ch=False, d=1, s=4)
    cmds.xform(side + '_foot_IK_ctl', ro=(90, 0, 0))
    cmds.makeIdentity(side + '_foot_IK_ctl', a=True, r=True, s=True, t=True)
    cmds.group(n=side + '_foot_IK_offset')
    cmds.xform(side + '_foot_IK_offset', t=ankle_pos, ro=ankle_rot)

    rig_utils.colour_red(side + '_foot_IK_ctl')

    # Duplicate the leg joints twice (for IK and FK)
    cmds.duplicate(side + '_hip_jnt')
    cmds.duplicate(side + '_hip_jnt')

    # Rename the joints chains for IK and FK
    # FK
    cmds.rename(side + '_hip_jnt1', side + '_hip_FK_jnt')
    cmds.rename(side + '_hip_FK_jnt|' + side + '_knee_jnt', side + '_knee_FK_jnt')
    cmds.rename(side + '_knee_FK_jnt|' + side + '_ankle_jnt', side + '_ankle_FK_jnt')
    cmds.rename(side + '_ankle_FK_jnt|' + side + '_ball_jnt', side + '_ball_FK_jnt')
    cmds.rename(side + '_ball_FK_jnt|' + side + '_toe_jnt', side + '_toe_FK_jnt')
    cmds.rename(side + '_ankle_FK_jnt|' + side + '_heel_jnt', side + '_heel_FK_jnt')

    # IK
    cmds.rename(side + '_hip_jnt2', side + '_hip_IK_jnt')
    cmds.rename(side + '_hip_IK_jnt|' + side + '_knee_jnt', side + '_knee_IK_jnt')
    cmds.rename(side + '_knee_IK_jnt|' + side + '_ankle_jnt', side + '_ankle_IK_jnt')
    cmds.rename(side + '_ankle_IK_jnt|' + side + '_ball_jnt', side + '_ball_IK_jnt')
    cmds.rename(side + '_ball_IK_jnt|' + side + '_toe_jnt', side + '_toe_IK_jnt')
    cmds.rename(side + '_ankle_IK_jnt|' + side + '_heel_jnt', side + '_heel_IK_jnt')

    # constrain all the FK and IK joints to their respective skinning joint
    # IK
    cmds.parentConstraint(side + '_hip_IK_jnt', side + '_hip_jnt')
    cmds.parentConstraint(side + '_knee_IK_jnt', side + '_knee_jnt')
    cmds.parentConstraint(side + '_ankle_IK_jnt', side + '_ankle_jnt')
    cmds.parentConstraint(side + '_ball_IK_jnt', side + '_ball_jnt')

    # FK
    cmds.parentConstraint(side + '_hip_FK_jnt', side + '_hip_jnt')
    cmds.parentConstraint(side + '_knee_FK_jnt', side + '_knee_jnt')
    cmds.parentConstraint(side + '_ankle_FK_jnt', side + '_ankle_jnt')
    cmds.parentConstraint(side + '_ball_FK_jnt', side + '_ball_jnt')

    # set all the constraints' interpolation type to 'shortest'
    cmds.setAttr(side + '_hip_jnt_parentConstraint1' + '.interpType', 2)
    cmds.setAttr(side + '_knee_jnt_parentConstraint1' + '.interpType', 2)
    cmds.setAttr(side + '_ankle_jnt_parentConstraint1' + '.interpType', 2)
    cmds.setAttr(side + '_ball_jnt_parentConstraint1' + '.interpType', 2)

    # create the FKIK switch attribute on the locator
    cmds.addAttr(side + '_leg_FKIK_switch', ln='FKIKSwitch', sn='FKIK', at='float', min=0.0, max=1.0, dv=0.0, k=True)

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

    create_fk_ctl('hip')
    create_fk_ctl('knee')
    create_fk_ctl('ankle')
    create_fk_ctl('ball')

    # make FK controller hierarchy
    cmds.parent(side + '_ball_FK_offset', side + '_ankle_FK_ctl')
    cmds.parent(side + '_ankle_FK_offset', side + '_knee_FK_ctl')
    cmds.parent(side + '_knee_FK_offset', side + '_hip_FK_ctl')

    # lets colors the new controllers Blue
    rig_utils.colour_blue(side + '_hip_FK_ctl')
    rig_utils.colour_blue(side + '_knee_FK_ctl')
    rig_utils.colour_blue(side + '_ankle_FK_ctl')
    rig_utils.colour_blue(side + '_ball_FK_ctl')

    # Now we need to hook up the FKIK switch to the constraints and controllers visibility using driven keys

    cmds.setDrivenKeyframe(side + '_hip_jnt_parentConstraint1.' + side + '_hip_FK_jntW1',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_hip_jnt_parentConstraint1.' + side + '_hip_FK_jntW1',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_hip_jnt_parentConstraint1.' + side + '_hip_IK_jntW0',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(side + '_hip_jnt_parentConstraint1.' + side + '_hip_IK_jntW0',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=1, v=0)

    cmds.setDrivenKeyframe(side + '_knee_jnt_parentConstraint1.' + side + '_knee_FK_jntW1',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_knee_jnt_parentConstraint1.' + side + '_knee_FK_jntW1',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_knee_jnt_parentConstraint1.' + side + '_knee_IK_jntW0',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(side + '_knee_jnt_parentConstraint1.' + side + '_knee_IK_jntW0',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=1, v=0)

    cmds.setDrivenKeyframe(side + '_ball_jnt_parentConstraint1.' + side + '_ball_FK_jntW1',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_ball_jnt_parentConstraint1.' + side + '_ball_FK_jntW1',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_ball_jnt_parentConstraint1.' + side + '_ball_IK_jntW0',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(side + '_ball_jnt_parentConstraint1.' + side + '_ball_IK_jntW0',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=1, v=0)

    cmds.setDrivenKeyframe(side + '_ankle_jnt_parentConstraint1.' + side + '_ankle_FK_jntW1',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_ankle_jnt_parentConstraint1.' + side + '_ankle_FK_jntW1',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_ankle_jnt_parentConstraint1.' + side + '_ankle_IK_jntW0',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=0, v=1)
    cmds.setDrivenKeyframe(side + '_ankle_jnt_parentConstraint1.' + side + '_ankle_IK_jntW0',
                           cd=side + '_leg_FKIK_switch.FKIKSwitch', dv=1, v=0)

    # IK controller
    cmds.setDrivenKeyframe(side + '_foot_IK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=0, v=1)
    cmds.setDrivenKeyframe(side + '_foot_IK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=1, v=0)

    # FK controllers
    cmds.setDrivenKeyframe(side + '_ankle_FK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_ankle_FK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_knee_FK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_knee_FK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_hip_FK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_hip_FK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=1, v=1)

    cmds.setDrivenKeyframe(side + '_ball_FK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=0, v=0)
    cmds.setDrivenKeyframe(side + '_ball_FK_ctl.v', cd=side + '_leg_FKIK_switch.FKIKSwitch',
                           dv=1, v=1)
