import maya.cmds as cmds
import rig_utils as utils
import operator
from class_joint import Joint
from class_joint import JointController
from class_simple_rig import SimpleRig
reload(utils)


class FkikLimb(object):
    def __init__(self, top_joint, mid_joint=None, end_joint=None):
        """Get the joints to make into FKIK setup, make them Joint objects.
        Set names for Fk and IK joint chains and make the Joint objects"""
        if mid_joint:
            self.top_joint = Joint(top_joint)
            self.mid_joint = Joint(mid_joint)
            self.end_joint = Joint(end_joint)
        else:
            self.top_joint = Joint(top_joint)
            self.mid_joint = Joint(cmds.listRelatives(self.top_joint.name, c=True, type='joint')[0])
            self.end_joint = Joint(cmds.listRelatives(self.mid_joint.name, c=True, type='joint')[0])
        self.pv_ctl = self.mid_joint.nice_name + '_pv_ctl'
        self.pv_offset = self.mid_joint.nice_name + '_pv_offset'

    @property
    def top_to_mid_dist(self):
        """Get distance between top and middle joint"""
        top_x, top_y, top_z = self.top_joint.position
        mid_x, mid_y, mid_z = self.mid_joint.position
        distance = ((top_x - mid_x) ** 2 + (top_y - mid_y) ** 2 + (top_z - mid_z) ** 2) ** 0.5
        return abs(float("{:.2f}".format(distance)))

    def duplicate_limb(self):
        """Duplicate limb joint chain twice"""
        cmds.duplicate(self.top_joint.name)
        cmds.duplicate(self.top_joint.name)

    def rename_duplicates(self):
        """Rename duplicate joint chains with _ik_jnt and _fk_jnt suffixes"""
        cmds.rename(self.top_joint.name + '1', self.top_joint.ik_name)
        for jnt in cmds.listRelatives(self.top_joint.ik_name, ad=True, type='joint', f=True):
            jnt = Joint(jnt)
            cmds.rename(jnt.name, jnt.nice_name + '_ik_jnt')

        cmds.rename(self.top_joint.name + '2', self.top_joint.fk_name)
        for jnt in cmds.listRelatives(self.top_joint.fk_name, ad=True, type='joint', f=True):
            jnt = Joint(jnt)
            cmds.rename(jnt.name, jnt.nice_name + '_fk_jnt')

    def delete_hand_joints(self):
        for x in cmds.listRelatives(self.end_joint.ik_name, c=True, type='joint'):
            cmds.delete(x)
        for x in cmds.listRelatives(self.end_joint.fk_name, c=True, type='joint'):
            cmds.delete(x)

    def constrain_duplicates(self):
        """Constrain top joint, then loop all children and constrain all who have children (all but tip joints)"""
        cmds.parentConstraint(self.top_joint.ik_name, self.top_joint.name)
        cmds.parentConstraint(self.top_joint.fk_name, self.top_joint.name)
        for jnt in cmds.listRelatives(self.top_joint.name, ad=True, type='joint', f=True):
            jnt = Joint(jnt)
            if jnt.has_children:
                cmds.parentConstraint(jnt.ik_name, jnt.name)
                cmds.parentConstraint(jnt.fk_name, jnt.name)
                cmds.setAttr(jnt.constraint_name + '.interpType', 2)
            else:
                continue

    def create_fk_ctls(self):
        """Use the SimpleRig class to create all the fk controllers on the fk joint chain."""
        fk_rig = SimpleRig(self.top_joint.fk_name)
        fk_rig.setup_rig(tips=True)

    def set_preferred_angle(self):
        cmds.joint(self.top_joint.name, e=True, spa=True)

    def hide_joints(self):
        top_ik = Joint(self.top_joint.ik_name)
        top_ik.hide()
        top_fk = Joint(self.top_joint.fk_name)
        top_fk.hide()


