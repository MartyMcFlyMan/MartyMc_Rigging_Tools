import maya.cmds as cmds
import rig_utils as utils
import operator
reload(utils)


class Joint(object):
    def __init__(self, joint_name):
        """Initialize joint name, short_name and nice_name variable,
         which holds the name of the joint without the _jnt suffix"""
        self.name = joint_name
        self.short_name = self.name.split('|')[-1]
        if self.short_name[-4:] == '_jnt':
            self.nice_name = self.short_name[:-4]
        else:
            self.nice_name = self.short_name

    @property
    def middle_name(self):
        """Hold the middle part of a name"""
        return self.short_name.split('_')[1]

    @property
    def prefix(self):
        """Hold the prefix part of a name."""
        return self.short_name.split('_')[0]

    @property
    def suffix(self):
        """Hold the prefix part of a name."""
        return self.short_name.split('_')[-1]

    @property
    def has_children(self):
        """Return True if joint has child joint"""
        return False if cmds.listRelatives(self.name, c=True, type='joint') is None else True

    @property
    def ctl_name(self):
        """Hold the name of the control for the current joint"""
        return self.nice_name + '_ctl'

    @property
    def offset_name(self):
        """Hold the name of the offset for the current joint"""
        return self.nice_name + '_offset'

    @property
    def ik_name(self):
        """Hold the name of the control for the current joint"""
        return self.nice_name + '_ik_jnt'

    @property
    def constraint_name(self):
        """Hold the name of the control for the current joint"""
        return self.short_name + '_parentConstraint1'

    @property
    def fk_name(self):
        """Hold the name of the control for the current joint"""
        return self.nice_name + '_fk_jnt'

    @property
    def fk_ctl(self):
        """Hold the name of the control for the current fk joint"""
        return self.nice_name + '_fk_ctl'

    @property
    def position(self):
        """Hold current joint's position as a tuple"""
        return tuple(cmds.xform(self.name, q=True, t=True, ws=True))

    @property
    def rotation(self):
        """Hold current joint's rotation as a tuple"""
        return tuple(cmds.xform(self.name, q=True, ro=True, ws=True))

    @property
    def scale(self):
        """Hold current joint's rotation as a tuple"""
        return tuple(cmds.xform(self.name, q=True, s=True, ws=True))

    def hide(self):
        cmds.setAttr(self.name + '.v', 0)


class JointController(Joint):
    """The class contains all the requisite methods to create a controller on a joint,
    with an offset group"""
    def __init__(self, joint):
        """Get the processed joint's name"""
        super(JointController, self).__init__(joint)

    def create_ctl(self):
        """Create NURB circle"""
        cmds.circle(ch=False, n=self.ctl_name)
        cmds.xform(self.ctl_name, ro=(0, 90, 0))
        cmds.makeIdentity(self.ctl_name, a=True, t=True, r=True, s=True)
        utils.colour_blue(self.ctl_name)

    def create_offset(self):
        """Create offset group on control"""
        cmds.group(self.ctl_name, n=self.offset_name)

    def place_offset(self):
        """Move offset group to joint position and orientation"""
        cmds.xform(self.offset_name, ro=self.rotation, t=self.position, a=True)

    def constraint_ctl(self):
        cmds.parentConstraint(self.ctl_name, self.name)

    def create_ctl_on_joint(self):
        """Creates the controller on the joint with its offset group"""
        self.create_ctl()
        self.create_offset()
        self.place_offset()
        self.constraint_ctl()


class SimpleRig:
    """The class contains all the necessary methods to create a simple FK rig from joints"""
    def __init__(self, root_joint):
        """Get the root joint name"""
        self.root = JointController(root_joint)

    def has_children(self, joint):
        """Check if current joint has children"""
        return False if cmds.listRelatives(joint, c=True, type='joint') is None else True

    def get_children(self, joint):
        """Return a list of the current joint's children"""
        if self.has_children(joint):
            return cmds.listRelatives(joint, c=True, type='joint')
        return []

    def get_parent_ctl(self, joint):
        parent = JointController(cmds.listRelatives(joint, p=True, type='joint')[0])
        return parent.ctl_name

    def setup_joint(self, joint):
        """Create controller and offset on joint. Return offset name"""
        current_joint = JointController(joint)
        current_joint.create_ctl_on_joint()
        return current_joint.offset_name

    def parent_controller(self, joint):
        """Parent the current joint's offset under its parent joint's control"""
        current_joint = JointController(joint)
        parent_ctl = self.get_parent_ctl(joint)
        child_offset = current_joint.offset_name
        cmds.parent(child_offset, parent_ctl)

    def loop_joints(self, joint_list):
        """Setup joint controllers and hierarchy and feeds back joint's children in loop"""
        for jnt in joint_list:
            if not self.has_children(jnt):
                continue
            self.setup_joint(jnt)
            self.parent_controller(jnt)
            children_list = self.get_children(jnt)
            self.loop_joints(children_list)

    def setup_rig(self):
        """Create controller on root joint,
        then loop the whole skeleton and create all controllers"""
        self.root.create_ctl_on_joint()
        root_children = self.get_children(self.root.name)
        self.loop_joints(root_children)


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
        fk_rig.setup_rig()

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
        cmds.setDrivenKeyframe(self.ik_hand_ctl + '.v', cd=self.switch_attr, dv=0, v=1)
        cmds.setDrivenKeyframe(self.ik_hand_ctl + '.v', cd=self.switch_attr, dv=1, v=0)

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

    def rig_fkik_arm(self):
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

    def hide_ikHandles(self):
        utils.hide(self.foot_ik_handle)

    def rig_fkik_leg(self):
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


