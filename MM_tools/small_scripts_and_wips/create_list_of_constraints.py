import maya.cmds as cmds

# Build list of constraints
parent_cnst_list = cmds.ls(type='parentConstraint')
point_cnst_list = cmds.ls(type='pointConstraint')
orient_cnst_list = cmds.ls(type='orientConstraint')

#cmds.delete(parent_cnst_list, point_cnst_list, orient_cnst_list)

for cnst in parent_cnst_list:
    trans = []
    rot = []
    for attr in 'XYZ':
        # check for translate and rotate connections
        t = cmds.listConnections(cnst + '.constraintTranslate' + attr)
        r = cmds.listConnections(cnst + '.constraintRotate' + attr)
    
        # add attribute to list if it is missing an attribute connection
        if not t:
            trans.append(attr.lower())
        if not r:
            rot.append(attr.lower())
        
        # get the driver and driven objects
        driver = cmds.parentConstraint(cnst, q=True, targetList=True)[0]
        driven = cnst.replace('_parentConstraint1', '')
       
    # print out the python command for parent constraint
    # use the rot/trans list to adress skipped axes
    print('cmds.parentConstraint("{}", "{}", skipRotate={}, skipTranslate={}, mo=True)'.format(
        driver, driven, rot, trans))
            
for cnst in orient_cnst_list:
    rot = []
    for attr in 'XYZ':
        r = cmds.listConnections(cnst + '.constraintRotate' + attr)

        if not r:
            rot.append(attr.lower())
        
        driver = cmds.orientConstraint(cnst, q=True, targetList=True)[0]
        driven = cnst.replace('_orientConstraint1', '')

    print('cmds.orientConstraint("{}", "{}", skip={}, mo=True)'.format(
        driver, driven, rot))            

for cnst in point_cnst_list:
    trans = []
    for attr in 'XYZ':
        t = cmds.listConnections(cnst + '.constraintTranslate' + attr)

        if not t:
            trans.append(attr.lower())
        
        driver = cmds.pointConstraint(cnst, q=True, targetList=True)[0]
        driven = cnst.replace('_pointConstraint1', '')

    print('cmds.pointConstraint("{}", "{}", skip={}, mo=True)'.format(
        driver, driven, trans))            
            