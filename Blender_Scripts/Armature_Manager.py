import bpy
from Blender_Library import animate_from_list

class ArmatureManager():

    def __init__(self, name, location=(0,0,0)):
        self.name = name
        self.ID = name
        bpy.ops.object.armature_add(enter_editmode=True, location = location)
        arm_object = bpy.data.objects["Armature"]
        arm_object.name = name
        self._armature_object = arm_object

        arm = bpy.data.objects[name].data
        arm.name = name + "arm"
        self._armature = arm
        arm.edit_bones.remove(arm.edit_bones[0])

        # Alternate way to create armature
        #self._armature = bpy.data.armatures.new(name)
        #self._armature_object = bpy.data.objects.new(name, self._armature)

    @property
    def armature(self):
        return bpy.data.armatures[self.name + "arm"]

    @property
    def armature_object(self):
        return bpy.data.objects[self.name]

    def select_armature_object(self):
        bpy.context.view_layer.objects.active = self.armature_object

    def set_to_edit_mode(self):
        self.select_armature_object()
        bpy.ops.object.mode_set(mode="EDIT")

    def add_bone(self, name, location = (0,0,0), child = None, prevent_duplicates = False):
        # Check if the requested bone already exists and should not be duplicated
        if prevent_duplicates and name+"bone" in bpy.data.armatures[self.name + "arm"].bones:
            return bpy.data.armatures[self.name + "arm"].bones[name + "bone"]

        self.set_to_edit_mode()
        new_bone = self.armature.edit_bones.new(name + "bone")
        new_bone.head = location
        new_bone.tail = (location[0], location[1] + 1, location[2])

        if child:
            child = bpy.data.objects[child.name]
            bpy.context.view_layer.objects.active = child # set gear as active
            bpy.ops.object.mode_set(mode="EDIT") # set to edit mode to add new bones
            # Parent the object to it's animation skeleton bone.
            child = bpy.data.objects[child.name]
            child.parent = self.armature_object
            child.parent_type = "BONE"
            child.parent_bone = child.name + "bone"

        self.select_armature_object()
        bpy.ops.object.mode_set(mode="OBJECT")

        return self.armature.bones[name + "bone"]

    def setup_animation(self):
        if "animation_setup" not in self.__dict__ or not self.animation_setup:
            self.armature.animation_data_create()
            self.animation_setup = True

    def add_animation(self, bone, action_name, data_path, index, frame_vals_list):
        self.setup_animation()

        # Set to pose mode
        self.select_armature_object()
        bpy.ops.object.mode_set(mode="POSE")

        # Add action or set existing action to active
        if action_name not in bpy.data.actions:
            self.armature.animation_data.action = bpy.data.actions.new(name=action_name)
            action = self.armature.animation_data.action
            action.use_fake_user = True
        else:
            action = bpy.data.actions[action_name]
            self.armature.animation_data.action = action

        # animate bone
        for frame, value in frame_vals_list:
            # get pose bone
            pose_bone = self.armature_object.pose.bones[bone.name]
            pose_bone.rotation_euler[index] = value
            pose_bone.keyframe_insert(data_path, frame = frame)

        #fcurve = action.fcurves.new(data_path=data_path, index = index)
        #for frame, value in frame_vals_list:
        #    keyframe_one = fcurve.keyframe_points.insert(frame=frame, value=value)
        #    keyframe_one.interpolation = "LINEAR"


        #animate_from_list(animation_dict["name"], bone, animation_dict["variable"], animation_dict["keyframes"], interpolation="LINEAR")
            # add action to armature
            #for each frame:
                # add frames to action
