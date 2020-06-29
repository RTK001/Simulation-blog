from django.shortcuts import render
from django.conf import settings
import json
import glob
import os

from pprint import pprint

def find_min_max_diff(json_files, name, index, context):
    vals_list = []
    for json_file in json_files:
        _, filename = os.path.split(json_file)
        filename = filename.split(".json")[0]
        value = filename.split("_")[2 * index + 1]
        vals_list.append(int(value))
    vals_list = list(set(vals_list))
    vals_list.sort()
    try:
        context[name + "_diff"] = vals_list[1] - vals_list[0]
        context[name + "_min"] = min(vals_list)
        context[name + "_max"] = max(vals_list)
    except IndexError:
        context[name + "_diff"] = 0
        context[name + "_min"] = min(vals_list)
        context[name + "_max"] = max(vals_list)
    return context


# Create your views here.
def index(request):
    staticloc = os.path.join(settings.BASE_DIR, "GearsPilot", "static", "GearsPilot")
    json_files = glob.glob(os.path.join(staticloc, "*", "*.json"))
    context = {"jsons" : {}}
    for file in json_files:
        with open(file, "r") as f:
            key = os.path.split(file)[1].split(".json")[0]
            context["jsons"][key] = json.dumps(json.load(f))

    pprint(context)
    parameters = ["sun", "planet", "pressure"]
    for index, name in enumerate(parameters):
        context = find_min_max_diff(json_files, name, index, context)
    return render(request, "GearsPilot/index2.html", context)
