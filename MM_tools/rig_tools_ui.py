
from maya import cmds
import os
import rig_utils
import create_base_skel
from class_simple_rig import SimpleRig
from class_fkik_limb import FkikArm, FkikLeg, ReverseFoot

reload(rig_utils)
reload(create_base_skel)


def ui():

    # check if window exists, if it does, then delete it and create a new one to avoid multiple windows.
    if cmds.window('MM_rigging_tools', exists=True):
        cmds.deleteUI('MM_rigging_tools')

    # Create a window
    window = cmds.window('MM_rigging_tools',  title="MM Rigging Tools", w=300, h=250, mxb=False, mnb=False)

    # setup tabs
    tabs = cmds.tabLayout()

    tab_child1 = cmds.columnLayout()

    # create banner image
    # find the relative path to the icons folder.
    icons_path = os.path.dirname(os.path.realpath(__file__)) + '/icons/'
    image_path1 = icons_path + 'RiggingTools.png'
    cmds.image(w=300, h=100, image=image_path1)
    cmds.separator(h=15)
    cmds.button(label='Create FK Controls on Joints', command=rig_utils.create_fk_ctls, w=300)
    cmds.separator(h=10)
    cmds.button(label='Combine Nurbs', command=rig_utils.combine_nurbs, w=300)
    cmds.separator(h=30)
    cmds.button(label='Colour Yellow', command=rig_utils.colour_yellow, w=300, bgc=(0.5, 0.5, 0))
    cmds.separator(h=10)
    cmds.button(label='Colour Red', command=rig_utils.colour_red, w=300, bgc=(0.5, 0, 0))
    cmds.separator(h=10)
    cmds.button(label='Colour Blue', command=rig_utils.colour_blue, w=300, bgc=(0, 0, 0.5))
    cmds.separator(h=30)
    cmds.button(label='Freeze Transformations', command=rig_utils.freeze, w=300)
    cmds.separator(h=10)
    cmds.button(label='Delete History', command=rig_utils.deleteHist, w=300)
    cmds.separator(h=30)
    cmds.button(label='Display Local Rotation Axes', command=rig_utils.display_local_axis, w=300)
    cmds.separator(h=10)
    cmds.button(label='Hide Local Rotation Axes', command=rig_utils.hide_local_axis, w=300)
    cmds.separator(h=15)
    cmds.floatSliderGrp('size_slider', label='Joint Display Size', field=True, v=1.0,
                        minValue=0.1, maxValue=10.0, cw3=(100, 40, 150))
    cmds.floatSliderGrp('size_slider', e=True, dc=update_size)
    cmds.setParent('..')

    tab_child2 = cmds.columnLayout(rs=10)
    image_path2 = icons_path + 'directConnection.png'
    cmds.image(w=300, h=100, image=image_path2)

    cmds.button(label='All Translation', command=rig_utils.connect_translation, w=300)
    cmds.button(label='All Rotation', command=rig_utils.connect_rotation, w=300)
    cmds.button(label='All Scale', command=rig_utils.connect_scale, w=300)
    cmds.button(label='Visibility', command=rig_utils.connect_visibility, w=300)

    cmds.separator(h=5, style='singleDash')
    cmds.text(label='Connect single attribute', font='boldLabelFont')
    # create menu for individual direct connections
    cmds.optionMenu('direct_connection_menu', w=300, label='Connection Attribute: ')

    # create the indiv connections button and link it to the connect function
    cmds.button(label='Connect Individual', command=connect_attrs, w=300, h=30)

    cmds.separator(h=5, style='singleDash')
    cmds.text(label='Connect different attributes', font='boldLabelFont')
    # create menus for connecting different attributes
    cmds.optionMenu('parent_attr_menu', w=300, label='Parent Attribute:')

    cmds.optionMenu('child_attr_menu', w=300, label='Child Attribute:  ')
    populate_connection_menu()

    # create the different connections button
    cmds.button(label='Connect Different', command=connect_diff, w=300, h=30)
    cmds.separator(h=5)

    cmds.setParent('..')

    tab_child3 = cmds.columnLayout(rs=10)
    image_path3 = icons_path + 'mySKEL.png'
    cmds.image(w=300, h=100, image=image_path3)

    # create mySKEL autorigger buttons
    cmds.button(label='Fast FK rig', command=fast_fk_rig, w=300)
    cmds.text(label='Select COG only', font='smallBoldLabelFont')
    cmds.separator(h=20)
    cmds.button(label='Create Biped Skeleton', command=create_base_skel.create_skel, w=300)
    cmds.button(label='Mirror skeleton', command=mirror_skel, w=300)
    cmds.separator(h=15)
    cmds.button(label='Setup Leg', command=rig_leg, w=300)
    cmds.text(label='Select hip joint', font='smallBoldLabelFont')
    cmds.separator(h=5)
    cmds.button(label='Setup Leg and foot', command=rig_leg_foot, w=300)
    cmds.text(label='Select hip joint', font='smallBoldLabelFont')
    cmds.separator(h=5)
    cmds.button(label='Setup Arm', command=rig_arm, w=300)
    cmds.text(label='Select shoulder joint', font='smallBoldLabelFont')
    cmds.separator(h=5)

    cmds.tabLayout(tabs, edit=True, tabLabel=((tab_child1, 'Rigging Tools'),
                                              (tab_child2, 'Direct Connections'),
                                              (tab_child3, 'mySKEL')))
    cmds.setParent('..')
    cmds.showWindow(window)


