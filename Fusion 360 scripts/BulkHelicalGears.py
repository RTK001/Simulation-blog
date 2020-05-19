

import adsk.core, adsk.fusion, traceback
from math import pi
from .InvoluteScript.involute import Involute
import os.path

def print(to_print):
    adsk.core.Application.get().userInterface.messageBox(to_print)

def setup_fusion_workspace():
    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent # the top level component in the autodesk component tree
    ui = app.userInterface
    return app, design, rootComp, ui

def create_component(root_component, transform_matrix = None, name = None):
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

def convert_to_valid_filename(filename):
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
    filename = os.path.join(folder, convert_to_valid_filename(str(component.name)) + ".stl")
    stlOptions.filename = filename
    exportMgr.execute(stlOptions)

def rotateOccurence(occ, angle, axis = 2, about = None):
    transform = occ.transform
    trl = transform.translation
    ax = [0,0,0]
    ax[axis] = 1
    ax = adsk.core.Vector3D.create(ax[0], ax[1], ax[2])
    if about is None:
        pt = adsk.core.Point3D.create(trl.x, trl.x, trl.x)
    else:
        pt = adsk.core.Point3D.create(about[0], about[1], about[2])
    transform.setToRotation(angle, ax, pt)
    occ.transform = transform
    return occ

def create_gear(name, involute, gear_height, location = None):

    app, design, rootComp, ui = setup_fusion_workspace()

    I = involute
    tooth_start_angle = 0

    # create new component
    if location is not None:
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(  transform.translation.x + location.x,
                                                            transform.translation.y + location.y,
                                                            transform.translation.z + location.z)
        new_component, new_occurence = create_component(rootComp, transform_matrix = transform, name = name)
    else:
        new_component, new_occurence = create_component(rootComp, name = "Planet1")

    # Sketch points
    gear_profile_sketch = new_component.sketches.add(new_component.xYConstructionPlane)

    # create tooth profile for involute 1
    x1,y1 = I.create_involute1(tooth_start_angle)
    points = points_from_coordinates(x1, y1)
    gear_profile = gear_profile_sketch.sketchCurves.sketchFittedSplines.add(points)


    # create tooth profile for involute 2
    x2,y2 = I.create_involute2(tooth_start_angle)
    points2 = points_from_coordinates(x2, y2)
    gear_profile2 = gear_profile_sketch.sketchCurves.sketchFittedSplines.add(points2)

    # sketch dedendum circle and addendum arc
    circle_centre = adsk.core.Point3D.create(0,0,0)
    dedendum_circle = gear_profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(circle_centre, I._dedendum_radius)
    addendum_circle = gear_profile_sketch.sketchCurves.sketchArcs.addByCenterStartSweep(circle_centre, points[-1], I._addendum_end_angle - I._addendum_start_angle + tooth_start_angle)
    pitch_circle = gear_profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(circle_centre, I._pitch_radius)
    pitch_circle.isConstruction = True

    # constrain points on addendum circle
    gear_profile_sketch.geometricConstraints.addCoincident(addendum_circle.startSketchPoint, gear_profile.endSketchPoint)
    gear_profile_sketch.geometricConstraints.addCoincident(addendum_circle.endSketchPoint, gear_profile2.endSketchPoint)

    # Extrude Gear circle
    extrudes = new_component.features.extrudeFeatures
    extInput = extrudes.createInput(gear_profile_sketch.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation); # create an extrusion using the new feature operation
    extInput.setDistanceExtent(False, adsk.core.ValueInput.createByReal(gear_height))
    ext = extrudes.add(extInput)

    # Extrude gear tooth
    extrudes2 = new_component.features.extrudeFeatures
    extInput2 = extrudes2.createInput(gear_profile_sketch.profiles.item(1), adsk.fusion.FeatureOperations.JoinFeatureOperation); # create an extrusion using the new feature operation
    extInput2.setDistanceExtent(False, adsk.core.ValueInput.createByReal(gear_height))
    ext2 = extrudes2.add(extInput2)

    # create circular tooth pattern
    pattern = new_component.features.circularPatternFeatures

    patternInputFeatures = adsk.core.ObjectCollection.create()
    patternInputFeatures.add(ext2)
    patternInput = pattern.createInput(patternInputFeatures, new_component.zConstructionAxis); # create an extrusion using the new feature operation
    patternInput.quantity = adsk.core.ValueInput.createByReal(I._number_of_teeth)
    patternInput.totalAngle = adsk.core.ValueInput.createByString("360 deg")
    pattern.isSymmetric = False

    patternFeature = pattern.add(patternInput)

    return new_component, new_occurence

def run(context):
    try:

        export_folder = os.path.dirname(os.path.abspath(__file__))
        export_folder = os.path.join(export_folder, "Saved STL files")
        try:
            os.mkdir(export_folder)
        except FileExistsError:
            pass

        # unique things:
        #   pressure angle
        #   module
        #   pitch_diameter
        #   height
        #   Name
        #   Location
        pressure_angle = 20
        gear_pitch_diameter = 20
        gear_module = 0.9
        gear_height = 5
        I = Involute(pressure_angle, gear_pitch_diameter, gear_module)

        angle_to_rotate = 0
        if I._number_of_teeth % 2 == 1:
            angle_to_rotate += pi / I._number_of_teeth

        gear1Comp, gear1Occ = create_gear("Planet1", I, 5, location = adsk.core.Vector3D.create(I.pitch_diameter, 0, 0))
        gear2Comp, gear2Occ = create_gear("Planet2", I, 5, location = adsk.core.Vector3D.create(0, 0, 0))

        gear2Occ = rotateOccurence(gear2Occ, angle_to_rotate)

        export_to_stl(gear1Occ, export_folder)
        export_to_stl(gear2Occ, export_folder)

    except Exception as error:
        print("Error: " + str(traceback.format_exc()))
