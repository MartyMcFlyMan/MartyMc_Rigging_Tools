#create constraints on twin joint chains
#select initial joint chain, then new joint chain


import maya.cmds as cmds

#  Adjust name index for jnt name match in both chains
#  e.g: L_eye2_jnt would be index 1 for eye2
name_index = 1

initial_chain = cmds.ls(sl=True)[0]
new_chains = cmds.ls(sl=True)[1:]

#create list of binded joints
cmds.select(initial_chain, hi=True)
initial_list = cmds.ls(sl=True)

#create list of lists of binding joints

new_chains_list = []

for chain in new_chains:
    cmds.select(chain, hi=True)
    new_chains_list.append(cmds.ls(sl=True))


for chain in new_chains_list:
    for old_jnt in initial_list:
        for new_jnt in chain:
            if new_jnt.split('_')[name_index] == old_jnt.split('_')[name_index]:
                cmds.parentConstraint(new_jnt, old_jnt, mo=True)