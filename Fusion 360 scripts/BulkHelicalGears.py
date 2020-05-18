

import adsk.core, adsk.fusion, traceback
from math import pi
from .InvoluteScript.involute import Involute

def print(to_print):
    adsk.core.Application.get().userInterface.messageBox(to_print)

def setup_fusion_workspace():
    app = adsk.core.Application.get()
    design = app.activeProduct
    rootComp = design.rootComponent # the top level component in the autodesk component tree
    ui = app.userInterface
    return app, design, rootComp, ui

def create_new_component_and_occurrence(root_component, transform_matrix = None, name = None):
    if transform_matrix is None:
        transform_matrix = adsk.core.Matrix3D.create()
    new_occurrence = root_component.occurrences.addNewComponent(transform_matrix)
    new_component = new_occurrence.component
    if name is not None and isinstance(name, str):
        new_component.name = name
    return new_component, new_occurrence


def create_gear(name, involute, gear_height, location = None):

    app, design, rootComp, ui = setup_fusion_workspace()

    I = involute
    tooth_start_angle = 0

    # create new component
    if location is not None:
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(transform.translation.x + location.x, transform.translation.y + location.y, transform.translation.z + location.z)
        new_component, new_occurence = create_new_component_and_occurrence(rootComp, transform_matrix = transform, name = name)
    else:
        new_component, new_occurence = create_new_component_and_occurrence(rootComp, name = "Planet1")

    # Sketch points
    gear_profile_sketch = new_component.sketches.add(new_component.xYConstructionPlane)
    points = adsk.core.ObjectCollection.create()
    points2 = adsk.core.ObjectCollection.create()

    x1,y1 = I.create_involute1(tooth_start_angle)
    x2,y2 = I.create_involute2(tooth_start_angle)

    for i_point,_ in enumerate(x1):
            points.add(adsk.core.Point3D.create(x1[i_point], y1[i_point], 0))
    gear_profile = gear_profile_sketch.sketchCurves.sketchFittedSplines.add(points)

    for i_point,_ in enumerate(x2):
            points2.add(adsk.core.Point3D.create(x2[i_point], y2[i_point], 0))
    gear_profile2 = gear_profile_sketch.sketchCurves.sketchFittedSplines.add(points2)

    # sketch dedendum circle and addendum arc
    circle_centre = adsk.core.Point3D.create(0,0,0)
    dedendum_circle = gear_profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(circle_centre, I._dedendum_radius)
    addendum_circle = gear_profile_sketch.sketchCurves.sketchArcs.addByCenterStartSweep(circle_centre, points[-1], I._addendum_end_angle - I._addendum_start_angle + tooth_start_angle)
    pitch_circle = gear_profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(circle_centre, I._pitch_radius)
    pitch_circle.isConstruction = True

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

        # unique things:
        #   pressure angle
        #   module
        #   pitch_diameter
        #   height
        #   Name
        #   Location
        pressure_angle = 20
        gear_pitch_diameter = 20
        gear_module = 0.8
        gear_height = 5
        I = Involute(pressure_angle, gear_pitch_diameter, gear_module)


        gear1Comp, gear2Occ = create_gear("Planet1", I, 5, location = adsk.core.Vector3D.create(I.pitch_diameter, 0, 0))
        gear2Comp, gear2Occ = create_gear("Planet1", I, 5, location = adsk.core.Vector3D.create(0, 0, 0))

        gear2_transform = gear2Occ.transform
        angle_to_rotate = 0
        if I._number_of_teeth % 2 == 1:
            angle_to_rotate += pi / I._number_of_teeth
        gear2_transform.setToRotation(pi, adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create(0, 0, 0))
        gear2_transform.translation = adsk.core.Vector3D.create(0, 0, 0)
        gear2Occ.transform = gear2_transform
    except Exception as error:
        print("Error: " + str(traceback.format_exc()))
