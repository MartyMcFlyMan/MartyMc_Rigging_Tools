
import maya.cmds as cmds


def combine_nurbs(*args):
    """Select Nurbs to make into a single Nurb. All Nurbs have to be under the same parent or under world"""

    selection = cmds.ls(sl=True)

    for x in selection:
        cmds.makeIdentity(a=True, t=True, r=True, s=True)
        cmds.delete(x, ch=True)

    parent_name = selection[-1]
    selection.pop()  # remove parentNurb from list

    # now we have a list of the nurbs we need to parent under the parentNurb
    for nurb in selection:

        # get Transform name
        transform_name = nurb
        print transform_name

        # get Shape Name
        shape_name = cmds.listRelatives(nurb, ad=True, shapes=True)[0]
        print shape_name

        # parent the shape node to the new parent
        cmds.parent(shape_name, parent_name, s=True, r=True)

        # delete unneeded tranform nodes
        cmds.delete(transform_name)

    return None


def create_fk_ctls(*args):
    """
    Will create and place NURBS circles on all the selected joints.
    Will also parent the new controllers to their respective joint.
    You must select joints before calling the function.
    Select only one joint hierarchy at a time
    """

    # create a list with all selected objects.
    selected = cmds.ls(sl=True)

    jnt_list = []  # make a list for all the processed joints
    ctl_list = []  # make a list for all the created controls

    for jnt in selected:

        # verify if the jnt were given the _jnt suffix, and if they have, then remove it and give it a nice name
        nice_name = jnt
        if jnt[-4:] == '_jnt':
            nice_name = jnt[:-4]

        jnt_pos = tuple(cmds.xform(jnt, q=True, t=True, ws=True))
        jnt_rot = tuple(cmds.xform(jnt, q=True, ro=True, ws=True))

        # returns a list. Makes a circle controller named after the joint currently being looped
        ctl_name = cmds.circle(ch=False, n=nice_name + '_ctl')[0]
        cmds.xform(ctl_name, ro=(0, 90, 0))  # turns the control so that it is perpendicular to the joint
        cmds.makeIdentity(ctl_name, a=True, t=True, r=True, s=True)

        # newGrp returns group name as string. Creates the offset group
        grp_name = cmds.group(n=nice_name + '_offset')
        cmds.xform(grp_name, ro=jnt_rot, t=jnt_pos, a=True)
        cmds.parentConstraint(ctl_name, jnt)

        if jnt_list:  # check if it is the first joint being processed
            # check if the current joint's parent node is the same as the last joint processed
            # ''.join() because comparing a list to string. casts list to string before comparison
            if ''.join(cmds.listRelatives(jnt, p=True)) == jnt_list[-1]:
                cmds.parent(grp_name, ctl_list[-1])

        jnt_list.append(jnt)  # add the last processed joint
        ctl_list.append(ctl_name)  # add the last created control

    return None


def connect_translation(*args):
    sel = cmds.ls(sl=True)
    parent = sel[0]
    for x in sel[1:]:
        cmds.connectAttr(parent+'.tx', x+'.tx', f=True)
        cmds.connectAttr(parent+'.ty', x+'.ty', f=True)
        cmds.connectAttr(parent+'.tz', x+'.tz', f=True)
    return None


def connect_rotation(*args):
    sel = cmds.ls(sl=True)
    parent = sel[0]
    for x in sel[1:]:
        cmds.connectAttr(parent+'.rx', x+'.rx', f=True)
        cmds.connectAttr(parent+'.ry', x+'.ry', f=True)
        cmds.connectAttr(parent+'.rz', x+'.rz', f=True)
    return None


def connect_scale(*args):
    sel = cmds.ls(sl=True)
    parent = sel[0]
    for x in sel[1:]:
        cmds.connectAttr(parent+'.sx', x+'.sx', f=True)
        cmds.connectAttr(parent+'.sy', x+'.sy', f=True)
        cmds.connectAttr(parent+'.sz', x+'.sz', f=True)
    return None


