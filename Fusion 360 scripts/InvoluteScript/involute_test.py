
from math import pi
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from involute import Involute


pressure_angle = 20
pitch_diameter = 20
module = 0.1

slider_height = 0.05
sliders = []

fig = plt.figure(figsize = [8,8])
ax = plt.axes([0.05, 0.05 + 0.1, 0.9, 0.8])
ax.axis("equal")
ax.grid("on")

I = Involute(pressure_angle, pitch_diameter, 0.11)

def plot_wheel(module):
    ax.lines = []
    global pressure_angle, pitch_diameter, module
    I = Involute(pressure_angle, pitch_diameter, module)
    x, y = I.create_single_tooth(pi/4)
    x, y = I.create_wheel()
    ax.plot(x,y, 'kx--')
    plot_circle(I._pitch_radius, 'r--')
    plot_circle(I._base_radius, 'r--')

def plot_single_tooth(angle):
    ax.lines = []
    x, y = I.create_single_tooth(angle)
    ax.plot(x,y)
    plot_circle(I._pitch_radius, 'r--')
    plot_circle(I._base_radius, 'r--')

def plot_circle(radius, *args, **kwargs):
    global ax
    x,y = I.create_points_on_circle(radius)
    ax.plot(x, y, *args, **kwargs)

def plot_wheels_and_circles(module):
    global pressure_angle, pitch_diameter, module
    ax.lines = []
    I = Involute(pressure_angle, pitch_diameter, module)
    x, y = I.create_wheel()
    ax.plot(x + I._pitch_radius, y, 'k')
    x, y = I.create_points_on_circle(I._pitch_radius)
    ax.plot(x + I._pitch_radius, y, 'r--')
    x, y = I.create_points_on_circle(I._base_radius)
    ax.plot(x + I._pitch_radius, y, 'r--')

    I = Involute(pressure_angle, pitch_diameter, module)
    x, y = I.create_wheel()
    ax.plot(x - I._pitch_radius, y, 'k')
    x, y = I.create_points_on_circle(I._pitch_radius)
    ax.plot(x - I._pitch_radius, y, 'r--')
    x, y = I.create_points_on_circle(I._base_radius)
    ax.plot(x - I._pitch_radius, y, 'r--')


plot_wheels_and_circles(initial_module_value)

ax2 = plt.axes([0.15, 0.05, 0.7, 0.05])
S = Slider(ax2, "Module", 0.0, 1, valinit = initial_module_value)
S.on_changed(plot_wheels_and_circles)


plt.show()
