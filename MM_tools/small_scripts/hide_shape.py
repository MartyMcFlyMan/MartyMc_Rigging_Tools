import maya.cmds as cmds

sel = cmds.ls(sl=True)
for x in sel:
    shape = cmds.listRelatives(x, s=True)
    cmds.hide(shape)
