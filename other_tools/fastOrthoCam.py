import maya.cmds as cmds

# Simple script for fast orthographic view, put this in a shortcut or something

isOrtho = cmds.getAttr('persp.orthographic')

if isOrtho:
    cmds.setAttr('persp.orthographic', 0)

else:
    camRX, camRY, camRZ = cmds.xform('persp', q=True, ro=True)

    newRX = 90 * round((camRX % 360)/90)
    newRY = 90 * round((camRY % 360)/90)

    cmds.xform('persp', ro=(newRX, newRY, camRZ))

    cmds.setAttr('persp' + '.orthographic', 1)
