import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.curdir)))
from Fusion_360_scripts.InvoluteScript.involute import Involute
import json
import numpy as np
from math import atan
import subprocess
import glob




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

    def __init__(self, name, variable, parent_point = None):
        '''
        Animation variables:
        - Variable animated (rotation, position, etc.)
        - Speed
        '''
        if variable not in Animation.animation_variables:
            raise KeyError("Variable not animatable in Babylon.js")

        self.name = name
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

        self.start_angle = 0

        self.calculate_parameters()

    def calculate_parameters(self):
        # calculates additional useful parameters using Involute
        involute_generator = Involute(  self._pressure_angle,
                                        self.diameter,
                                        self._module)
        self.diameter = involute_generator.pitch_diameter
        self.number_of_teeth = involute_generator._number_of_teeth

    def add_rotation(self, name, speed = None, parent_point = None):
        if speed is None:
            speed = self.gear_ratio_to_sun
        rot = Animation(name, "rotation.y", parent_point = parent_point)
        rot.add_keyframe(0, 0 * speed)
        rot.add_keyframe(50, np.pi * speed)
        rot.add_keyframe(100, 2 * np.pi * speed)
        self.animations.append(rot)


class Planetary_Gears():

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    babylon_folder = os.path.join(os.path.abspath(base_dir),"DjangoServer", "SimulationBlog", "GearsPilot", "static", "GearsPilot")
    fusion_folder = os.path.join(os.path.abspath(base_dir),"Fusion_360_scripts", "Gearbox_Json_files")
    blender_folder = os.path.join(os.path.abspath(base_dir),"Blender_Scripts", "Json_files")

    @staticmethod
    def rotate_coords(x, y, angle, location = (0,0)):
        x = x - location[0]
        y = y - location[1]
        x_coords = x * np.cos(angle) - y * np.sin(angle)
        y_coords = x * np.sin(angle) + y * np.cos(angle)
        return x_coords, y_coords


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

        self.planet_locations = []
        self.gear_start_angles = []

        self.calculate_speeds()
        self.calculate_planet_positions()
        self.create_gears()
        self.setup_dir()

    def calculate_planet_positions(self):
        number_of_planets = 4
        ring_involute = Involute(self.pressure_angle, self.ring_diameter, self.module)

        x = (self.sun_diameter + self.planet_diameter)/2
        y = 0

        for i in range(number_of_planets):
            # angle to put planet
            desired_angle = 2 * np.pi * i / number_of_planets
            # angle ring would have to rotate with static sun to move planet to desired angle
            effective_ring_angle = desired_angle * (self.ring_speed[1] / self.carrier_speed[1])
            # normalise it to make sure the ring can only rotate an integer number of teeth
            effective_ring_angle -= effective_ring_angle % (2 * ring_involute._angle_between_teeth)
            # convert to actual carrier angle
            carrier_angle = effective_ring_angle * self.carrier_speed[1] / self.ring_speed[1]

            planet_angle = carrier_angle * (self.planet_speed[1] + self.carrier_speed[1]) / self.carrier_speed[1]
            # rotate carrier to correct location
            x_coords, y_coords = Planetary_Gears.rotate_coords(x, y, carrier_angle)
            # add x and y offsets to prevent negative .stl coordinates
            x_coords += self.x_offset
            y_coords += self.y_offset
            # store locations and angles
            self.planet_locations.append([x_coords, y_coords, 0])
            self.gear_start_angles.append(planet_angle)




    def calculate_speeds(self):
        ''' calculates all gear rotational velocities '''
        self.boundary_conditions = ["FixedRing", "FixedSun"]
        self.sun_speed = np.array([1.0, 0.0])
        self.ring_speed = np.array([0.0, 1.0])
        effective_carrier_diameter = (self.sun_diameter + self.planet_diameter)/2

        v_sun = self.sun_diameter * self.sun_speed
        v_ring = self.ring_diameter * self.ring_speed
        self.carrier_speed = (v_sun + v_ring) / (self.sun_diameter + self.ring_diameter)
        self.planet_speed = ((self.sun_diameter + self.planet_diameter) * self.carrier_speed - v_sun) / self.planet_diameter

        for i,_ in enumerate(self.boundary_conditions):
            speeds = [self.sun_speed[i], self.ring_speed[i], self.carrier_speed[i], self.planet_speed[i]]
            speeds = [s for s in speeds if s > 0]
            min_speed = min(speeds)
            self.sun_speed[i] /= min_speed
            self.ring_speed[i] /= min_speed
            self.carrier_speed[i] /= min_speed
            self.planet_speed[i] /= min_speed

        self.planet_speed -= self.carrier_speed # correct for rotations induced by parent relationship

        # convert back to lists for other operations
        self.sun_speed = self.sun_speed.tolist()
        self.ring_speed = self.ring_speed.tolist()
        self.carrier_speed = self.carrier_speed.tolist()
        self.planet_speed = self.planet_speed.tolist()


    def create_gears(self):
        '''
        Distinct function to call once all inputs have been set up.
        '''
        self.gears = {} # clear any previous gears
        self.carriers = {}

        # Create Sun
        self.gears["Sun"] = Gear(   name = "Sun",
                                    diameter= self.sun_diameter,
                                    assembly = self,
                                    location = [self.x_offset, self.y_offset, 0])

        for i, condition in enumerate(self.boundary_conditions):
            self.gears["Sun"].add_rotation(condition, speed = self.sun_speed[i])

        # Create Ring
        self.gears["Ring"] = Gear(  name = "Ring",
                                    diameter = self.sun_diameter + 2*self.planet_diameter,
                                    assembly = self,
                                    gear_ratio_to_sun = self.ring_speed[0],
                                    location = [self.x_offset, self.y_offset, 0])

        for i, condition in enumerate(self.boundary_conditions):
            self.gears["Ring"].add_rotation(condition, speed = self.ring_speed[i])

        # Create Planets
        sun_loc = self.gears["Sun"].location


        sun_planet_distance = (self.sun_diameter + self.planet_diameter)/2
        self.carriers["PlanetCarrier"] = AnimationPivot("PlanetCarrierAnim", sun_loc[0], sun_loc[1], sun_loc[2])

        for i in range(4):
            name =  "Planet" + str(i+1)
            self.gears[name] = Gear(    name = name,
                                        diameter = self.planet_diameter,
                                        assembly = self,
                                        location = self.planet_locations[i],
                                        gear_ratio_to_sun = self.planet_diameter /  self.sun_diameter)
            #self.calculate_gear_start_angle(self.gears[name])
            self.gears[name].start_angle = self.gear_start_angles[i]

            for i, condition in enumerate(self.boundary_conditions):
                self.gears[name].add_rotation(condition, speed = self.planet_speed[i])
                self.gears[name].add_rotation(condition, speed = self.carrier_speed[i], parent_point = self.carriers["PlanetCarrier"])

        # if planets have an odd number of teeth, sun won't start in correct rotation
        if self.gears["Planet1"].number_of_teeth % 2: # if planets have an odd number of teeth
            self.gears["Sun"].start_angle += np.pi / self.gears["Sun"].number_of_teeth


    def setup_dir(self):
        # create FolderName
        if self.name is None:
            self.name = "Sun_" + str(self.gears["Sun"].number_of_teeth)
            self.name += "_Planet_" + str(self.gears["Planet1"].number_of_teeth)
            self.name += "_Pressure_" + str(self.pressure_angle)

        self.babylon_path = os.path.join(Planetary_Gears.babylon_folder, self.name)
        if not os.path.exists(self.babylon_path):
            os.mkdir(self.babylon_path)


        self.fusion_path = Planetary_Gears.fusion_folder

        self.blender_path = Planetary_Gears.blender_folder

        self.filename = self.name + ".json"


    def save_json(self):
        for pth in [self.babylon_path, self.fusion_path, self.blender_path]:
            with open(os.path.join(pth, self.filename), "w") as f:
                json.dump(self.__dict__, f, default=lambda o: o.__dict__, indent = 4)



height = 5 #cm
module = 1
planet_teeth_range = range(10, 25, 2)
sun_teeth_range = range(10, 25, 2)
pressure_angle_range = [14.5, 20]

for pressure_angle in pressure_angle_range:
    for planet_teeth in planet_teeth_range:
        for sun_teeth in sun_teeth_range:
            sun_diam = sun_teeth * 2 / module
            planet_diam = planet_teeth * 2 / module
            a = Planetary_Gears(pressure_angle=pressure_angle, sun_diameter=sun_diam, planet_diameter=planet_diam, module=module, height=height)
            a.save_json()



if True:

    # Run Fusion 360
    fusion360_run_path = r"C:\Users\rishi\AppData\Local\Autodesk\webdeploy\production"
    launchers = glob.glob(os.path.join(fusion360_run_path, "*", "FusionLauncher.exe"))
    prc = subprocess.run(launchers[0]) # will block until program closed

    # Run blender script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    blender_script_path = os.path.join(base_dir, "Blender_Scripts")
    file = "Import_Gears.py"
    subprocess.run(r'D:\Program Files\blender --background --python "{}"'.format(os.path.join(blender_script_path, file)))
