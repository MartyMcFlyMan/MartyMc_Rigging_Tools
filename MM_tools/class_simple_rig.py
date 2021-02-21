import maya.cmds as cmds
from class_joint import JointController


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