import maya.cmds as cmds

sel = cmds.ls(sl=True)
cmds.select(cl=True)

for x in sel:
    cvs = cmds.getAttr(x + '.spans')
    cmds.select(x + '.cv[0:' + str(cvs) + ']', add=True)