from django.shortcuts import render
from django.conf import settings
import json
import glob
import os

# Create your views here.
def index(request):
    staticloc = os.path.join(settings.BASE_DIR, "GearsPilot", "static", "GearsPilot")
    json_files = glob.glob(os.path.join(staticloc, "*", "*.json"))

    sun_teeth_list  = []
    planet_teeth_list  = []
    for file in json_files:
        dirname, filename = os.path.split(file)
        filename = filename.split(".json")[0] # remove .json
        sun_teeth, planet_teeth = filename.split("_")[1::2]
        sun_teeth_list.append(int(sun_teeth))
        planet_teeth_list.append(int(planet_teeth))

    sun_teeth_list.sort()
    planet_teeth_list.sort()
    context = {
                "sun_diff" : sun_teeth_list[1] - sun_teeth_list[0],
                "sun_min" : min(sun_teeth_list),
                "sun_max" : max(sun_teeth_list),
                "planet_diff" : planet_teeth_list[1] - planet_teeth_list[0],
                "planet_min" : min(planet_teeth_list),
                "planet_max" : max(planet_teeth_list),
                }
    return render(request, "GearsPilot/index2.html", context)
