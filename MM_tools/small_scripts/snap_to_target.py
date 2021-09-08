import maya.cmds as cmds

def snap(*args):
    """Get target info, give to moved object"""
    moved, target = cmds.ls(sl=True)
    trash_cst = cmds.parentConstraint(moved, target, mo=False)
    cmds.delete(trash_cst)
    
snap()