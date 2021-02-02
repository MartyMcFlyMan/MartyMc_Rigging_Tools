import maya.cmds as cmds
import rig_utils as utils


class JointController:
    """The class contains all the requisite methods to create a controller on a joint,
    with an offset group"""
    def __init__(self, joint):
        """Get the processed joint's name"""
        self.name = joint

    def has_jnt(self):
        return self.name[-4:] == '_jnt'

    def get_nice_name(self):
        """Get joint name without the _jnt suffix"""
        if self.has_jnt():
            return self.name[:-4]
        return self.name

    def give_suffix(self, suffix):
        """Add suffix to object name, return new name"""
        return self.get_nice_name() + suffix

    def get_ctl_name(self):
        """Create the name of the control for the current joint"""
        return self.give_suffix('_ctl')

    def get_offset_name(self):
        """Create the name of the control for the current joint"""
        return self.give_suffix('_offset')

    def get_joint_translate(self):
        """Get current joint's position as a tuple"""
        return tuple(cmds.xform(self.name, q=True, t=True, ws=True))

    def get_joint_rotate(self):
        """Get current joint's rotation as a tuple"""
        joint_rot = tuple(cmds.xform(self.name, q=True, ro=True, ws=True))
        return joint_rot

    def create_ctl(self):
        """Create NURB circle"""
        ctl_name = self.get_ctl_name()
        cmds.circle(ch=False, n=ctl_name)
        cmds.xform(ctl_name, ro=(0, 90, 0))
        cmds.makeIdentity(ctl_name, a=True, t=True, r=True, s=True)
        utils.colour_blue(ctl_name)

    def create_offset(self):
        """Create offset group on control"""
        ctl_name = self.get_ctl_name()
        offset_name = self.get_offset_name()
        cmds.group(ctl_name, n=offset_name)

    def place_offset(self):
        """Move offset group to joint position and orientation"""
        offset_name = self.get_offset_name()
        cmds.xform(offset_name, ro=self.get_joint_rotate(), t=self.get_joint_translate(), a=True)

    def constraint_ctl(self):
        ctl_name = self.get_ctl_name()
        cmds.parentConstraint(ctl_name, self.name)

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
        self.root_joint = root_joint

    def has_children(self, joint):
        """Check if current joint has children"""
        return False if cmds.listRelatives(joint, c=True) is None else True

    def get_children(self, joint):
        """Return a list of the current joint's children"""
        if self.has_children(joint):
            return cmds.listRelatives(joint, c=True, type='joint')
        return []

    def get_parent_ctl(self, joint):
        parent_joint = cmds.listRelatives(joint, p=True, type='joint')[0]
        parent = JointController(parent_joint)
        return parent.get_ctl_name()

    def setup_joint(self, joint):
        """Create controller and offset on joint. Return offset name"""
        current_joint = JointController(joint)
        current_joint.create_ctl_on_joint()
        return current_joint.get_offset_name()

    def parent_controller(self, joint):
        """Parent the current joint's offset under its parent joint's control"""
        current_joint = JointController(joint)
        parent_ctl = self.get_parent_ctl(joint)
        child_offset = current_joint.get_offset_name()
        cmds.parent(child_offset, parent_ctl)

    def loop_joints(self, joint_list):
        """Setup joint controllers and hierarchy and feeds back joint's children in loop"""
        print joint_list
        for jnt in joint_list:
            print jnt
            if not self.has_children(jnt):
                continue
            self.setup_joint(jnt)
            self.parent_controller(jnt)
            children_list = self.get_children(jnt)
            self.loop_joints(children_list)

    def setup_rig(self):
        root = JointController(self.root_joint)
        root.create_ctl_on_joint()
        root_children = self.get_children(self.root_joint)
        self.loop_joints(root_children)
        cmds.group(root.get_offset_name(), n='ctl_grp')
        jnt_grp = cmds.group(root.name, n='jnt_grp')






