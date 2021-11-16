def reset_to_origin(node, node_pos=False):
    
    if not node:
        node = cmds.ls(sl=True)[0]
    
    # get the node's pivot position if it is not provided
    if not node_pos:
        node_pos = cmds.xform(node, query=True, worldSpace=True, rotatePivot=True)
        
    # translate node to origin
    # ensure translation is frozen
    cmds.makeIdentity(node, apply=True, translate=True, rotate=False, scale=False, normal=False)
    
    # offset to origin
    node_offset = [p * -1 for p in node_pos]
    cmds.xform(node, worldSpace=True, translation=node_offset)
    
    # zero rotates, then freezes all transforms
    cmds.setAttr(node + '.rotate', 0, 0, 0)
    cmds.makeIdentity(node, apply=True, translate=True, rotate=False, scale=False, normal=False)

reset_to_origin(node=False)