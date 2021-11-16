# Create all your set driven keys properly
# This script will allow you to offset the keys

# change the start and end times and the increment
# change the anim_curve_name and driven_attribute suffixes

import maya.cmds as cmds

sel = cmds.ls(sl=True)

start_time = 0
end_time = -20
time_increment = 2

for node in sel:
    anim_curve_name = node + '_rotateY'
    driven_attribute = node + '.rotateY'
    driver_attribute = 'main_fk_ctl.Coil'
    #print start_time, end_time
    #print cmds.keyframe(anim_curve_name, q=True, vc=True)
    cmds.keyframe(anim_curve_name, fc=end_time, a=True, o='over', index=(0,0))
    cmds.setDrivenKeyframe(driver_attribute, driven_attribute, dv=start_time, v=0)
    end_time -= time_increment
    start_time -= time_increment