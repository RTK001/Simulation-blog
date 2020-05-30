import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.curdir)))
from Fusion_360_scripts.InvoluteScript.involute import Involute
import json
import numpy as np
import subprocess
import glob
from shutil import copyfile
from time import sleep


'''
This should create Json input files,
providing info for Fusion 360 scripts to make gears and Babylon to animate them:
Fusion 360:
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
        STL SaveAs Location
        File structure (for multiple files)
Babylon:
    Gear ratios
    STL Saveas Location
    File structure
'''

class Animation():
    animation_variables = {"position": "BABYLON.Animation.ANIMATIONTYPE_VECTOR3",
                            "position.x": "BABYLON.Animation.ANIMATIONTYPE_FLOAT",
                            "position.y": "BABYLON.Animation.ANIMATIONTYPE_FLOAT",
                            "position.z": "BABYLON.Animation.ANIMATIONTYPE_FLOAT",
                            "rotation.x":"BABYLON.Animation.ANIMATIONTYPE_FLOAT",
                            "rotation.y":"BABYLON.Animation.ANIMATIONTYPE_FLOAT",
                            "rotation.z":"BABYLON.Animation.ANIMATIONTYPE_FLOAT",}

    def __init__(self, variable, parent_point = None):
        '''
        Animation variables:
        - Variable animated (rotation, position, etc.)
        - Speed
        '''
        if variable not in Animation.animation_variables:
            raise KeyError("Variable not animatable in Babylon.js")

        self.variable = variable
        self.type = Animation.animation_variables[variable]
        self.keyframes = []
        if parent_point:
            self.parent_point = parent_point

    def add_keyframe(self, frame, value):
        self.keyframes.append({"frame":frame, "value":value})

class AnimationPivot():
    def __init__(self, name, x=0, y=0, z=0):
        self.name = name
        self.x = x
        self.y = y
        self.z = z

class Gear():

    def __init__(self, name, diameter, assembly, gear_ratio_to_sun = 1, location = [0,0,0]):
        # Easily instantiates properties, as defined in class properties. Can also accept any as a keyword argument.
        self.name = name
        self.diameter = diameter
        self.filename = name + ".stl"

        self._pressure_angle = assembly.pressure_angle
        self._module = assembly.module

        self.location = location
        self.gear_ratio_to_sun = gear_ratio_to_sun
        self.animations = []

        self.calculate_parameters()

    def calculate_parameters(self):
        # calculates additional useful parameters using Involute
        involute_generator = Involute(  self._pressure_angle,
                                        self.diameter,
                                        self._module)
        self.diameter = involute_generator.pitch_diameter

    def add_rotation(self, speed = None, parent_point = None):
        if speed is None:
            speed = self.gear_ratio_to_sun
        rot = Animation("rotation.y", parent_point = parent_point)
        rot.add_keyframe(0, 0 * speed)
        rot.add_keyframe(50, np.pi * speed)
        rot.add_keyframe(100, 2 * np.pi * speed)
        self.animations.append(rot)


