#create the rotation order switch attribute on selected controllers

import maya.cmds as cmds

ctls = cmds.ls(sl=True)

for ctl in ctls:
    current_ro = cmds.getAttr(ctl + ".rotateOrder")
    cmds.addAttr(ctl, ln="rotational_order_attr", sn="roa", nn="Rotational Order",\
        at="enum", enumName="xyz:yzx:zxy:xzy:yxz:zyx", r=1, w=1, k=1)
    cmds.connectAttr(ctl + ".roa", ctl + ".ro")
    cmds.setAttr(ctl + '.roa', current_ro)