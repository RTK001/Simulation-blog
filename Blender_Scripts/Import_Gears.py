import bpy
import os
import glob
import json
from math import pi

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Blender_Library import *
from Armature_Manager import ArmatureManager



class GearsJsonLoader():

    animation_variables_dict = {"position": ["location", -1],
                                "position.x" : ["location", 0],
                                "position.y" : ["location", 2],
                                "position.z" : ["location", 1],
                                "rotation": ["rotation_euler", -1],
                                "rotation.x" : ["rotation_euler", 0],
                                "rotation.y" : ["rotation_euler", 2],
                                "rotation.z" : ["rotation_euler", 1],}

    def __init__(self, filepath):
        self.filepath = filepath
        self.dirname, self.filename = os.path.split(self.filepath)
        with open(self.filepath, "r") as f:
            self.loaded_json = json.load(f)


        self.name =  self.loaded_json["name"]
        self.offsets = (self.loaded_json["x_offset"], self.loaded_json["y_offset"], 0)

        self.gears_names = []
        self._gears = []
        #self.load_gears()

    @property
    def gears(self):
        return [bpy.data.object[name] for name in self.gears_names]

    def subtract_offsets(self, loc):
        temp_sub = lambda a,b: a - b
        return list(map(temp_sub, loc, self.offsets))

    def load_gears(self):
        '''
        files = glob.glob(os.path.join(self.dirname, "*.stl"))
        for file in files:
            bpy.ops.import_mesh.stl(filepath = os.path.join(pth, file))
        '''
        self.gears_names = [] # reset gear_names
        for gear_name, gear in self.loaded_json["gears"].items():
            filepath = os.path.join(self.dirname, gear_name + ".stl")
            bpy.ops.import_mesh.stl(filepath = filepath)
            self.gears_names.append(gear_name)
            gear_object = bpy.data.objects[gear_name]
            gear_object.location = self.subtract_offsets(gear["location"])

    def create_carrier(self, carrier_dict):
        loc = (carrier_dict["x"], carrier_dict["y"], carrier_dict["z"])
        loc = self.subtract_offsets(loc)
        return self.armature_manager.add_bone(carrier_dict["name"], location = loc, prevent_duplicates = True) # add carrier as bone

    def create_skeleton(self):
        if "armature_manager" not in self.__dict__ or not self.armature_manager:
            self.armature_manager = ArmatureManager(self.name)

        self.gear_bones = []
        for name, gear in self.loaded_json["gears"].items():
            loc = (gear["location"][0], gear["location"][1], gear["location"][2]) # Save carrier location
            loc = self.subtract_offsets(loc)
            self.gear_bones.append(self.armature_manager.add_bone(gear["name"], location = loc))

        # add carriers
        for name, carrier in self.loaded_json["carriers"].items():
            loc = (carrier["x"], carrier["y"], carrier["z"]) # Save carrier location
            loc = self.subtract_offsets(loc)
            self.armature_manager.add_bone(carrier["name"], location = loc) # add carrier as bone


    def load_all_skeleton(self):
        # Setup armature manager
        if "armature_manager" not in self.__dict__ or not self.armature_manager:
            self.armature_manager = ArmatureManager(self.name)

        # Import each gear
        self.gears_names = [] # reset gear_names
        for gear_name, gear in self.loaded_json["gears"].items():
            filepath = os.path.join(self.dirname, gear_name + ".stl")
            bpy.ops.import_mesh.stl(filepath = filepath)
            self.gears_names.append(gear_name)
            gear_object = bpy.data.objects[gear_name]
            #gear_object.location = self.subtract_offsets(gear_object.location)

            # create rigging bones for gear
            loc = (gear["location"][0], gear["location"][1], gear["location"][2]) # Save carrier location
            loc = self.subtract_offsets(loc)
            gear_bone = self.armature_manager.add_bone(gear["name"], location = loc, child = gear_object)

            # add animations for each gear
            for animation in gear["animations"]: # need to deal with case without animations
                if "parent_point" in animation:
                    self.create_carrier(animation["parent_point"])
                animation_info = GearsJsonLoader.animation_variables_dict[animation["variable"]]
                #variable = "pose.bones['{0}'].{1}".format(gear_bone.name, animation_info[0])
                variable = animation_info[0]
                index = animation_info[1]
                keyframe_list = [(kf["frame"], kf["value"]) for kf in animation["keyframes"]]
                self.armature_manager.add_animation(gear_bone, animation["name"], variable, index, keyframe_list)


# specify json
pth = r"C:\Users\rishi\Google Drive\Simulation blog\Django server\SimulationBlog\GearsPilot\static\GearsPilot\Sun_20_Planet_20"
files = os.listdir(pth)
json_file = "Sun_20_Planet_20.json"

remove_cube()
#a = ArmatureManager("GearsArmature")
gl = GearsJsonLoader(os.path.join(pth, json_file))
#gl.load_all_skeleton()


