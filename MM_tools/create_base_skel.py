
import maya.cmds as cmds

def create_skel(*args):
    """Creates the required setup to use my auto leg and foot FKIK rigging script.
    You will need to place the joints using rotation and scaling, or reorient the joints yourself"""

    #create Right leg joints (lower body chain)
    cmds.joint(n = 'COG_jnt', p = (0, 10, 0))
    cmds.joint(n = 'lowerBody_jnt', p = (0, 9.9, 0))
    cmds.joint(n = 'R_hip_jnt', p = (-1.1, 9.3, -0.1))
    cmds.joint(n = 'R_knee_jnt', p = (-1.3, 4.8, 0.2))
    cmds.joint(n = 'R_ankle_jnt', p = (-1.3, 0.6, -0.2))
    cmds.joint(n = 'R_ball_jnt', p = (-1.3, 0.1, 0.8))
    cmds.joint(n ='R_toe_jnt', p = (-1.3, 0, 1.7))

    cmds.select('R_ankle_jnt')
    cmds.joint(n = 'R_heel_jnt', p = (-1.3, 0, -0.8))


    #orient joints lower body joints
    cmds.joint('R_hip_jnt', e = True, oj = 'xyz', sao = 'zup')
    cmds.joint('R_knee_jnt', e = True, oj = 'xyz', sao = 'zup')
    cmds.joint('R_ankle_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_ball_jnt', e = True, oj = 'xyz', sao = 'yup')


    #create upper body chain (spine to head)
    cmds.select('COG_jnt')
    cmds.joint(n = 'upperBody_jnt', p = (0, 10.1, 0))
    cmds.joint(n = 'spine_jnt', p = (0, 12, 0))
    cmds.joint(n = 'chest_jnt', p = (0, 13.5, -0.1))
    cmds.joint(n = 'neck_jnt', p = (0, 14.7, 0))
    cmds.joint(n = 'head_jnt', p = (0, 16.2, 0.3))
    cmds.joint(n = 'headTip_jnt', p = (0, 17.7, 0.3))

    cmds.select('head_jnt')
    cmds.joint(n = 'R_eye_jnt', p = (-0.5, 16.4, 1.4))
    cmds.joint(n = 'R_eyeTip_jnt', p = (-0.5, 16.4, 1.7))

    cmds.select('head_jnt')
    cmds.joint(n = 'jaw_jnt', p = (0, 15.9, 0.7))
    cmds.joint(n = 'jawTip_jnt', p = (0, 15.4, 1.7))

    #orient upper body chain
    cmds.joint('spine_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('chest_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('neck_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('head_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('jaw_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_eye_jnt', e = True, oj = 'xyz', sao = 'yup')


    #create right arm joints
    cmds.select('chest_jnt')
    cmds.joint(n = 'R_scapula_jnt', p = (-0.4, 14.2, 0.3))
    cmds.joint(n = 'R_shoulder_jnt', p = (-1.5, 14.2, 0.3))
    cmds.joint(n = 'R_elbow_jnt', p = (-4.1, 14.2, 0.1))
    cmds.joint(n = 'R_wristTwist_jnt', p = (-5.4, 14.2, 0.2))
    cmds.joint(n = 'R_wrist_jnt', p = (-6.4, 14.2, 0.3))

    cmds.select('R_wrist_jnt')
    cmds.joint(n = 'R_middleFinger1_jnt', p = (-7.4, 14.2, 0.25))
    cmds.joint(n = 'R_middleFinger2_jnt', p = (-7.7, 14.2, 0.25))
    cmds.joint(n = 'R_middleFinger3_jnt', p = (-7.9, 14.2, 0.25))
    cmds.joint(n = 'R_middleFinger4_jnt', p = (-8.1, 14.2, 0.25))

    #orient right arm joints
    cmds.joint('R_scapula_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('R_shoulder_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('R_elbow_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('R_wristTwist_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('R_wrist_jnt', e = True, oj = 'xyz', sao = 'yup')


    # create right hand joints
    cmds.select('R_wrist_jnt')
    cmds.joint(n = 'R_thumbFinger1_jnt', p = (-6.6, 14.1, 0.4))
    cmds.joint(n = 'R_thumbFinger2_jnt', p = (-6.8, 14, 0.6))
    cmds.joint(n = 'R_thumbFinger3_jnt', p = (-7, 13.9, 0.7))
    cmds.joint(n = 'R_thumbFinger4_jnt', p = (-7.2, 13.8, 0.8))

    cmds.select('R_wrist_jnt')
    cmds.joint(n = 'R_indexFinger1_jnt', p = (-7.3, 14.2, 0.5))
    cmds.joint(n = 'R_indexFinger2_jnt', p = (-7.5, 14.2, 0.55))
    cmds.joint(n = 'R_indexFinger3_jnt', p = (-7.7, 14.2, 0.6))
    cmds.joint(n = 'R_indexFinger4_jnt', p = (-7.9, 14.2, 0.65))

    cmds.select('R_wrist_jnt')
    cmds.joint(n = 'R_handCup_jnt', p = (-6.6, 14.2, 0.15))
    cmds.joint(n = 'R_pinkyFinger1_jnt', p = (-7.2, 14.2, -0.15))
    cmds.joint(n = 'R_pinkyFinger2_jnt', p = (-7.4, 14.2, -0.2))
    cmds.joint(n = 'R_pinkyFinger3_jnt', p = (-7.6, 14.2, -0.25))
    cmds.joint(n = 'R_pinkyFinger4_jnt', p = (-7.8, 14.2, -0.3))

    cmds.select('R_handCup_jnt')
    cmds.joint(n = 'R_ringFinger1_jnt', p = (-7.3, 14.2, 0))
    cmds.joint(n = 'R_ringFinger2_jnt', p = (-7.6, 14.2, 0))
    cmds.joint(n = 'R_ringFinger3_jnt', p = (-7.8, 14.2, 0))
    cmds.joint(n = 'R_ringFinger4_jnt', p = (-8, 14.2, 0))

    #orient fingers
    cmds.joint('R_thumbFinger1_jnt', e = True, oj = 'xyz', sao = 'zup')
    cmds.joint('R_thumbFinger2_jnt', e = True, oj = 'xyz', sao = 'zup')
    cmds.joint('R_thumbFinger3_jnt', e = True, oj = 'xyz', sao = 'zup')

    cmds.joint('R_middleFinger1_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_middleFinger2_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_middleFinger3_jnt', e = True, oj = 'xyz', sao = 'yup')

    cmds.joint('R_ringFinger1_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_ringFinger2_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_ringFinger3_jnt', e = True, oj = 'xyz', sao = 'yup')

    cmds.joint('R_handCup_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_pinkyFinger1_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_pinkyFinger2_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_pinkyFinger3_jnt', e = True, oj = 'xyz', sao = 'yup')

    cmds.joint('R_indexFinger1_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_indexFinger2_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint('R_indexFinger3_jnt', e = True, oj = 'xyz', sao = 'yup')

    orient_skel('R')

    cmds.circle(n = 'scale_ctl', ch = False, r = 4, nr = (0, 1, 0))
    cmds.parent('COG_jnt', 'scale_ctl')

    cmds.select(d = True)

def mirror_skel(*args):

    #mirror right scapula
    cmds.mirrorJoint('R_scapula_jnt', mirrorYZ = True, sr = ('R', 'L'), mb = True)

    #mirror right eye joints
    cmds.mirrorJoint('R_eye_jnt', mirrorYZ = True, sr = ('R', 'L'), mb = True)

    #mirror right leg joints
    cmds.mirrorJoint('R_hip_jnt', mirrorYZ = True, sr = ('R', 'L'), mb = True)

    cmds.select(d=True)




def orient_skel(side, *args):

    #orient joints lower body joints
    cmds.joint(side + '_hip_jnt', e = True, oj = 'xyz', sao = 'zup')
    cmds.joint(side + '_knee_jnt', e = True, oj = 'xyz', sao = 'zup')
    cmds.joint(side + '_ankle_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_ball_jnt', e = True, oj = 'xyz', sao = 'yup')

    #orient upper body chain
    cmds.joint('spine_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('chest_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('neck_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('head_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint('jaw_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_eye_jnt', e = True, oj = 'xyz', sao = 'yup')

    #orient right arm joints
    cmds.joint(side + '_scapula_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint(side + '_shoulder_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint(side + '_elbow_jnt', e = True, oj = 'xyz', sao = 'zdown')
    cmds.joint(side + '_wristTwist_jnt', e = True, oj = 'xyz', sao = 'zdown')

    #orient fingers
    cmds.joint(side + '_thumbFinger1_jnt', e = True, oj = 'xyz', sao = 'zup')
    cmds.joint(side + '_thumbFinger2_jnt', e = True, oj = 'xyz', sao = 'zup')
    cmds.joint(side + '_thumbFinger3_jnt', e = True, oj = 'xyz', sao = 'zup')

    cmds.joint(side + '_middleFinger1_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_middleFinger2_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_middleFinger3_jnt', e = True, oj = 'xyz', sao = 'yup')

    cmds.joint(side + '_ringFinger1_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_ringFinger2_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_ringFinger3_jnt', e = True, oj = 'xyz', sao = 'yup')

    cmds.joint(side + '_handCup_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_pinkyFinger1_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_pinkyFinger2_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_pinkyFinger3_jnt', e = True, oj = 'xyz', sao = 'yup')

    cmds.joint(side + '_indexFinger1_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_indexFinger2_jnt', e = True, oj = 'xyz', sao = 'yup')
    cmds.joint(side + '_indexFinger3_jnt', e = True, oj = 'xyz', sao = 'yup')

    #unparent finger joints from wrist except middle finger, orient, reparent.
    #otherwise maya has to choose the finger to align with from the wrist's children
    #its not smart enough to do that and it gives an error

    cmds.parent(side + '_indexFinger1_jnt', w = True)
    cmds.parent(side + '_handCup_jnt', w = True)
    cmds.parent(side + '_thumbFinger1_jnt', w = True)

    cmds.joint(side + '_wrist_jnt', e = True, oj = 'xyz', sao = 'yup')

    cmds.parent(side + '_indexFinger1_jnt', side + '_wrist_jnt')
    cmds.parent(side + '_handCup_jnt', side + '_wrist_jnt')
    cmds.parent(side + '_thumbFinger1_jnt', side + '_wrist_jnt')

    cmds.select(d=True)












