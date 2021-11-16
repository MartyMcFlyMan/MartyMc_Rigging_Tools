# AnimCurve Queryier

import maya.cmds as cmds

# get selected object name
keyed_object = cmds.ls(sl=True)[0]
print 'Keyed object:', keyed_object

# get animcurve node name
animCurve_name = cmds.keyframe(q=True, n=True)[0]
print 'AnimCurve node name:', animCurve_name

# get keyed attribute name
keyed_attribute = cmds.listConnections(animCurve_name, p=True)[0]
print 'Keyed attribute:', keyed_attribute

# get time value of selected keys
key_time = cmds.keyframe(sl=True, q=True)
print 'Key time:', key_time

# get value of selected keys
key_values = cmds.keyframe(sl=True, q=True, vc=True)
print 'Key values:', key_values

# get index of selected keys
key_index_list = cmds.keyframe(sl=True, q=True, iv=True)
key_index_list = [int(x) for x in key_index_list] # change index datatype from Long to int
print 'Key index list:', key_index_list

# get total keys amount
total_keys = cmds.keyframe(keyed_attribute, q=True, keyframeCount=True)
print 'Total keys on attribute:', total_keys

# get total keys selected
total_keys_sel = cmds.keyframe(keyed_attribute, sl=True, q=True, keyframeCount=True)
print 'Total keys selected:', total_keys_sel

# get last selected key index
last_selected_key_index = key_index_list[-1]
print 'Last selected key index:', last_selected_key_index

# get last key index
last_key_index = total_keys - 1
print 'Last key index:', last_key_index

# select key from its index
# index is a range, 0, 0 means from 0 to 0 so only the first key
# you need the relative flag because otherwise it will try to move the key by 0
# and since the absolute flag is deafult it will set the key at time 0
cmds.keyframe(keyed_attribute, index=(1, 1), r=True)

# get key value from index
cmds.keyframe(keyed_attribute, index=(1, 1), vc=True, q=True)

def create_key_value_dict():
    keyframes_dict = {}
    if len(key_index_list) == len(key_values):
        for i in range(len(key_index_list)):
            keyframes_dict[key_index_list[i]] = key_values[i]
        print keyframes_dict
        return keyframes_dict
        
    else:
        print "the amount of keys and values do not match"

create_key_value_dict()
