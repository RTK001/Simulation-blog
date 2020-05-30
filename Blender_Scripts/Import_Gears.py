import bpy
import os
import json
from math import pi


def create_point(name, x=0, y=0, z=0):
    msh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, msh)
    obj.show_name = True
    points = msh.from_pydata([(float(x), float(y), float(z))],[], [])
    msh.update()
    bpy.context.collection.objects.link(obj)
    return obj


def animate_from_list(name, to_animate, prop, lst, interpolation="LINEAR"):
    ''' dict should contain frame:value pairs'''
    animation_variables_dict = {"position": ["location", -1],
                                "position.x" : ["location", 0],
                                "position.y" : ["location", 2],
                                "position.z" : ["location", 1],
                                "rotation": ["rotation_euler", -1],
                                "rotation.x" : ["rotation_euler", 0],
                                "rotation.y" : ["rotation_euler", 2],
                                "rotation.z" : ["rotation_euler", 1],}

    data_path, index = animation_variables_dict[prop]


    to_animate.animation_data_create()
    to_animate.animation_data.action = bpy.data.actions.new(name=name)
    fcurve = to_animate.animation_data.action.fcurves.new(data_path=data_path, index = index)
    for frame in lst:
        keyframe_one = fcurve.keyframe_points.insert(frame=frame["frame"], value=frame["value"])
        keyframe_one.interpolation = "LINEAR"


C = bpy.context
D = bpy.data

# remove mesh Cube
if "Cube" in bpy.data.meshes:
    mesh = bpy.data.meshes["Cube"]
    print("removing mesh", mesh)
    bpy.data.meshes.remove(mesh)

# specify json
pth = r"C:\Users\rishi\Google Drive\Simulation blog\Django server\SimulationBlog\GearsPilot\static\GearsPilot\Sun_20_Planet_20"
files = os.listdir(pth)
json_file = ""

# Load each .stl file
for file in files:
    if ".json" in file:
        with open(os.path.join(pth, file), "r") as f:
            json_file = json.load(f)
    else:
        bpy.ops.import_mesh.stl(filepath = os.path.join(pth, file))

# Move gears to desired locations
for name, gear in json_file["gears"].items():
    loc = gear["location"]
    bpy.data.objects[name].location.x = loc[0] - json_file["x_offset"]
    bpy.data.objects[name].location.y = loc[1] - json_file["y_offset"]
    bpy.data.objects[name].location.z = loc[2]


bpy.context.scene.frame_end = 100


for name, gear in json_file["gears"].items():
    for ani in gear["animations"]:
        # if moving relative to a parent point
        if "parent_point" in ani:
            pt = ani["parent_point"]
            obj = create_point(pt["name"], pt["x"], pt["z"], pt["y"])
            bpy.data.objects[name].parent = obj
            to_animate = obj
        else:
            to_animate = bpy.data.objects[name]

        animate_from_list("rotation", to_animate, ani["variable"], ani["keyframes"])


# export to .gltf
filepath = os.path.join(json_file["babylon_path"], json_file["name"])
bpy.ops.export_scene.gltf(export_format="GLB", filepath=filepath)
