import maya.cmds as cmds

shapes = cmds.ls(s=True)

print shapes

for shape in shapes:
    if 'ctl' in shape:
        cmds.setAttr(shape + '.isHistoricallyInteresting', 0)