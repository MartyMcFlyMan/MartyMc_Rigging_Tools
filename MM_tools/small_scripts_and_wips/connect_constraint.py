#select all constraints, then fkik switch with already created fkik attribute
#change switch attribute name and IK/Fk w0 w1 to match your constraints

sel = cmds.ls(sl=True)
switch = sel[-1]
constraints_list = sel[:-1]

#CHANGE THESE STRINGS
switch_attribute_name = switch + '.splineik_fk'
ik_weight = '.w0'
fk_weight = '.w1'

reverse_node = cmds.shadingNode('reverse',asUtility=1)
cmds.connectAttr(switch_attribute_name, reverse_node + '.input.inputX')

for cst in constraints_list:
    cmds.connectAttr(switch_attribute_name, cst + ik_weight)
    cmds.connectAttr(reverse_node + '.output.outputX', cst + fk_weight)