gl.load_gears()
carrier = create_point("Carrier")
carrier_animated = []
for name, gear in gl.loaded_json["gears"].items():
    for animation in gear["animations"]:
        if "parent_point" in animation:
            bpy.data.objects[gear["name"]].parent = carrier
            if animation["name"] in carrier_animated:
                continue
            to_animate = carrier
            carrier_animated.append(animation["name"])
        else:
            to_animate = bpy.data.objects[gear["name"]]

        animate_from_list(animation["name"], to_animate, animation["variable"], animation["keyframes"])


bpy.context.scene.frame_end = 100

# export to .gltf
filepath = os.path.join(gl.loaded_json["babylon_path"], gl.loaded_json["name"])
bpy.ops.export_scene.gltf(export_format="GLB", filepath=filepath)

'''
# Load each .stl file
#for file in files:
#    if ".json" in file:
#        with open(os.path.join(pth, file), "r") as f:
#            json_file = json.load(f)
#    else:
#        bpy.ops.import_mesh.stl(filepath = os.path.join(pth, file))


# Setup animation rigging structure
#armature = bpy.data.armatures.new(json_file["name"])

bpy.ops.object.armature_add(enter_editmode = True, location = (0,0,0))
armature = bpy.data.objects["Armature"]
armature.data.edit_bones.remove(armature.data.edit_bones[0])


# Setup any carrier bones

# cycle through each carrier to be made
for name, carrier in json_file["carriers"].items():
    loc = (carrier["x"], carrier["y"], carrier["z"])
    a.add_bone(carrier["name"])

    bpy.context.view_layer.objects.active = bpy.data.objects["Armature"] # set armature as active
    bpy.ops.object.mode_set(mode="EDIT") # set to edit mode to add new bones
    armature = bpy.data.objects["Armature"] # redefine armature after memory wipe when changing modes

    loc = (carrier["x"], carrier["y"], carrier["z"])

    carrier_bone = armature.data.edit_bones.new(carrier["name"]+"bone")
    carrier_bone.head = (loc[0], loc[1], loc[2] + 1)
    carrier_bone.tail = (loc[0], loc[1], loc[2] + 1)

    #bpy.context.view_layer.objects.active = bpy.data.objects["Armature"] # set armature as active
    bpy.ops.object.mode_set(mode="OBJECT")



# Move gears to desired locations
for name, gear in json_file["gears"].items():
    loc = gear["location"]
    #bpy.data.objects[name].location.x = loc[0] - json_file["x_offset"]
    #bpy.data.objects[name].location.y = loc[1] - json_file["y_offset"]
    #bpy.data.objects[name].location.z = loc[2]
    loc[0] -= json_file["x_offset"]
    loc[1] -= json_file["y_offset"]
    a.add_bone(gear["name"], location = loc, child = bpy.data.objects[name])


    # create animation rigging for each gear
    bpy.context.view_layer.objects.active = bpy.data.objects["Armature"]
    bpy.ops.object.mode_set(mode="EDIT")
    armature = bpy.data.objects["Armature"]
    gear_bone = armature.data.edit_bones.new(name+"bone")
    gear_bone.head = bpy.data.objects[name].location
    gear_bone.tail = (loc[0] - json_file["x_offset"], loc[1] - json_file["y_offset"], loc[2] + 1)

    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.context.view_layer.objects.active = bpy.data.objects[name] # set gear as active
    bpy.ops.object.mode_set(mode="EDIT") # set to edit mode to add new bones
    # Parent the object to it's animation skeleton bone.
    bpy.data.objects[name].parent = bpy.data.objects["Armature"]
    bpy.data.objects[name].parent_type = "BONE"
    bpy.data.objects[name].parent_bone = name+"bone"

    bpy.ops.object.mode_set(mode="OBJECT")



armature = bpy.data.objects["Armature"]
#[print(i.name) for i in armature.data.bones]


bpy.ops.object.mode_set(mode="OBJECT")


for name, gear in json_file["gears"].items():
    for ani in gear["animations"]:
        gear = bpy.data.objects[name]
        gearbone = bpy.data.objects["Armature"].data.bones[name + "bone"]
        # if moving relative to a parent point
        if "parent_point" in ani:
            parent_name = ani["parent_point"]["name"]
            parent_point = bpy.data.objects["Armature"].data.bones[parent_name + "bone"]
            gear.parent = parent_point

        # ReWrite below to
        #   - create bones at each gear
        #   - Add actions to each bone
        #   - add animations to each action


        if "parent_point" in ani:
            pt = ani["parent_point"]

            obj = create_point(pt["name"], pt["x"], pt["z"], pt["y"])
            bpy.data.objects[name].parent = obj
            to_animate = obj

            if pt["name"] in bpy.data.objects:
                to_animate = bpy.data.objects[pt["name"]]
            else:
                obj = create_point(pt["name"], pt["x"], pt["z"], pt["y"])
                bpy.data.objects[name].parent = obj
                to_animate = obj
        else:
            to_animate = bpy.data.objects[name]


        #animate_from_list(ani["name"], to_animate, ani["variable"], ani["keyframes"])


# export to .gltf
filepath = os.path.join(json_file["babylon_path"], json_file["name"])
bpy.ops.export_scene.gltf(export_format="GLB", filepath=filepath)

'''