class FkikArm(FkikLimb):
    def __init__(self, shoulder_joint, elbow_joint=None, wrist_joint=None):
        """Initialise Joint objects and fkik switch name and position"""
        super(FkikArm, self).__init__(shoulder_joint, elbow_joint, wrist_joint)
        self.switch_pos = tuple(map(operator.add, self.top_joint.position, (0, 0, -self.top_to_mid_dist)))
        self.switch_name = self.top_joint.prefix + '_arm_fkikSwitch'
        self.switch_attr = self.switch_name + '.FKIKSwitch'
        self.ik_hand_ctl = self.end_joint.nice_name + '_IK_ctl'
        self.ik_hand_offset = self.end_joint.nice_name + '_IK_offset'
        self.hand_ik_handle = self.end_joint.nice_name + '_ikHandle'
        self.hand_group_name = self.end_joint.name.replace('wrist_jnt', 'hand_grp')

    def constrain_duplicates_arm(self):
        """Constrain top joint, then loop all children and constrain all who have children (all but tip joints)"""
        cmds.parentConstraint(self.top_joint.ik_name, self.top_joint.name)
        cmds.parentConstraint(self.top_joint.fk_name, self.top_joint.name)

        cmds.parentConstraint(self.mid_joint.ik_name, self.mid_joint.name)
        cmds.parentConstraint(self.mid_joint.fk_name, self.mid_joint.name)

        cmds.parentConstraint(self.end_joint.ik_name, self.end_joint.name)
        cmds.parentConstraint(self.end_joint.fk_name, self.end_joint.name)

    def create_fkik_switch(self):
        """Create arm fkik switch. Create its switch attribute."""
        cmds.spaceLocator(n=self.switch_name, p=self.switch_pos, a=True)
        utils.colour_red(self.switch_name)
        cmds.xform(self.switch_name, cp=True)
        scale_factor = [x * self.top_to_mid_dist for x in (0.2, 0.2, 0.2)]
        cmds.xform(self.switch_name, s=scale_factor)
        cmds.addAttr(self.switch_name, ln='FKIKSwitch', sn='FKIK', at='float', min=0.0, max=1.0, dv=0.0, k=True)

    def create_ik_foot_ctl(self):
        """Create the IK foot controller, rotate it and freeze its transformations. Create its offset group."""
        cmds.circle(n=self.ik_hand_ctl, ch=False, d=1, s=4)
        cmds.xform(self.ik_hand_ctl, ro=(0, 90, 0))
        cmds.makeIdentity(self.ik_hand_ctl, a=True, r=True, s=True, t=True)
        utils.colour_red(self.ik_hand_ctl)
        cmds.group(n=self.ik_hand_offset)
        cmds.xform(self.ik_hand_offset, t=self.end_joint.position, ro=self.end_joint.rotation)

    def switch_sdk_constraints(self):
        """Create all driven keys to choose which joint chain controls the main joint chain."""
        cmds.setDrivenKeyframe(self.top_joint.constraint_name + '.' + self.top_joint.ik_name + 'W0',
                               cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.top_joint.constraint_name + '.' + self.top_joint.ik_name + 'W0',
                               cd=self.switch_attr, dv=1, v=0)
        cmds.setDrivenKeyframe(self.top_joint.constraint_name + '.' + self.top_joint.fk_name + 'W1',
                               cd=self.switch_attr, dv=0, v=0)
        cmds.setDrivenKeyframe(self.top_joint.constraint_name + '.' + self.top_joint.fk_name + 'W1',
                               cd=self.switch_attr, dv=1, v=1)

        cmds.setDrivenKeyframe(self.mid_joint.constraint_name + '.' + self.mid_joint.ik_name + 'W0',
                               cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.mid_joint.constraint_name + '.' + self.mid_joint.ik_name + 'W0',
                               cd=self.switch_attr, dv=1, v=0)
        cmds.setDrivenKeyframe(self.mid_joint.constraint_name + '.' + self.mid_joint.fk_name + 'W1',
                               cd=self.switch_attr, dv=0, v=0)
        cmds.setDrivenKeyframe(self.mid_joint.constraint_name + '.' + self.mid_joint.fk_name + 'W1',
                               cd=self.switch_attr, dv=1, v=1)

        cmds.setDrivenKeyframe(self.end_joint.constraint_name + '.' + self.end_joint.ik_name + 'W0',
                               cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.end_joint.constraint_name + '.' + self.end_joint.ik_name + 'W0',
                               cd=self.switch_attr, dv=1, v=0)
        cmds.setDrivenKeyframe(self.end_joint.constraint_name + '.' + self.end_joint.fk_name + 'W1',
                               cd=self.switch_attr, dv=0, v=0)
        cmds.setDrivenKeyframe(self.end_joint.constraint_name + '.' + self.end_joint.fk_name + 'W1',
                               cd=self.switch_attr, dv=1, v=1)


    def switch_sdk_visibility(self):
        """Create driven keys linking fkik switch to controllers visibility"""
        cmds.setDrivenKeyframe(self.ik_hand_ctl + '.v', cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.ik_hand_ctl + '.v', cd=self.switch_attr, dv=1, v=0)

        cmds.setDrivenKeyframe(self.top_joint.fk_ctl + '.v', cd=self.switch_attr, dv=1, v=1)
        cmds.setDrivenKeyframe(self.top_joint.fk_ctl + '.v', cd=self.switch_attr, dv=0, v=0)

        cmds.setDrivenKeyframe(self.mid_joint.fk_ctl + '.v', cd=self.switch_attr, dv=1, v=1)
        cmds.setDrivenKeyframe(self.mid_joint.fk_ctl + '.v', cd=self.switch_attr, dv=0, v=0)

        cmds.setDrivenKeyframe(self.end_joint.fk_ctl + '.v', cd=self.switch_attr, dv=1, v=1)
        cmds.setDrivenKeyframe(self.end_joint.fk_ctl + '.v', cd=self.switch_attr, dv=0, v=0)

    def create_ik_handle(self):
        """create ik handle for arm"""
        ik_name = cmds.ikHandle(n=self.hand_ik_handle, sj=self.top_joint.ik_name,
                                ee=self.end_joint.ik_name, sol='ikRPsolver')
        cmds.setAttr(self.hand_ik_handle + '.snapEnable', 0)
        cmds.rename(ik_name[1], self.end_joint.nice_name + '_effector')

    def orient_constraint_ik_ctl(self):
        """Orient constraint ik hand control to ikHandle"""
        cmds.orientConstraint(self.hand_ik_handle, self.end_joint.ik_name, mo=True)

    def parent_ikhandle(self):
        cmds.parent(self.hand_ik_handle, self.ik_hand_ctl)

    def create_pv(self):
        cmds.circle(n=self.pv_ctl, d=1, s=3, ch=False)
        cmds.xform(self.pv_ctl, s=tuple([x*self.top_to_mid_dist for x in (0.2, 0.2, 0.2)]))
        cmds.makeIdentity(self.pv_ctl, a=True, t=True, r=True, s=True)

        cmds.group(n=self.pv_offset)
        cmds.xform(self.pv_offset, t=self.mid_joint.position, ro=self.mid_joint.rotation)
        cmds.xform(self.pv_offset, t=(0, self.top_to_mid_dist, 0), r=True, os=True)

        arm_pv_pos = cmds.xform(self.pv_offset, t=True, q=True)
        if arm_pv_pos[2] > 0:
            cmds.xform(self.pv_offset, t=(0, 2*-self.top_to_mid_dist, 0), r=True, os=True)
        cmds.poleVectorConstraint(self.pv_ctl, self.hand_ik_handle)

        utils.colour_yellow(self.pv_ctl)
        cmds.xform(self.pv_offset, ro=(0, 0, 0))

    def hide_ikHandles(self):
        utils.hide(self.hand_ik_handle)

    def create_hand_controls(self):
        """Create empty hand group with correct name. Place it on wrist joint.
        Then create all finger controls and place finger root control offsets in the empty hand group"""
        cmds.group(em=True, n=self.hand_group_name, w=True)
        cmds.xform(self.hand_group_name, t=self.end_joint.position)
        for x in cmds.listRelatives(self.end_joint.name, type='joint'):
            fk_rig = SimpleRig(x)
            base_ctl_offset = fk_rig.setup_rig()
            print base_ctl_offset
            cmds.parent(base_ctl_offset, self.hand_group_name)

    def constraint_hand_grp(self):
        cmds.pointConstraint(self.end_joint.name, self.hand_group_name, mo=True)
        cmds.orientConstraint(self.end_joint.name, self.hand_group_name, mo=True)

    def setup_arm(self):
        """Execute all commands in order to create the rig"""
        self.create_fkik_switch()
        self.create_ik_foot_ctl()
        self.duplicate_limb()
        self.rename_duplicates()
        self.constrain_duplicates_arm()
        self.delete_hand_joints()
        self.create_fk_ctls()
        self.switch_sdk_constraints()
        self.switch_sdk_visibility()
        self.set_preferred_angle()
        self.create_ik_handle()
        self.orient_constraint_ik_ctl()
        self.hide_joints()
        self.parent_ikhandle()
        self.create_pv()
        self.hide_ikHandles()

        self.create_hand_controls()
        self.constraint_hand_grp()

    def setup_hand(self):
        """Execute all commands in order to create the rig"""
        self.create_hand_controls()
        self.constraint_hand_grp()


