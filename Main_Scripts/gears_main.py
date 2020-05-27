import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.curdir)))
from Fusion_360_scripts.InvoluteScript.involute import Involute
import json
import numpy as np


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

class Gear():

    def __init__(self, name, diameter, assembly, gear_ratio_to_sun = 1, location = [0,0,0]):
        # Easily instantiates properties, as defined in class properties. Can also accept any as a keyword argument.
        self.name = name
        self.diameter = diameter

        self._pressure_angle = assembly.pressure_angle
        self._module = assembly.module

        self.location = location
        self.gear_ratio_to_sun = gear_ratio_to_sun
        self.calculate_parameters()

    def calculate_parameters(self):
        # calculates additional useful parameters using Involute
        involute_generator = Involute(  self._pressure_angle,
                                        self.diameter,
                                        self._module)
        self.diameter = involute_generator.pitch_diameter


class Assembly():

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    babylon_folder = os.path.join(os.path.abspath(base_dir),"Django server", "SimulationBlog", "GearsPilot", "static", "GearsPilot")
    fusion_folder = os.path.join(os.path.abspath(base_dir),"Fusion_360_scripts", "Gearbox_Json_files")


    # replace with more abstract sin/cos formula?
    planet_locations = [[1, 0, 0],
                        [-1, 0, 0],
                        [0, 1, 0],
                        [0, -1, 0]]

    def __init__(self, pressure_angle, sun_diameter, planet_diameter, module, height, name = None):
        # Easily instantiates properties, as defined in class properties. Can also accept any as a keyword argument.
        self.pressure_angle = pressure_angle
        self.sun_diameter = sun_diameter
        self.planet_diameter = planet_diameter
        self.module = module
        self.height = height
        self.name = name
        self.setup_dir()

    def create(self):
        '''
        Distinct function to call once all inputs have been set up.
        Will prepare the
        '''
        self.gears = {} # clear any previous gears

        # Create Sun
        self.gears["Sun"] = Gear(   name = "Sun",
                                    diameter= self.sun_diameter,
                                    assembly = self)

        # Create Ring
        self.gears["Ring"] = Gear(  name = "Ring",
                                    diameter = self.sun_diameter + 2*self.planet_diameter,
                                    assembly = self,
                                    gear_ratio_to_sun = 0)

        # Create Planets
        sun_planet_distance = (self.sun_diameter + self.planet_diameter)/2
        for i in range(4):
            name =  "Planet" + str(i+1)
            self.gears[name] = Gear(    name = name,
                                        diameter = self.planet_diameter,
                                        assembly = self,
                                        location = [sun_planet_distance * ax for ax in Assembly.planet_locations[i]],
                                        gear_ratio_to_sun = self.planet_diameter /  self.sun_diameter)

    def setup_dir(self):
        # create FolderName
        if self.name is None:
            self.name = "Sun_" + str(self.sun_diameter) + "_Planet_" + str(self.planet_diameter)

        self.babylon_path = os.path.join(Assembly.babylon_folder, self.name)
        if not os.path.exists(self.babylon_path):
            os.mkdir(self.babylon_path)


        self.fusion_path = Assembly.fusion_folder
        self.filename = self.name + ".json"


    def save_json(self):
        for pth in [self.babylon_path, self.fusion_path]:
            with open(os.path.join(pth, self.filename), "w") as f:
                json.dump(self.__dict__, f, default=lambda o: o.__dict__, indent = 4)



a = Assembly(pressure_angle=20, sun_diameter=20, planet_diameter=20, module=1, height=5)
a.create()
a.save_json()
