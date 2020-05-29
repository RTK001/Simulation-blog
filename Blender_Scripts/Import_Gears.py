import bpy
import os
import json
from math import pi

def create_point(name, x=0, y=0, z=0):
    msh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, msh)
    obj.show_name = True
    msh.from_pydata([(float(x), float(y), float(z))],[], [])
    msh.update()
    return obj, msh


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

animation_variables_dict = {"position": "location",
                            "position.x" : "location.x",
                            "position.y" : "location.y",
                            "position.z" : "location.z",
                            "rotation": "rotation_euler",
                            "rotation.x" : "rotation_euler.x",
                            "rotation.y" : "rotation_euler.z",
                            "rotation.z" : "rotation_euler.y",}

for name, gear in json_file["gears"].items():
    for ani in gear["animations"]:
        prop = animation_variables_dict[ani["variable"]]
        # if moving relative to a parent point
        if ani["parent_point"]:
            pt = ani["parent_point"]
            obj, msh = create_point(name+"_parent", pt[0], pt[2], pt[1])
            bpy.data.objects[name].parent = obj
            for frame_data in ani["keyframes"]:
                exec("bpy.data.objects[name + '_parent']." + prop + " = " + str(frame_data["value"]))
                data_path = prop.split(".")[0]
                bpy.data.objects[name+"_parent"].keyframe_insert(data_path=data_path, frame=frame_data["frame"])
        # If moving on own axes
        else:
            for frame_data in ani["keyframes"]:
                exec("bpy.data.objects[name]." + prop + " = " + str(frame_data["value"]))
                data_path = prop.split(".")[0]
                bpy.data.objects[name].keyframe_insert(data_path=data_path, frame=frame_data["frame"])


'''
# create animations
for name, gear in json_file["gears"].items():
    for ani in gear["animations"]:

'''
