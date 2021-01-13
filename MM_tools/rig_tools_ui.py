
from maya import cmds
import os
from functools import partial
import rig_utils
import create_base_skel
import fkik_switch
import ik_leg
import reverse_foot
import lock_ctls

reload(rig_utils)
reload(create_base_skel)
reload(ik_leg)
reload(reverse_foot)
reload(fkik_switch)
reload(lock_ctls)


def ui():

    #check if window exists, if it does, then delete it and create a new one to avoid multiple windows.
    if cmds.window('my_rigging_tools', exists = True):
        cmds.deleteUI('my_rigging_tools')

    # Create a window
    window = cmds.window('my_rigging_tools',  title="My Rigging Tools", w=300, h=250, mxb = False, mnb = False)

    #setup tabs
    tabs = cmds.tabLayout()



    tab_child1 = cmds.columnLayout()

    #create banner image
    # find the relative path to the icons folder.
    icons_path = os.path.dirname(os.path.realpath(__file__)) + '/icons/'
    image_path1 = icons_path + 'RiggingTools.png'
    cmds.image(w = 300, h = 100, image = image_path1)
    cmds.separator(h = 15)
    cmds.button( label='Create FK Controls on Joints', command=rig_utils.create_fk_ctls, w = 300)
    cmds.separator(h = 10)
    cmds.button( label='Combine Nurbs', command=rig_utils.combine_nurbs, w = 300)
    cmds.separator(h = 30)
    cmds.button( label='Colour Yellow', command=rig_utils.colour_yellow, w = 300, bgc = (0.5, 0.5, 0))
    cmds.separator(h = 10)
    cmds.button( label='Colour Red', command=rig_utils.colour_red, w = 300, bgc = (0.5, 0, 0))
    cmds.separator(h = 10)
    cmds.button( label='Colour Blue', command=rig_utils.colour_blue, w = 300, bgc = (0, 0, 0.5))
    cmds.separator(h = 30)
    cmds.button( label='Freeze Transformations', command=rig_utils.freeze, w = 300)
    cmds.separator(h = 10)
    cmds.button( label='Delete History', command=rig_utils.deleteHist, w = 300)
    cmds.separator(h = 30)
    cmds.button( label='Display Local Rotation Axes', command=rig_utils.display_local_axis, w = 300)
    cmds.separator(h = 10)
    cmds.button( label='Hide Local Rotation Axes', command=rig_utils.hide_local_axis, w = 300)
    cmds.separator(h = 15)
    cmds.floatSliderGrp('size_slider', label='Joint Display Size', field=True, v = 1.0, minValue=0.1, maxValue=10.0, cw3 = (100, 40, 150))
    cmds.floatSliderGrp('size_slider', e = True, dc = update_size)
    cmds.setParent('..')




    tab_child2 = cmds.columnLayout(rs = 10)
    image_path2 = icons_path + 'directConnection.png'
    cmds.image(w = 300, h = 100, image = image_path2)

    cmds.button(label='All Translation', command=rig_utils.connect_translation, w = 300)
    cmds.button(label='All Rotation', command=rig_utils.connect_rotation, w = 300)
    cmds.button(label='All Scale', command=rig_utils.connect_scale, w = 300)
    cmds.button(label='Visibility', command=rig_utils.connect_visibility, w = 300)

    cmds.separator(h = 5, style = 'singleDash')
    cmds.text(label = 'Connect single attribute', font = 'boldLabelFont')
    #create menu for individual direct connections
    cmds.optionMenu('direct_connection_menu', w=300, label='Connection Attribute: ')

    #create the indiv connections button and link it to the connect function
    cmds.button(label='Connect Individual', command = connect_attrs, w = 300, h = 30)

    cmds.separator(h = 5, style = 'singleDash')
    cmds.text(label = 'Connect different attributes', font = 'boldLabelFont')
    #create menus for connecting different attributes
    cmds.optionMenu('parent_attr_menu', w=300, label='Parent Attribute:')

    cmds.optionMenu('child_attr_menu', w=300, label='Child Attribute:  ')
    populate_connection_menu()

    #create the different connections button
    cmds.button(label='Connect Different', command = connect_diff, w = 300, h = 30)
    cmds.separator(h = 5)

    cmds.setParent('..')



    tab_child3 = cmds.columnLayout(rs = 10)
    image_path3 = icons_path + 'mySKEL.png'
    cmds.image(w = 300, h = 100, image = image_path3)

    #create mySKEL autorigger buttons
    cmds.button(label='Create Biped Skeleton', command = create_base_skel.create_skel, w = 300)
    cmds.button(label='Mirror Skeleton', command = create_base_skel.mirror_skel, w = 300)
    cmds.text(label = 'Use translation only on lowerBody_jnt\nPlace the other joints using rotate and scale\nto keep the good joint orientations', align = 'left', font = 'smallObliqueLabelFont')
    cmds.button(label='Setup Both Legs', command = setup_both_legs, w = 300)


    cmds.rowColumnLayout(nr = 1, p = tab_child3)
    #get the side prefix with a text input field.
    cmds.text(label = 'Input extra leg prefix here: ', font = 'boldLabelFont')
    side_input = cmds.textField('side_input')


    cmds.columnLayout(p = tab_child3)
    cmds.button(label='Setup extra Leg', command = lambda *args: setup_leg( cmds.textField( side_input, q = True, tx = True ) ), w = 300)
    cmds.text(label = 'input the prefix you gave the extra leg,\nex. right leg prefix would be R, left leg would be L\n(R_leg_jnt, L_leg_jnt, X_leg_jnt)', align = 'left', font = 'smallObliqueLabelFont')



    cmds.tabLayout(tabs, edit=True, tabLabel=((tab_child1, 'Rigging Tools'), (tab_child2, 'Direct Connections'), (tab_child3, 'mySKEL')))
    cmds.setParent('..')
    cmds.showWindow(window)


def populate_connection_menu(*args):
    attrib_list = [
        'translateX',
        'translateY',
        'translateZ',
        'rotateX',
        'rotateY',
        'rotateZ',
        'scaleX',
        'scaleY',
        'scaleZ',
        'visibility'
    ]
    for attr in attrib_list:
        cmds.menuItem(label = attr, parent = 'direct_connection_menu')
        cmds.menuItem(label = attr, parent = 'parent_attr_menu')
        cmds.menuItem(label = attr, parent = 'child_attr_menu')

def connect_attrs(*args):
    connection_attr = cmds.optionMenu('direct_connection_menu', q = True, v = True)
    rig_utils.connect_individual(connection_attr)


def connect_diff(*args):
    parent_attr = cmds.optionMenu('parent_attr_menu', q = True, v = True)
    child_attr = cmds.optionMenu('child_attr_menu', q = True, v = True)
    print parent_attr
    print child_attr
    rig_utils.connect_different(parent_attr, child_attr)


def setup_leg(side):
    fkik_switch.create_fkik_switch(side)
    ik_leg.setup_ik_leg(side)
    reverse_foot.create_rfs(side)
    lock_ctls.lock_ctls(side)


def setup_both_legs(*args):
    setup_leg('L')
    setup_leg('R')

def update_size(*args):
    val = cmds.floatSliderGrp('size_slider', q = True, v = True)
    cmds.jointDisplayScale(val, a = True)