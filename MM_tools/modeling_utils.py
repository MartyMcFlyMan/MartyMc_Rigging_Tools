import maya.cmds as cmds
import random as rand


def select_random_verts(seed, thresh, *args):
    rand.seed(seed)
    sel = cmds.ls(sl=True)
    obj_name = sel[0].split('.')[0]

    # support for whole object
    if cmds.objectType(sel[0]) == 'transform':
        print 'Object mode selected'
        vert_nmb = cmds.polyEvaluate(sel[0], v=True) - 1

        cmds.select(cl=True)

        for x in range(0, vert_nmb):
            if rand.random() <= thresh:
                cmds.select(obj_name + '.vtx[{}]'.format(x), add=True)

    # support for selection of points
    elif cmds.objectType(sel[0]) == 'mesh':
        print 'Vertex mode selected'

        cmds.select(cl=True)

        for item in sel:

            new_string = item.split('[')[1]    # split to get the right part "x : y]"
            range_list = new_string[:-1].split(':')
            print 'range list : ', range_list
            if len(range_list) == 2:
                range_min = int(range_list[0])
                range_max = int(range_list[1])

                for x in range(range_min, range_max):
                    if rand.random() <= thresh:
                        cmds.select(obj_name + '.vtx[{}]'.format(x), add=True)
            else:
                if rand.random() <= thresh:
                    cmds.select(obj_name + '.vtx[{}]'.format(int(range_list[0])), add=True)

    else:
        print 'Selection type not supported'


def ui(*args):
    if cmds.window('Random Vertex Tool', exists=True):
        cmds.deleteUI('Random Vertex Tool')

    window = cmds.window('Random Vertex Tool',  title='Random Vertex Tool',
                         w=300, h=100, mxb=False, mnb=False)

    cmds.columnLayout()

    cmds.floatSliderGrp('Threshold_slider', label='Threshold', field=True, v=0.5,
                        minValue=0.0, maxValue=1.0, cw3=(55, 40, 150))
    #cmds.floatSliderGrp('Threshold_slider', e=True, dc=_update_sliders)

    cmds.floatSliderGrp('Seed_slider', label='Seed', v=0.5, field=True,
                        minValue=1.0, maxValue=100.0, cw3=(55, 40, 150))
    #cmds.floatSliderGrp('Seed_slider', e=True, dc=_update_sliders)

    cmds.button(label='Select',
                command=_select_rand,  w=300)

    cmds.setParent('..')
    cmds.showWindow(window)


def _select_rand(*args):
    thresh_val = cmds.floatSliderGrp('Threshold_slider', q=True, v=True)
    seed_val = cmds.floatSliderGrp('Seed_slider', q=True, v=True)
    select_random_verts(seed_val, thresh_val)


