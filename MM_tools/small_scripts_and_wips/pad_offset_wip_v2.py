import maya.cmds as cmds

def snap(moved, target):
    """Get target info, give to moved object"""
    trash_cst = cmds.parentConstraint(target, moved, mo=False)
    cmds.delete(trash_cst)

sel = cmds.ls(sl=True)
for x in sel:
    newGroup = cmds.group(em=True, w=True, n=x+'_pad')
    snap(newGroup, x)
    cmds.makeIdentity(newGroup, t=True, a=True)
    parentNode = cmds.listRelatives(x, p=True, )

    if not parentNode:
        cmds.parent(x, newGroup)
    else:
        cmds.parent(newGroup, parentNode)
        cmds.parent(x, newGroup)
