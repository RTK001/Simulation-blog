import os
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



Assembly = namedtuple("Assembly", [ "name",
                                    "stl_path",
                                    "pressure_angle",
                                    "module",
                                    "height",
                                    "components"])

Component = namedtuple("Assembly", [ "name",
                                    "location",
                                    "file",
                                    "gear_ratio_to_sun",])




'''

class Assembly():
    properties = {"stl_path": None,
                "pressure_angle": None,
                "module":None,
                "height":None}

    def __init__(self):
        for i in Assembly.properties:
            self.__dict__[i] = None

    def is_valid(self):
        invalid = any([self.__dict__[prop] is None for prop in Assembly.properties])
        return not invalid

class Component():
    properties = {"stl_path": None,
                "pressure_angle": None,
                "module":None,
                "height":None}

    def __init__(self):
        self.name = None
        self.location  = None
        self.file = None
        self.gear_ratio_to_sun  = None

'''
