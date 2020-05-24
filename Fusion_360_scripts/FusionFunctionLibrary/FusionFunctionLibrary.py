import adsk.core, adsk.fusion, traceback
from os.path import join

def print(to_print):
    adsk.core.Application.get().userInterface.messageBox(to_print)

def setup_fusion_workspace():
    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent # the top level component in the autodesk component tree
    ui = app.userInterface
    return app, design, rootComp, ui

def create_component(root_component, location = None, transform_matrix = None,  name = None):

    if location is not None and transform_matrix is None:
        transform_matrix = adsk.core.Matrix3D.create()
        transform_matrix.translation = adsk.core.Vector3D.create(   transform_matrix.translation.x + location.x,
                                                                    transform_matrix.translation.y + location.y,
                                                                    transform_matrix.translation.z + location.z)

    if transform_matrix is None:
        transform_matrix = adsk.core.Matrix3D.create()

    new_occurrence = root_component.occurrences.addNewComponent(transform_matrix)
    new_component = new_occurrence.component

    if name is not None and isinstance(name, str):
        new_component.name = name

    return new_component, new_occurrence

def points_from_coordinates(x, y, z=None):
    points = adsk.core.ObjectCollection.create()
    if len(x) != len(y):
        raise ValueError("x and y coordiantes should be the same length")
    if z is None:
        z = [0 for _ in x]
    for i,_ in enumerate(x):
            points.add(adsk.core.Point3D.create(x[i], y[i], z[i]))
    return points

def Extrude(component, profile, type, height):
    '''
    Creates an extrude from a profile.

    Allowable types:
    adsk.fusion.FeatureOperations
     eg/ JoinFeatureOperation
        NewComponentFeatureOperation, etc.
    '''
    extrudes = component.features.extrudeFeatures
    extInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.JoinFeatureOperation) # create an extrusion using the new feature operation.
    extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
    ext = extrudes.add(extInput)
    return ext

def booleanSubtract(targetComp, toolComp):
    '''
    Subtract one component from another.
    The targetComp should only contain one body.
    '''
    if targetComp.bRepBodies.count > 1:
        raise NotImplementedError
    combines = targetComp.features.combineFeatures
    toolBodies = adsk.core.ObjectCollection.create()
    for i in range(toolComp.bRepBodies.count):
        toolBodies.add(toolComp.bRepBodies.item(i))
    combInput = combines.createInput(targetComp.bRepBodies.item(0), toolBodies)
    combInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    comb = combines.add(combInput)
    return comb

def convert_to_valid_filename(filename):
    filename = ":".join(filename.split(":")[:-1])
    to_replace = {"@":"",
                "(": "",
                 ")":"",
                 "_": "_",
                 " ": "_",
                 ":":"_"}
    new_name = filename
    for key in to_replace.keys():
        new_name = new_name.replace(key, to_replace[key])
    return new_name

def export_to_stl(component, folder, meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementLow):
    app, design, rootComp, ui = setup_fusion_workspace()
    exportMgr = adsk.fusion.ExportManager.cast(design.exportManager)
    stlOptions = exportMgr.createSTLExportOptions(component)
    stlOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
    filename = join(folder, convert_to_valid_filename(str(component.name)) + ".stl")
    stlOptions.filename = filename
    exportMgr.execute(stlOptions)

def rotateOccurence(occ, angle, axis = 2, about = None):
    transform = occ.transform
    trl = transform.translation
    ax = [0,0,0]
    ax[axis] = 1
    ax = adsk.core.Vector3D.create(ax[0], ax[1], ax[2])
    if about is None:
        pt = adsk.core.Point3D.create(trl.x, trl.y, trl.z)
    else:
        pt = adsk.core.Point3D.create(about[0], about[1], about[2])
    transform.setToRotation(angle, ax, pt)
    transform.translation = trl
    occ.transform = transform

    #rotation_collection = adsk.core.ObjectCollection.create()
    #rotation_collection.add(occ.component)
    moveFeature = occ.component.features.moveFeatures
    moveInput = moveFeature.createInput(occ.component.bRepBodies, occ.transform)
    moveOperation = moveFeature.add(moveInput)

    return occ
