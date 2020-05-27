import adsk.core, adsk.fusion, traceback
from math import pi
from .InvoluteScript.involute import Involute
import os
from .FusionFunctionLibrary.FusionFunctionLibrary import *
import json


def create_cylinder(name, radius, height, location = None):
    app, design, rootComp, ui = setup_fusion_workspace()

    # create new component
    if location is not None:
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(  transform.translation.x + location.x,
                                                            transform.translation.y + location.y,
                                                            transform.translation.z + location.z)
        new_component, new_occurence = create_component(rootComp, transform_matrix = transform, name = name)
    else:
        new_component, new_occurence = create_component(rootComp, name = name)

    # Create Sketch
    cylinder_sketch = new_component.sketches.add(new_component.xYConstructionPlane)
    centre_point = adsk.core.Point3D.create(new_occurence.transform.translation.x,
                                            new_occurence.transform.translation.y,
                                            new_occurence.transform.translation.z)
    text_point = adsk.core.Point3D.create(  new_occurence.transform.translation.x + 1.5*radius,
                                            new_occurence.transform.translation.y + 1.5*radius,
                                            new_occurence.transform.translation.z)
    cylinder_circle = cylinder_sketch.sketchCurves.sketchCircles.addByCenterRadius(centre_point, radius)
    cylinder_sketch.sketchDimensions.addDiameterDimension(cylinder_circle, text_point)

    ext = Extrude(new_component, cylinder_sketch.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation, height)

    return new_component, new_occurence


def create_gear(name, involute, gear_height, location = None, tooth_start_angle = 0):

    app, design, rootComp, ui = setup_fusion_workspace()

    # create new component
    new_component, new_occurence = create_component(rootComp, location = location, name = name)
    # Sketch points

    gear_profile_sketch = new_component.sketches.add(new_component.xYConstructionPlane)

    # create tooth profile for involute 1
    x1,y1 = involute.create_involute1(tooth_start_angle)
    points = points_from_coordinates(x1, y1)
    gear_profile = gear_profile_sketch.sketchCurves.sketchFittedSplines.add(points)

    # create tooth profile for involute 2
    x2,y2 = involute.create_involute2(tooth_start_angle)
    points2 = points_from_coordinates(x2, y2)
    gear_profile2 = gear_profile_sketch.sketchCurves.sketchFittedSplines.add(points2)

    # sketch dedendum circle and addendum arc
    circle_centre = adsk.core.Point3D.create(0,0,0)
    dedendum_circle = gear_profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(circle_centre, involute._dedendum_radius)
    addendum_circle = gear_profile_sketch.sketchCurves.sketchArcs.addByCenterStartSweep(circle_centre, points[-1], involute._addendum_end_angle - involute._addendum_start_angle + tooth_start_angle)
    pitch_circle = gear_profile_sketch.sketchCurves.sketchCircles.addByCenterRadius(circle_centre, involute._pitch_radius)
    pitch_circle.isConstruction = True

    # constrain points on addendum circle
    gear_profile_sketch.geometricConstraints.addCoincident(addendum_circle.startSketchPoint, gear_profile.endSketchPoint)
    gear_profile_sketch.geometricConstraints.addCoincident(addendum_circle.endSketchPoint, gear_profile2.endSketchPoint)

    # Extrude Gear circle
    ext = Extrude(new_component, gear_profile_sketch.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation, gear_height)

    # Extrude gear tooth
    ext2 = Extrude(new_component, gear_profile_sketch.profiles.item(1), adsk.fusion.FeatureOperations.JoinFeatureOperation, gear_height)

    # create circular tooth pattern
    pattern = new_component.features.circularPatternFeatures

    patternInputFeatures = adsk.core.ObjectCollection.create()
    patternInputFeatures.add(ext2)
    patternInput = pattern.createInput(patternInputFeatures, new_component.zConstructionAxis); # create an extrusion using the new feature operation
    patternInput.quantity = adsk.core.ValueInput.createByReal(involute._number_of_teeth)
    patternInput.totalAngle = adsk.core.ValueInput.createByString("360 deg")
    pattern.isSymmetric = False

    patternFeature = pattern.add(patternInput)

    return new_component, new_occurence


def create_stl_from_json(parsed_json, delete_after_export = True):
    export_folder = parsed_json["babylon_path"]
    try:
        os.mkdir(export_folder)
    except FileExistsError:
        pass

    component_list = []
    occurrence_list = []

    for component in parsed_json["gears"]:
        component = parsed_json["gears"][component]
        I = Involute(component["_pressure_angle"], component["diameter"], component["_module"])

        angle_to_rotate = 0
        if I._number_of_teeth % 2 == 1:
            angle_to_rotate += pi/I._number_of_teeth

        loc = adsk.core.Vector3D.create( component["location"][0], component["location"][1], component["location"][2])
        comp, occ = create_gear(component["name"], I, parsed_json["height"], location = loc, tooth_start_angle = angle_to_rotate)
        component_list.append(comp)
        occurrence_list.append(occ)

        if component["name"] == "Ring":
            housingComp, housingOcc = create_cylinder("RingGear", I._pitch_radius + 5, parsed_json["height"])
            booleanSubtract(housingComp, component_list[-1])
            component_list.append(housingComp)
            occurrence_list.append(housingOcc)

        export_to_stl(occurrence_list[-1], export_folder)

    if delete_after_export:
        [occ.deleteMe() for occ in occurrence_list]


def run(context):
    try:
        '''
        Input Parameters:
         System
           pressure angle
           module
           height
         Gear
           pitch_diameter
           Name
           Location
         File
            SaveAs Location
            File structure (for multiple files)
        '''

        json_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Gearbox_Json_files")
        json_files = os.listdir(json_folder)

        for file in json_files:
            with open(os.path.join(json_folder, file), "r") as gear_json:
                loaded_object = json.load(gear_json)
                create_stl_from_json(loaded_object)


    except Exception as error:
        print("Error: " + str(traceback.format_exc()))
