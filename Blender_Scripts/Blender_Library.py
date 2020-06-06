import bpy

'''
library of blender helper functions
'''

def create_point(name, x=0, y=0, z=0):
    '''
    Creates a mesh & object from a single point.
    Originally used for animating roations about a pivot.
    '''
    msh = bpy.data.meshes.new(name + "_mesh")
    obj = bpy.data.objects.new(name, msh)
    obj.show_name = True
    points = msh.from_pydata([(float(x), float(y), float(z))],[], [])
    msh.update()
    bpy.context.collection.objects.link(obj)
    return obj


def animate_from_list(action_name, to_animate, prop, lst, interpolation="LINEAR"):
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
    action = to_animate.animation_data.action
    track = to_animate.animation_data.nla_tracks.new()
    to_animate.animation_data.action = bpy.data.actions.new(name=action_name)
    to_animate.animation_data.action.use_fake_user = True

    '''
    if action_name not in bpy.data.actions:
        to_animate.animation_data.action = bpy.data.actions.new(name=action_name)
        to_animate.animation_data.action.use_fake_user = True
    else:
        print("re-using action {}".format(action_name))
        to_animate.animation_data.action = bpy.data.actions[action_name]
    '''
    
    fcurve = to_animate.animation_data.action.fcurves.new(data_path=data_path, index = index)
    for frame in lst:
        keyframe_one = fcurve.keyframe_points.insert(frame=frame["frame"], value=frame["value"])
        keyframe_one.interpolation = "LINEAR"

    action = to_animate.animation_data.action
    track.strips.new(action.name, action.frame_range[0], action)


def remove_cube():
    # remove mesh Cube
    if "Cube" in bpy.data.meshes:
        mesh = bpy.data.meshes["Cube"]
        print("removing mesh", mesh)
        bpy.data.meshes.remove(mesh)
