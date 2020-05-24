import os
import sys
sys.path.append("...")
from Fusion_360_scripts.InvoluteScript.involute import Involute
import json
import numpy as np
from collections import namedtuple


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

class Assembly():
    properties = {"name": None,
                "stl_path": None,
                "pressure_angle": None,
                "module":None,
                "height":None,
                "components":None}

    def __init__(self, *args, **kwargs):
        # For easy instantiation of properties, as defined in class properties.
        for i in Assembly.properties:
            if i in kwargs:
                self.__dict__[i] = kwargs[i]
            else:
                self.__dict__[i] = None

    def is_valid(self):
        # returns valid when all properties have been set.
        invalid = any([self.__dict__[prop] is None for prop in Assembly.properties])
        if len(self.components) > 1:
            invalid &= all([comp.is_valid() for comp in self.components])
        return not invalid

class Component():
    properties = {"name": None,
                "location": [0,0,0],
                "gear_ratio_to_sun":None,
                "Assembly":None}

    def __init__(self, *args, **kwargs):
        for i in Component.properties:
            if i in kwargs:
                self.__dict__[i] = kwargs[i]
            else:
                self.__dict__[i] = None

    def is_valid(self):
        # returns valid when all properties have been set.
        invalid = any([self.__dict__[prop] is None for prop in COmponent.properties])
        return not invalid

#base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def create_planetary_gears(module = 1, height = 1, pressure_angle = 20):
    gearset1 = Assembly(module = 1,
                        height = 5,
                        pressure_angle = 20)

    sun = Component(name = "Sun",
                    gear_ratio_to_sun = 1,
                    assembly = gearset1)

    ring = Component(name = "Ring",
                     gear_ratio_to_sun = 1,
                     assembly = gearset1,)

    planets = []
    # planet locations
    # replace with more abstract sin/cos formula?
    planet_locations = [[1, 0, 0],
                        [-1, 0, 0],
                        [0, 1, 0],
                        [0, -1, 0]]

    for i in range(4):
        p = Component(  name = "Planet" + str(i+1),
                        location = planet_locations[i],
                        gear_ratio_to_sun = 1,
                        Assembly = gearset1)
        planets.append(p)

    return [sun, ring, *planets]

a = create_planetary_gears()





'''
Assembly = namedtuple("Assembly", [ "name",
                                    "stl_path",
                                    "pressure_angle",
                                    "module",
                                    "height",
                                    "components"])

Component = namedtuple("Component", [ "name",
                                    "location",
                                    "gear_ratio_to_sun",])


sun1 = Component(name = "Sun1",
                location = (0,0,0),
                gear_ratio_to_sun = 1)

planets = []
for i in range(4):
    planets[i] = Component(name = "Planet"+str(i),
                    location = (0,0,0),
                    gear_ratio_to_sun = 1)

gearset1 = Assembly(name = "gearset1",
                    stl_path=os.path.join(base_dir, "Fusion 360 Scripts", "Saved STL files"),
                    pressure_angle=20,
                    module=1,
                    height = 5,
                    components = ,)
'''