def connect_visibility(*args):
    sel = cmds.ls(sl=True)
    parent = sel[0]
    for x in sel[1:]:
        cmds.connectAttr(parent+'.v', x + '.v', f=True)
    return None


# connect single attribute given as argument
def connect_individual(attr, *args):
    sel = cmds.ls(sl=True)
    parent = sel[0]
    for x in sel[1:]:
        cmds.connectAttr(parent + '.' + attr, x + '.' + attr, f=True)
    return None


# connect all attributes given as arguments
def direct_connection(*args):
    sel = cmds.ls(sl=True)
    parent = sel[0]
    # parse children objects
    for x in sel[1:]:
        # parse attributes to be connected
        for attr in args:
            cmds.connectAttr(parent + '.' + attr, x + '.' + attr, f=True)


# connect different attributes on parent and children
def connect_different(parent_attr, child_attr, *args):
    sel = cmds.ls(sl=True)
    parent = sel[0]
    # parse children objects
    for x in sel[1:]:
        cmds.connectAttr(parent + '.' + parent_attr, x + '.' + child_attr, f=True)


def colour_stuff(object, R, G, B, *args):
    if not object:
        object = cmds.ls(sl=True)[0]

    cmds.setAttr(object + '.overrideEnabled', 1)
    cmds.setAttr(object + '.overrideRGBColors', 1)
    cmds.setAttr(object + '.overrideColorRGB', R, G, B)
    return None


def colour_yellow(*args):

    object = cmds.ls(sl=True)

    for obj in object:
        cmds.setAttr(obj + '.overrideEnabled', 1)
        cmds.setAttr(obj + '.overrideRGBColors', 1)
        cmds.setAttr(obj + '.overrideColorRGB', 1, 1, 0)

    if type(object) is str:
        cmds.setAttr(object + '.overrideEnabled', 1)
        cmds.setAttr(object + '.overrideRGBColors', 1)
        cmds.setAttr(object + '.overrideColorRGB', 1, 1, 0)

    return None


def colour_red(*args):

    object = cmds.ls(sl=True)

    for obj in object:
        cmds.setAttr(obj + '.overrideEnabled', 1)
        cmds.setAttr(obj + '.overrideRGBColors', 1)
        cmds.setAttr(obj + '.overrideColorRGB', 1, 0, 0)

    if type(object) is str:
        cmds.setAttr(object + '.overrideEnabled', 1)
        cmds.setAttr(object + '.overrideRGBColors', 1)
        cmds.setAttr(object + '.overrideColorRGB', 1, 0, 0)

    return None


def colour_blue(*args):

    object = cmds.ls(sl=True)

    for obj in object:
        cmds.setAttr(obj + '.overrideEnabled', 1)
        cmds.setAttr(obj + '.overrideRGBColors', 1)
        cmds.setAttr(obj + '.overrideColorRGB', 0, 0, 1)

    if type(object) is str:
        cmds.setAttr(object + '.overrideEnabled', 1)
        cmds.setAttr(object + '.overrideRGBColors', 1)
        cmds.setAttr(object + '.overrideColorRGB', 0, 0, 1)

    return None


def hide(obj, *args):
    cmds.setAttr(obj + '.v', 0)
    return None


def lock_attr(obj, *attrs):
    for attr in attrs:
        cmds.setAttr(obj + '.' + attr, lock=True)
    return None


def freeze(*args):
    sel = cmds.ls(sl=True)
    cmds.makeIdentity(sel, a=True, t=True, r=True, s=True)


def deleteHist(*args):
    sel = cmds.ls(sl=True)
    cmds.delete(sel, ch=True)


def display_local_axis(*args):
    sel = cmds.ls(sl=True)
    # if selection is empty, show all joints local axis
    if not sel:
        jnt_list = cmds.ls(type='joint')
        for jnt in jnt_list:
            cmds.setAttr(jnt + '.displayLocalAxis', True)
    else:
        for jnt in sel:
            cmds.setAttr(jnt + '.displayLocalAxis', True)


def hide_local_axis(*args):
    jnt_list = cmds.ls(type='joint')
    for jnt in jnt_list:
        cmds.setAttr(jnt + '.displayLocalAxis', False)