def fast_fk_rig(*args):
    cog_joint = cmds.ls(sl=True)[0]
    root = SimpleRig(cog_joint)
    root.setup_rig()

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
        cmds.menuItem(label=attr, parent='direct_connection_menu')
        cmds.menuItem(label=attr, parent='parent_attr_menu')
        cmds.menuItem(label=attr, parent='child_attr_menu')


def connect_attrs(*args):
    connection_attr = cmds.optionMenu('direct_connection_menu', q=True, v=True)
    rig_utils.connect_individual(connection_attr)


def connect_diff(*args):
    parent_attr = cmds.optionMenu('parent_attr_menu', q=True, v=True)
    child_attr = cmds.optionMenu('child_attr_menu', q=True, v=True)
    print parent_attr
    print child_attr
    rig_utils.connect_different(parent_attr, child_attr)


# joint display size update
def update_size(*args):
    val = cmds.floatSliderGrp('size_slider', q=True, v=True)
    cmds.jointDisplayScale(val, a=True)


def detect_parts(*args):

    parts_dict = {}
    ankles_list = []
    scaps_list = []
    hips_list = []

    joints_list = cmds.ls(type='joint')

    # detect scapulas and hips for mirroring
    for long_name in joints_list:
        name_list = long_name.split('|')
        short_name = name_list[-1]

        if 'scapula' in short_name:
            scaps_list.append(long_name)

        if 'hip' in short_name:
            hips_list.append(long_name)

        if 'ankle' in short_name:
            ankles_list.append(long_name)

    parts_dict['ankles_list'] = ankles_list
    parts_dict['scaps_list'] = scaps_list
    parts_dict['hips_list'] = hips_list

    return parts_dict


def mirror_skel(*args):
    hips_list = detect_parts().get('hips_list')
    scap_list = detect_parts().get('scaps_list')

    if hips_list:
        for hip in hips_list:
            # mirror right leg joints
            cmds.mirrorJoint(hip, mirrorYZ=True, sr=('R', 'L'), mb=True)

    if scap_list:
        for scap in scap_list:
            # mirror right scapula
            cmds.mirrorJoint(scap, mirrorYZ=True, sr=('R', 'L'), mb=True)

    # mirror right eye joints
    cmds.mirrorJoint('R_eye_jnt', mirrorYZ=True, sr=('R', 'L'), mb=True)

    cmds.select(d=True)


def rig_leg_foot(*args):
    """Pass selection to rig setup function of class ReverseFoot"""
    sel = cmds.ls(sl=True)
    for x in sel:
        x = ReverseFoot(x)
        x.setup_foot()


def rig_leg(*args):
    """Pass selection to rig setup function of class FkikLeg"""
    sel = cmds.ls(sl=True)
    for x in sel:
        x = FkikLeg(x)
        x.setup_leg()


def rig_arm(*args):
    """Pass selection to rig setup function of class FkikArm"""
    sel = cmds.ls(sl=True)
    for x in sel:
        x = FkikArm(x)
        x.setup_arm()




