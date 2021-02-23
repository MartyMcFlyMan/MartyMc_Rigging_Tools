import maya.cmds as cmds
import rig_utils as utils


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

        if '_' in self.short_name:
            self.middle_name = self.short_name.split('_')[1]
        self.prefix = self.short_name.split('_')[0]
        self.suffix = self.short_name.split('_')[-1]
        self.has_children = False if cmds.listRelatives(self.name, c=True, type='joint') is None else True
        self.ctl_name = self.nice_name + '_ctl'
        self.offset_name = self.nice_name + '_offset'
        self.ik_name = self.nice_name + '_ik_jnt'
        self.ik_handle_name = self.nice_name + '_IkHandle'
        self.effector_name = self.nice_name + '_effector'
        self.rfs_group_name = self.nice_name + '_RFS_grp'
        self.constraint_name = self.short_name + '_parentConstraint1'
        self.fk_name = self.nice_name + '_fk_jnt'
        self.fk_ctl = self.nice_name + '_fk_ctl'
        self.position = tuple(cmds.xform(self.name, q=True, t=True, ws=True))
        self.rotation = tuple(cmds.xform(self.name, q=True, ro=True, ws=True))
        self.scale = tuple(cmds.xform(self.name, q=True, s=True, ws=True))

    def hide(self):
        cmds.setAttr(self.name + '.v', 0)


class JointController(Joint):
    """The class contains all the requisite methods to create a controller on a joint,
    with an offset group"""
    def __init__(self, joint, rfs=False):
        """Get the processed joint's name"""
        self.rfs = rfs
        super(JointController, self).__init__(joint)
        if rfs:
            self.ctl_name = self.nice_name + '_RFS_ctl'
            self.offset_name = self.nice_name + '_RFS_offset'

    def create_ctl(self, name=None):
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
        if not self.rfs:
            self.constraint_ctl()