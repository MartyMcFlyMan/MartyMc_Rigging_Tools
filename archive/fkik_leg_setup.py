
import maya.cmds as cmds

import MM_tools.rig_utils
reload(MM_tools.rig_utils)


def setup_fkik_leg(hip=None, knee=None, ankle=None, *args):

    if cmds.objExists('scale_ctl'):
        cmds.parent('COG_jnt', w=True)
        cmds.delete('scale_ctl')

    # freeze all the joints'  to remove rotation info and scale info
    cmds.makeIdentity(hip, a=True, r=True, s=True)
    cmds.makeIdentity(knee, a=True, r=True, s=True)
    cmds.makeIdentity(ankle, a=True, r=True, s=True)

    # get joints side prefix (it is the first character of the joint strings_
    side = hip[0] + '_'

    def get_middle_name(jnt):
        full_name_list = jnt.split('|')
        short_name_list = full_name_list[-1].split('_')
        middle_name = short_name_list[-2]
        return middle_name

    def get_short_name(jnt):
        full_name_list = jnt.split('|')
        short_name = full_name_list[-1]
        return short_name

    hip_mid = get_middle_name(hip)
    leg_name = side + hip_mid.replace('hip', 'leg')
    foot_name = side + hip_mid.replace('hip', 'foot')

    hip_short = get_short_name(hip)
    knee_short = get_short_name(knee)
    ankle_short = get_short_name(ankle)

    # Part 2 : Make the IK/FK setup and switch
    # create FKIK switch not too far from the hip joint (3 units)

    switch_offset_x = -1
    switch_offset_z = 3

    axis = cmds.xform(ankle, q=True, t=True, ws=True)
    if axis[0] > 0:
        switch_offset_x = -switch_offset_x

    hip_pos = cmds.xform(hip, q=True, t=True, ws=True)

    fkik_loc = cmds.spaceLocator(n=leg_name + 'FKIK_switch', p=hip_pos, a=True)
    fkik_loc = ''.join(fkik_loc)
    cmds.xform(fkik_loc, cp=True)
    cmds.xform(fkik_loc, s=(0.5, 0.5, 0.5))

    MM_tools.rig_utils.colour_red(fkik_loc)
    cmds.xform(fkik_loc, r=True, t=(switch_offset_x, 0, switch_offset_z))

    # create IK foot controllers
    # get ankle joint position and orientation
    ankle_pos = tuple(cmds.xform(ankle, q=True, t=True, ws=True))
    ankle_rot = tuple(cmds.xform(ankle, q=True, ro=True, ws=True))

    foot_ctl = cmds.circle(n=foot_name + '_IK_ctl', ch=False, d=1, s=4)[0]
    cmds.xform(foot_ctl, ro=(90, 0, 0))
    cmds.makeIdentity(foot_ctl, a=True, r=True, s=True, t=True)
    cmds.group(n=foot_name + '_IK_offset')
    cmds.xform(foot_name + '_IK_offset', t=ankle_pos, ro=ankle_rot)

    MM_tools.rig_utils.colour_red(foot_ctl)

    # Duplicate the leg joints twice (for IK and FK)
    cmds.duplicate(hip)
    cmds.duplicate(hip)

    # Rename the joints chains for IK and FK
    # FK
    hip_fk = cmds.rename(hip + '1', hip_short[:-4] + '_FK_jnt')
    knee_fk = cmds.rename(hip_fk + '|' + knee_short, knee_short[:-4] + '_FK_jnt')
    ankle_fk = cmds.rename(knee_fk + '|' + ankle_short, ankle_short[:-4] + '_FK_jnt')

    # IK
    hip_ik = cmds.rename(hip + '2', hip_short[:-4] + '_IK_jnt')
    knee_ik = cmds.rename(hip_ik + '|' + knee_short, knee_short[:-4] + '_IK_jnt')
    ankle_ik = cmds.rename(knee_ik + '|' + ankle_short, ankle_short[:-4] + '_IK_jnt')

    # constrain all the FK and IK joints to their respective skinning joint
    # IK
    hip_cst = cmds.parentConstraint(hip_ik, hip)
    hip_cst = ''.join(hip_cst)
    knee_cst = cmds.parentConstraint(knee_ik, knee)
    knee_cst = ''.join(knee_cst)
    ankle_cst = cmds.parentConstraint(ankle_ik, ankle)
    ankle_cst = ''.join(ankle_cst)

    # FK
    cmds.parentConstraint(hip_fk, hip)
    cmds.parentConstraint(knee_fk, knee)
    cmds.parentConstraint(ankle_fk, ankle)

    # set all the constraints' interpolation type to 'shortest'
    cmds.setAttr(hip_cst + '.interpType', 2)
    cmds.setAttr(knee_cst + '.interpType', 2)
    cmds.setAttr(ankle_cst + '.interpType', 2)

    # create the FKIK switch attribute on the locator
    cmds.addAttr(leg_name + 'FKIK_switch', ln='FKIKSwitch', sn='FKIK', at='float', min=0.0, max=1.0, dv=0.0, k=True)

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

        return ctl_name, grp_name

    hip_fk_ctl, hip_fk_offset = create_fk_ctl(hip_fk)
    knee_fk_ctl, knee_fk_offset = create_fk_ctl(knee_fk)
    ankle_fk_ctl, ankle_fk_offset = create_fk_ctl(ankle_fk)

    # make FK controller hierarchy
    cmds.parent(ankle_fk_offset, knee_fk_ctl)
    cmds.parent(knee_fk_offset, hip_fk_ctl)

    # lets colors the new controllers Blue
    MM_tools.rig_utils.colour_blue(hip_fk_ctl)
    MM_tools.rig_utils.colour_blue(knee_fk_ctl)
    MM_tools.rig_utils.colour_blue(ankle_fk_ctl)

    # Now we need to hook up the FKIK switch to the constraints and controllers visibility using driven keys

    fkik_switch = fkik_loc + '.FKIKSwitch'

    cmds.setDrivenKeyframe(hip_cst + '.' + hip_fk + 'W1',
                           cd=fkik_switch, dv=0, v=0)
    cmds.setDrivenKeyframe(hip_cst + '.' + hip_fk + 'W1',
                           cd=fkik_switch, dv=1, v=1)

    cmds.setDrivenKeyframe(hip_cst + '.' + hip_ik + 'W0',
                           cd=fkik_switch, dv=0, v=1)
    cmds.setDrivenKeyframe(hip_cst + '.' + hip_ik + 'W0',
                           cd=fkik_switch, dv=1, v=0)

    cmds.setDrivenKeyframe(knee_cst + '.' + knee_fk + 'W1',
                           cd=fkik_switch, dv=0, v=0)
    cmds.setDrivenKeyframe(knee_cst + '.' + knee_fk + 'W1',
                           cd=fkik_switch, dv=1, v=1)

    cmds.setDrivenKeyframe(knee_cst + '.' + knee_ik + 'W0',
                           cd=fkik_switch, dv=0, v=1)
    cmds.setDrivenKeyframe(knee_cst + '.' + knee_ik + 'W0',
                           cd=fkik_switch, dv=1, v=0)

    cmds.setDrivenKeyframe(ankle_cst + '.' + ankle_fk + 'W1',
                           cd=fkik_switch, dv=0, v=0)
    cmds.setDrivenKeyframe(ankle_cst + '.' + ankle_fk + 'W1',
                           cd=fkik_switch, dv=1, v=1)

    cmds.setDrivenKeyframe(ankle_cst + '.' + ankle_ik + 'W0',
                           cd=fkik_switch, dv=0, v=1)
    cmds.setDrivenKeyframe(ankle_cst + '.' + ankle_ik + 'W0',
                           cd=fkik_switch, dv=1, v=0)

    # IK controller
    cmds.setDrivenKeyframe(foot_name + '_IK_ctl.v', cd=fkik_switch,
                           dv=0, v=1)
    cmds.setDrivenKeyframe(foot_name + '_IK_ctl.v', cd=fkik_switch,
                           dv=1, v=0)

    # FK controllers
    cmds.setDrivenKeyframe(ankle_fk_ctl + '.v', cd=fkik_switch,
                           dv=0, v=0)
    cmds.setDrivenKeyframe(ankle_fk_ctl + '.v', cd=fkik_switch,
                           dv=1, v=1)

    cmds.setDrivenKeyframe(knee_fk_ctl + '.v', cd=fkik_switch,
                           dv=0, v=0)
    cmds.setDrivenKeyframe(knee_fk_ctl + '.v', cd=fkik_switch,
                           dv=1, v=1)

    cmds.setDrivenKeyframe(hip_fk_ctl + '.v', cd=fkik_switch,
                           dv=0, v=0)
    cmds.setDrivenKeyframe(hip_fk_ctl + '.v', cd=fkik_switch,
                           dv=1, v=1)

    # set preferred angle on hips
    cmds.joint(hip, e=True, spa=True)

    # create IK handle on right leg
    ik_name = cmds.ikHandle(n=leg_name + '_ikHandle', sj=hip_ik,
                            ee=ankle_ik, sol='ikRPsolver', s='sticky')
    cmds.setAttr(leg_name + '_ikHandle.snapEnable', 0)
    cmds.rename(ik_name[1], leg_name + '_effector')

    # constraint ankle orientation to ikHandle orientation
    cmds.orientConstraint(leg_name + '_ikHandle', ankle_ik, mo=True)

    # Now we need pole vectors
    # first we will need the location of the knee joints and their orientations
    knee_pos = cmds.xform(knee, t=True, ws=True, q=True)
    knee_orient = cmds.xform(knee, ro=True, ws=True, q=True)

    #  we create the pole vector controllers, we place them using the knee joints' orientations
    pv_ctl = cmds.circle(n=leg_name + 'PV_ctl', d=1, s=3, ch=False)
    cmds.xform(pv_ctl[0], s=(0.5, 0.5, 0.5))
    cmds.makeIdentity(pv_ctl[0], a=True, t=True, r=True, s=True)

    pv_offset = cmds.group(n=leg_name + 'PV_offset')
    cmds.xform(pv_offset, t=tuple(knee_pos), ro=tuple(knee_orient))
    cmds.xform(pv_offset, t=(0, 5, 0), r=True, os=True)

    leg_pv_pos = cmds.xform(pv_offset, t=True, q=True)

    if leg_pv_pos[2] < 0:
        cmds.xform(pv_offset, t=(0, -10, 0), r=True, os=True)

    # reset legPV offset group rotations so the controllers sit nicely in place with world axis
    cmds.xform(pv_offset, ro=(0, 0, 0))

    # color the legPV controllers
    MM_tools.rig_utils.colour_yellow(pv_ctl[0])

    # create Pole vector constraints
    cmds.poleVectorConstraint(pv_ctl[0], leg_name + '_ikHandle')

    # hide the FKIK joints (I only hide the top joint so the rest disappears with it)
    MM_tools.rig_utils.hide(hip_ik)
    MM_tools.rig_utils.hide(hip_fk)

    # parent ikhandle under foot ctl
    cmds.parent(leg_name + '_ikHandle', foot_name + '_IK_ctl')

    #parent pole vector under ik foot ctl
    cmds.parent(pv_offset, foot_name + '_IK_ctl')

    #orient constraint