class FkikLeg(FkikLimb):
    def __init__(self, hip_joint, knee_joint=None, ankle_joint=None):
        """Initialise Joint objects, fkik switch name and position and ik foot controller name"""
        super(FkikLeg, self).__init__(hip_joint, knee_joint, ankle_joint)
        switch_offset_x = self.top_to_mid_dist/2
        if self.top_joint.position[0] < 0:
            switch_offset_x = -switch_offset_x
        self.switch_pos = tuple(map(operator.add, self.top_joint.position, (switch_offset_x, 0, 0)))
        self.switch_name = self.top_joint.prefix + '_leg_fkikSwitch'
        self.switch_attr = self.switch_name + '.FKIKSwitch'
        self.ik_foot_ctl = self.end_joint.nice_name + '_IK_ctl'
        self.ik_foot_offset = self.end_joint.nice_name + '_IK_offset'
        self.foot_ik_handle = self.end_joint.nice_name + '_ikHandle'



    def create_fkik_switch(self):
        """Create the fkik switch, color it red, center its pivot, scale it using the top to mid distance value"""
        cmds.spaceLocator(n=self.switch_name, p=self.switch_pos, a=True)
        utils.colour_red(self.switch_name)
        cmds.xform(self.switch_name, cp=True)
        scale_factor = [x * self.top_to_mid_dist for x in (0.1, 0.1, 0.1)]
        cmds.xform(self.switch_name, s=scale_factor)
        cmds.addAttr(self.switch_name, ln='FKIKSwitch', sn='FKIK', at='float', min=0.0, max=1.0, dv=0.0, k=True)

    def create_ik_foot_ctl(self):
        """Create the IK foot controller, rotate it and freeze its transformations. Create its offset group."""
        cmds.circle(n=self.ik_foot_ctl, ch=False, d=1, s=4)
        cmds.xform(self.ik_foot_ctl, ro=(90, 0, 0))
        cmds.makeIdentity(self.ik_foot_ctl, a=True, r=True, s=True, t=True)
        utils.colour_red(self.ik_foot_ctl)
        cmds.group(n=self.ik_foot_offset)
        cmds.xform(self.ik_foot_offset, t=self.end_joint.position, ro=self.end_joint.rotation)

    def switch_sdk_constraints(self):
        """Create all driven keys to choose which joint chain controls the main joint chain."""
        cmds.setDrivenKeyframe(self.top_joint.constraint_name + '.' + self.top_joint.ik_name + 'W0',
                               cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.top_joint.constraint_name + '.' + self.top_joint.ik_name + 'W0',
                               cd=self.switch_attr, dv=1, v=0)
        cmds.setDrivenKeyframe(self.top_joint.constraint_name + '.' + self.top_joint.fk_name + 'W1',
                               cd=self.switch_attr, dv=0, v=0)
        cmds.setDrivenKeyframe(self.top_joint.constraint_name + '.' + self.top_joint.fk_name + 'W1',
                               cd=self.switch_attr, dv=1, v=1)
        for jnt in cmds.listRelatives(self.top_joint.name, ad=True, type='joint'):
            jnt = Joint(jnt)
            if jnt.has_children:
                cmds.setDrivenKeyframe(jnt.constraint_name + '.' + jnt.ik_name + 'W0',
                                       cd=self.switch_attr, dv=0, v=1)
                cmds.setDrivenKeyframe(jnt.constraint_name + '.' + jnt.ik_name + 'W0',
                                       cd=self.switch_attr, dv=1, v=0)
                cmds.setDrivenKeyframe(jnt.constraint_name + '.' + jnt.fk_name + 'W1',
                                       cd=self.switch_attr, dv=0, v=0)
                cmds.setDrivenKeyframe(jnt.constraint_name + '.' + jnt.fk_name + 'W1',
                                       cd=self.switch_attr, dv=1, v=1)
            else:
                continue

    def switch_sdk_visibility(self):
        """Create driven keys linking fkik switch to controllers visibility"""
        cmds.setDrivenKeyframe(self.ik_foot_ctl + '.v', cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.ik_foot_ctl + '.v', cd=self.switch_attr, dv=1, v=0)

        cmds.setDrivenKeyframe(self.top_joint.fk_ctl + '.v', cd=self.switch_attr, dv=1, v=1)
        cmds.setDrivenKeyframe(self.top_joint.fk_ctl + '.v', cd=self.switch_attr, dv=0, v=0)
        print self.top_joint.fk_ctl

        for jnt in cmds.listRelatives(self.top_joint.name, ad=True, type='joint'):
            jnt = Joint(jnt)
            if jnt.has_children:
                cmds.setDrivenKeyframe(jnt.fk_ctl + '.v', cd=self.switch_attr, dv=1, v=1)
                cmds.setDrivenKeyframe(jnt.fk_ctl + '.v', cd=self.switch_attr, dv=0, v=0)
            else:
                continue

    def create_ik_handle(self):
        """create ik handle for leg"""
        ik_name = cmds.ikHandle(n=self.foot_ik_handle, sj=self.top_joint.ik_name,
                                ee=self.end_joint.ik_name, sol='ikRPsolver', s='sticky')
        cmds.setAttr(self.foot_ik_handle + '.snapEnable', 0)
        cmds.rename(ik_name[1], self.end_joint.nice_name + '_effector')

    def orient_constraint_ik_ctl(self):
        """Orient constraint ik foot control to ikHandle"""
        cmds.orientConstraint(self.foot_ik_handle, self.end_joint.ik_name, mo=True)

    def parent_ikhandle(self):
        cmds.parent(self.foot_ik_handle, self.ik_foot_ctl)

    def create_pv(self):
        cmds.circle(n=self.pv_ctl, d=1, s=3, ch=False)
        cmds.xform(self.pv_ctl, s=tuple([x*self.top_to_mid_dist for x in (0.1, 0.1, 0.1)]))
        cmds.makeIdentity(self.pv_ctl, a=True, t=True, r=True, s=True)

        cmds.group(n=self.pv_offset)
        cmds.xform(self.pv_offset, t=self.mid_joint.position, ro=self.mid_joint.rotation)
        cmds.xform(self.pv_offset, t=(0, self.top_to_mid_dist, 0), r=True, os=True)

        leg_pv_pos = cmds.xform(self.pv_offset, t=True, q=True)
        if leg_pv_pos[2] < 0:
            cmds.xform(self.pv_offset, t=(0, -2*self.top_to_mid_dist, 0), r=True, os=True)
        cmds.poleVectorConstraint(self.pv_ctl, self.foot_ik_handle)

        utils.colour_yellow(self.pv_ctl)
        cmds.xform(self.pv_offset, ro=(0, 0, 0))
        cmds.parent(self.pv_ctl, self.ik_foot_ctl)

    def hide_ikHandles(self):
        utils.hide(self.foot_ik_handle)


    def setup_leg(self):
        """Execute all commands in order to create the rig"""
        self.create_fkik_switch()
        self.create_ik_foot_ctl()
        self.duplicate_limb()
        self.rename_duplicates()
        self.constrain_duplicates()
        self.create_fk_ctls()
        self.switch_sdk_constraints()
        self.switch_sdk_visibility()
        self.set_preferred_angle()
        self.create_ik_handle()
        self.orient_constraint_ik_ctl()
        self.hide_joints()
        self.parent_ikhandle()
        self.create_pv()
        self.hide_ikHandles()


