# Use this after manually changing joint orient rotations
# Will realign translation axis with rotation axis

import maya.cmds as cmds

sel = cmds.ls(sl=True)

for x in sel:
    cmds.joint(e=True, zso=True)
    