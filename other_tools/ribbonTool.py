import pymel.core as pm


def create_follicle(nurbs_surface, *args):
    """initial code from http://chrislesage.com/character-rigging/manually-create-maya-follicle-in-python/"""
    # manually place and connect a follicle onto a nurbs surface.
    nurbs_ribbon = pm.PyNode(nurbs_surface)
    if nurbs_ribbon.type() == 'transform':
        nurbs_ribbon = nurbs_ribbon.getShape()
    elif nurbs_ribbon.type() == 'nurbsSurface':
        pass
    else:
        'Warning: Input must be a nurbs surface.'
        return False

    # create a name with frame padding
    foll_name = '_'.join((nurbs_ribbon.name(), 'follicle', '#'.zfill(2)))

    created_foll = pm.createNode('follicle', name=foll_name)
    nurbs_ribbon.local.connect(created_foll.inputSurface)

    return created_foll


def split_name(name, char, *args):
    if char in name:
        new_name = name.split(char)
        return new_name[0]
    else:
        return name


def place_follicle(foll, u_pos=0.0, v_pos=0.0, *args):
    """initial code from http://chrislesage.com/character-rigging/manually-create-maya-follicle-in-python/"""
    r_name = pm.textField('ribbon_name', q=True, tx=True).replace(" ", "_")
    r_name = pm.PyNode(r_name)
    r_name.worldMatrix[0].connect(foll.inputWorldMatrix)
    foll.outRotate.connect(foll.getParent().rotate)
    foll.outTranslate.connect(foll.getParent().translate)
    foll.parameterU.set(u_pos)
    foll.parameterV.set(v_pos)
    foll.getParent().t.lock()
    foll.getParent().r.lock()
    foll.setAttr('simulationMethod', 0)
    return foll
 
def create_foll_and_joints(*args):

    r_name = pm.textField('ribbon_name', q=True, tx=True).replace(" ", "_")
    skin_joints = []
    created_nodes = [r_name]

    rib_u = pm.intField('u_div', q=True, v=True)
    foll_amount = rib_u + 1

    jnt_frequency = pm.intField('jnt_freq', q=True, v=True)

    for i in range(0, foll_amount):
        new_foll = create_follicle(r_name)
        new_foll = place_follicle(new_foll, i/(foll_amount-1.0), 0.5)
        new_joint = pm.joint(n=split_name(new_foll, '|') + '_jnt')
        jnt_radius = new_joint.getAttr('radius')

        if (i % jnt_frequency) == 0:
            ctl_joint = pm.joint(new_joint, n=new_joint.replace('_follicle', ''))
            ctl_joint.setAttr('radius', jnt_radius+1)
            pm.parent(ctl_joint, w=True)
            skin_joints.append(ctl_joint)

        created_nodes.append(ctl_joint)
        created_nodes.append(new_foll)

    return skin_joints, created_nodes


def skin_ribbon_joints(skin_joints, *args):
    r_name = pm.textField('ribbon_name', q=True, tx=True).replace(" ", "_")
    pm.select(d=True)
    pm.select(skin_joints, r_name)
    pm.skinCluster()


def group_ribbon(created_nodes, *args):
    r_name = pm.textField('ribbon_name', q=True, tx=True).replace(" ", "_")
    pm.group(created_nodes, n=r_name+'_grp')


def ui(*args):
    if pm.window('Ribbon Tool', exists=True):
        pm.deleteUI('Ribbon Tool')

    window = pm.window('Ribbon Tool',  title='Ribbon Tool',
                         mxb=False, mnb=False)

    pm.columnLayout('mainColumn')
    pm.rowColumnLayout('ColumnLayout1', numberOfColumns=2, cs=(1, 3), rs=(1, 5),
                         columnWidth=[(1, 150), (2, 100)])

    pm.text(label='Ribbon Name:', al='left')
    pm.textField('ribbon_name', ed=True)

    pm.text(label='U divisions:', al='left')
    pm.intField('u_div', ed=True, v=10)

    pm.text(label='V divisions:', al='left')
    pm.intField('v_div', ed=True, v=1)

    pm.text(label='Ribbon Length', al='left')
    pm.floatField('r_length', ed=True, v=0.2)

    pm.text(label='Ribbon Width', al='left')
    pm.floatField('r_width', ed=True, v=5.0)

    pm.text(label='Control Joint Frequency', al='left')
    pm.intField('jnt_freq', ed=True, v=3)

    pm.button(label='Create Ribbon',
                command=create_ribbon,  w=300)

    pm.setParent('..')
    pm.showWindow(window)


def create_ribbon(*args):
    r_name = pm.textField('ribbon_name', q=True, tx=True).replace(" ", "_")
    print r_name
    if r_name == '':
        print 'give your ribbon a unique name'
        pass

    
    else:
        rib_u = pm.intField('u_div', q=True, v=True)
        rib_v = pm.intField('v_div', q=True, v=True)
        rib_length = pm.floatField('r_length', q=True, v=True)
        rib_width = pm.floatField('r_width', q=True, v=True)
        rib_axis = (0, 0, 1)
        rib_degree = 3

        pm.nurbsPlane(
            n=r_name,
            ax=rib_axis,
            d=rib_degree,
            w=rib_width,
            lr=rib_length,
            u=rib_u,
            v=rib_v)

        skin_joints, created_nodes = create_foll_and_joints()
        print 'Follicles and joints created'
        skin_ribbon_joints(skin_joints)
        print 'Joints skinned'
        group_ribbon(created_nodes)
        print 'Ribbon grouped'
        return


ui()