class ReverseFoot(FkikLeg):
    """Inherits from class FkikLeg. Contains methods for adding a reverse foot setup to the fkik leg"""
    def __init__(self, hip_joint, knee_joint=None, ankle_joint=None):
        """Initialise Joint objects, fkik switch name and position and ik foot controller name"""
        super(ReverseFoot, self).__init__(hip_joint, knee_joint, ankle_joint)
        switch_offset_x = self.top_to_mid_dist/2
        if self.top_joint.position[0] < 0:
            switch_offset_x = -switch_offset_x
        self.switch_pos = tuple(map(operator.add, self.top_joint.position, (switch_offset_x, 0, 0)))
        self.switch_name = self.top_joint.prefix + '_leg_fkikSwitch'
        self.switch_attr = self.switch_name + '.FKIKSwitch'
        self.ik_foot_ctl = self.end_joint.nice_name + '_IK_ctl'
        self.ik_foot_offset = self.end_joint.nice_name + '_IK_offset'
        self.foot_ik_handle = self.end_joint.nice_name + '_ikHandle'

        self.ankle = JointController(self.end_joint.name, rfs=True)
        for x in cmds.listRelatives(self.end_joint.name, c=True, type='joint'):
            x = JointController(x, rfs=True)
            if x.has_children:
                self.ball = x
            else:
                self.heel = x
        self.toe = JointController(cmds.listRelatives(self.ball.name, c=True, type='joint')[0], rfs=True)
        self.top_rfs_group = self.ankle.prefix + '_foot_RFS_grp'

    def create_foot_ik(self):
        """Create Ik Handles on foot parts and rename effectors. Hide Ik Handles"""
        ankle_eff = cmds.ikHandle(n=self.ball.ik_handle_name, sj=self.ankle.ik_name,
                                       ee=self.ball.ik_name, sol='ikSCsolver', s='sticky')
        cmds.rename(ankle_eff[1], self.ball.effector_name)
        utils.hide(self.ball.ik_handle_name)

        ball_eff = cmds.ikHandle(n=self.toe.ik_handle_name, sj=self.ball.ik_name,
                                      ee=self.toe.ik_name, sol='ikSCsolver', s='sticky')
        cmds.rename(ball_eff[1], self.toe.effector_name)
        utils.hide(self.toe.ik_handle_name)

    def create_groups(self):
        """Create reverse foot setup groups and position them on their respective joints."""
        cmds.group(n=self.heel.rfs_group_name, w=True, em=True)
        cmds.xform(self.heel.rfs_group_name, t=self.heel.position, ws=True)

        cmds.group(n=self.toe.rfs_group_name, em=True, p=self.heel.rfs_group_name)
        cmds.xform(self.toe.rfs_group_name, t=self.toe.position, ws=True)

        cmds.group(n=self.ball.rfs_group_name, em=True, p=self.toe.rfs_group_name)
        cmds.xform(self.ball.rfs_group_name, t=self.ball.position, ws=True)

        cmds.group(n=self.ankle.rfs_group_name, em=True, p=self.ball.rfs_group_name)
        cmds.xform(self.ankle.rfs_group_name, t=self.ankle.position, ws=True)

        cmds.group(n=self.top_rfs_group, em=True, w=True)
        cmds.parent(self.heel.rfs_group_name, self.top_rfs_group)

    def create_controls(self):
        self.heel.create_ctl_on_joint()
        self.ball.create_ctl_on_joint()
        self.toe.create_ctl_on_joint()

    def create_hierarchy(self):
        cmds.parent(self.foot_ik_handle, self.ankle.rfs_group_name)
        cmds.parent(self.ball.ik_handle_name, self.ball.rfs_group_name)
        cmds.parent(self.toe.ik_handle_name, self.toe.rfs_group_name)

        cmds.parent(self.top_rfs_group, self.ik_foot_ctl)

        cmds.parent(self.heel.offset_name, self.top_rfs_group)
        cmds.parent(self.heel.rfs_group_name, self.heel.ctl_name)

        cmds.parent(self.toe.offset_name, self.heel.rfs_group_name)
        cmds.parent(self.toe.rfs_group_name, self.toe.ctl_name)

        cmds.parent(self.ball.offset_name, self.toe.rfs_group_name)
        cmds.parent(self.ball.rfs_group_name, self.ball.ctl_name)

    def switch_visibility_foot(self):
        """Create driven keys linking fkik switch to controllers visibility"""
        cmds.setDrivenKeyframe(self.heel.ctl_name + '.v', cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.heel.ctl_name + '.v', cd=self.switch_attr, dv=1, v=0)

        cmds.setDrivenKeyframe(self.ball.ctl_name + '.v', cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.ball.ctl_name + '.v', cd=self.switch_attr, dv=1, v=0)

        cmds.setDrivenKeyframe(self.toe.ctl_name + '.v', cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.toe.ctl_name + '.v', cd=self.switch_attr, dv=1, v=0)

    def setup_foot(self, leg=True):
        if leg:
            self.setup_leg()
        self.create_foot_ik()
        self.create_groups()
        self.create_controls()
        self.create_hierarchy()
        self.switch_visibility_foot()

