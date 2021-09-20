import maya.cmds as cmds

sel = cmds.ls(sl=True)
print sel

for x in range(2, 10):
    R_cluster_name = 'R_eye_cluster_' + str(x)
    cmds.cluster('R_eye_curve.cv[' + str(x) + ']', n='R_eye_cluster_' + str(x))
    cmds.rename(R_cluster_name)
    Mid_cluster_name = 'Mid_eye_cluster_' + str(x)
    cmds.cluster('Mid_eye_curve.cv[' + str(x) + ']', n='Mid_eye_cluster_' + str(x))
    cmds.rename(Mid_cluster_name)
    L_cluster_name = 'L_eye_cluster_' + str(x)
    cmds.cluster('L_eye_curve.cv[' + str(x) + ']', n='L_eye_cluster_' + str(x))
    cmds.rename(L_cluster_name)