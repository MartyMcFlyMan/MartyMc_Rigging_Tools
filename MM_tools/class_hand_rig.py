import maya.cmds as cmds
import rig_utils as utils
from class_joint import Joint
from class_joint import JointController
from class_simple_rig import SimpleRig
reload(utils)

class HandSetup(object):
    def __init__(self):
        pass


#create controller object

def create_hand_driver(name, *args):
    """Create controller and add attributes"""
    cmds.spaceLocator(n=name)
    utils.colour_yellow(name)
    cmds.xform(name, cp=True)
    #scale_factor = [x * self.top_to_mid_dist for x in (0.2, 0.2, 0.2)]
    #cmds.xform(self.switch_name, s=scale_factor)
    cmds.addAttr(name, ln='pinkyCurl', at='float', min=-10.0, max=10.0, k=True)
    cmds.addAttr(name, ln='ringCurl', at='float', min=-10.0, max=10.0, k=True)
    cmds.addAttr(name, ln='middleCurl', at='float', min=-10.0, max=10.0, k=True)
    cmds.addAttr(name, ln='indexCurl', at='float', min=-10.0, max=10.0, k=True)
    cmds.addAttr(name, ln='thumbCurl', at='float', min=-10.0, max=10.0, k=True)
    cmds.addAttr(name, ln='thumbCup', at='float', min=-10.0, max=10.0, k=True)
    cmds.addAttr(name, ln='handCup', at='float', min=-10.0, max=10.0, k=True)
    cmds.addAttr(name, ln='hand', at='float', min=-10.0, max=10.0, k=True)

def driver_finger_sdk(side, name, *args):
    phalanx_list = ['1', '2', '3']
    finger_list = ['middle', 'index', 'thumb', 'pinky', 'ring']
    for x in phalanx_list:
        for y in finger_list:
            cmds.setDrivenKeyframe(side + y + 'Finger' + x + '_driver' + '.ry', cd=name + '.' + y + 'Curl', dv=0, v=0)
            cmds.setDrivenKeyframe(side + y + 'Finger' + x + '_driver' + '.ry', cd=name + '.' + y + 'Curl', dv=-10, v=-100)
            cmds.setDrivenKeyframe(side + y + 'Finger' + x + '_driver' + '.ry', cd=name + '.' + y + 'Curl', dv=10, v=100)


def create_driver_groups():
    sel = cmds.ls(sl=True)
    for x in sel:
        parent = cmds.listRelatives(x, p=True)[0]
        pos = tuple(cmds.xform(x, q=True, t=True, ws=True))
        group = cmds.group(n=x.replace('ctl', 'driver'), w=True)
        cmds.xform(x, t=pos)
        cmds.parent(group, parent)
        cmds.select(d=True)



