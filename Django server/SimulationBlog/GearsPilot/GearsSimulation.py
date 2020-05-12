
import os
import numpy
import stl
import json

to_json = {}

stl_folder = os.path.join(os.path.abspath(os.path.curdir), "GearsPilot", "static", "GearsPilot", "Gear2")
gear_filenames = [f for f in os.listdir(stl_folder) if os.path.isfile(os.path.join(stl_folder, f))]

for g in gear_filenames:
    if "8R30" not in g:
        continue
    gear = stl.mesh.Mesh.from_file(os.path.join(stl_folder, g))
    volume, cog, inertia = gear.get_mass_properties()
    print(g, cog)


# prepare Files
to_replace = {"@":"",
            "(": "",
             ")":"",
             "_": "-",
             " ": "-",}

for g in gear_filenames:
    new_name = g
    for key in to_replace.keys():
        new_name = new_name.replace(key, to_replace[key])
    os.rename(os.path.join(stl_folder, g), os.path.join(stl_folder, new_name))





# Remove .stl for just filenames
for i in range(len(gear_filenames)):
    gear_filenames[i] = gear_filenames[i].replace(".stl", "")

# write JSON
json_file_folder = os.path.join(os.path.abspath(os.path.curdir),"GearsPilot", "static", "GearsPilot")

with open(os.path.join(json_file_folder, "Gear2-files.json"), "w") as f:
    json.dump(gear_filenames, f)
