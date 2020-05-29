
import os
from shutil import copyfile
import subprocess


pth = r"C:\Users\rishi\Google Drive\Simulation blog\Blender_Scripts"
file = os.listdir(pth)[0];
dst = r"D:\Blender_Tests"
copyfile(os.path.join(pth, file), os.path.join(dst, file))

print(os.path.join(dst, file))

subprocess.run(r"D:\Program Files\blender --python " + os.path.join(dst, file))