class Planetary_Gears():

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    babylon_folder = os.path.join(os.path.abspath(base_dir),"Django server", "SimulationBlog", "GearsPilot", "static", "GearsPilot")
    fusion_folder = os.path.join(os.path.abspath(base_dir),"Fusion_360_scripts", "Gearbox_Json_files")

    def __init__(self, pressure_angle, sun_diameter, planet_diameter, module, height, name = None):
        # Easily instantiates properties, as defined in class properties. Can also accept any as a keyword argument.
        self.pressure_angle = pressure_angle
        self.sun_diameter = sun_diameter
        self.planet_diameter = planet_diameter
        self.ring_diameter = self.sun_diameter + 2*self.planet_diameter
        self.module = module
        self.height = height
        self.name = name

        self.x_offset = self.sun_diameter + 2*self.planet_diameter
        self.y_offset = self.x_offset

        self.setup_dir()
        self.calculate_planet_locations()
        self.calculate_speeds()

    def calculate_planet_locations(self):
        number_of_planets = 4
        # x and y offsets, to keep stl coordinates positive, as babylon doesn't support negative .stl coordinates
        dist = (self.sun_diameter + self.planet_diameter)/2
        x = lambda i: dist * np.cos(i * 2 * np.pi / number_of_planets) + self.x_offset
        y = lambda i: dist * np.sin(i * 2 * np.pi / number_of_planets) + self.y_offset
        self.planet_locations = []
        for i in range(number_of_planets):
            self.planet_locations.append([x(i), y(i), 0])

    def calculate_speeds(self):
        ''' calculates all gear rotational velocities '''
        self.sun_speed = 1.0
        self.ring_speed = 0.0
        v_sun = self.sun_diameter * self.sun_speed
        v_ring = self.ring_diameter * self.ring_speed
        effective_carrier_diameter = (self.sun_diameter + self.planet_diameter)/2

        self.carrier_speed = (v_sun + v_ring) / (self.sun_diameter + self.ring_diameter)
        self.planet_speed = (((self.sun_diameter + self.planet_diameter) * self.carrier_speed - v_sun) / self.planet_diameter) - self.carrier_speed
        #self.planet_speed = (v_ring - (self.ring_diameter - self.planet_diameter) * self.carrier_speed) / self.planet_diameter

        #self.planet_speed = (v_ring - v_sun) / (2 * self.planet_diameter)
        #self.carrier_speed = (v_sun + self.planet_speed * self.planet_diameter) / effective_carrier_diameter

        print("sun_speed: {0}".format(self.sun_speed))
        print("ring_speed: {0}".format(self.ring_speed))
        print("v_sun: {0}".format(v_sun))
        print("v_ring: {0}".format(v_ring))
        print("planet_speed: {0}".format(self.planet_speed))
        print("carrier_speed: {0}".format(self.carrier_speed))

    def create(self):
        '''
        Distinct function to call once all inputs have been set up.
        Will prepare the
        '''
        self.gears = {} # clear any previous gears

        # Create Sun
        self.gears["Sun"] = Gear(   name = "Sun",
                                    diameter= self.sun_diameter,
                                    assembly = self,
                                    location = [self.x_offset, self.y_offset, 0])
        self.gears["Sun"].add_rotation()

        # Create Ring
        self.gears["Ring"] = Gear(  name = "Ring",
                                    diameter = self.sun_diameter + 2*self.planet_diameter,
                                    assembly = self,
                                    gear_ratio_to_sun = self.ring_speed,
                                    location = [self.x_offset, self.y_offset, 0])

        # Create Planets
        sun_loc = self.gears["Sun"].location
        planet_carrier = AnimationPivot("PlanetCarrier", sun_loc[0], sun_loc[1], sun_loc[2])
        sun_planet_distance = (self.sun_diameter + self.planet_diameter)/2
        for i in range(4):
            name =  "Planet" + str(i+1)
            self.gears[name] = Gear(    name = name,
                                        diameter = self.planet_diameter,
                                        assembly = self,
                                        location = self.planet_locations[i],
                                        gear_ratio_to_sun = self.planet_diameter /  self.sun_diameter)
            self.gears[name].add_rotation(speed = self.planet_speed)
            self.gears[name].add_rotation(speed = self.carrier_speed, parent_point = planet_carrier)

    def setup_dir(self):
        # create FolderName
        if self.name is None:
            self.name = "Sun_" + str(self.sun_diameter) + "_Planet_" + str(self.planet_diameter)

        self.babylon_path = os.path.join(Planetary_Gears.babylon_folder, self.name)
        if not os.path.exists(self.babylon_path):
            os.mkdir(self.babylon_path)


        self.fusion_path = Planetary_Gears.fusion_folder
        self.filename = self.name + ".json"


    def save_json(self):
        for pth in [self.babylon_path, self.fusion_path]:
            with open(os.path.join(pth, self.filename), "w") as f:
                json.dump(self.__dict__, f, default=lambda o: o.__dict__, indent = 4)



a = Planetary_Gears(pressure_angle=20, sun_diameter=20, planet_diameter=20, module=1, height=5)
a.create()
a.save_json()


# Run Fusion 360
fusion360_run_path = r"C:\Users\rishi\AppData\Local\Autodesk\webdeploy\production"
launchers = glob.glob(os.path.join(fusion360_run_path, "*", "FusionLauncher.exe"))
#prc = subprocess.run(launchers[-1]) # will block until program closed


# Run blender script
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
blender_script_path = os.path.join(base_dir, "Blender_Scripts")
file = os.listdir(blender_script_path)[0];
dst = r"D:\Blender_Tests"
copyfile(os.path.join(blender_script_path, file), os.path.join(dst, file))
subprocess.run(r"D:\Program Files\blender --background --python " + os.path.join(dst, file))
sleep(10)

os.remove(os.path.join(dst, file))
