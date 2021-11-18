import maya.cmds as cmds
import sys

from class_AnimCurve import *
reload(sys.modules['class_AnimCurve'])

if cmds.keyframe(q=True, sl=True):
    # get selected object name
    keyed_object = cmds.ls(sl=True)[0]

    # get animcurve node name
    animCurve_name = cmds.keyframe(q=True, n=True)[0]

    # get keyed attribute name
    keyed_attribute = cmds.listConnections(animCurve_name, p=True)[0]

    #create AnimCurve instance
    sphere_x = AnimCurve(keyed_object, keyed_attribute)

    sphere_x.animcurve_info()

    print sphere_x.get_backward_difference(9)



else:
    print 'no keyframes are selected yo'
