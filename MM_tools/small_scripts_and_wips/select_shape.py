import maya.cmds as cmds

sel = cmds.ls(sl=True)
cmds.select(cl=True)

for x in sel:
    shapeNode = cmds.listRelatives(x, s=True)
    cmds.select(shapeNode, add=True)