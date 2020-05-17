
from math import pi
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from involute import Involute

class GearsPlotter():
    def __init__(self, pressure_angle, pitch_diameter, module):
        self._pressure_angle = pressure_angle
        self._pitch_diameter = pitch_diameter
        self._module = module
        self.I = Involute(pressure_angle, pitch_diameter, 0.11)
        self.fig = plt.figure(figsize = [8,8])
        self.ax = ax = plt.axes([0.05, 0.05 + 0.1, 0.9, 0.8])
        self.plot_func = self.plot_wheels_and_circles
        self.ax.axis("equal")
        self.ax.grid("on")

    @property
    def pressure_angle(self):
        return self._pressure_angle

    @pressure_angle.setter
    def pressure_angle(self, value):
        self._pressure_angle = value
        self.re_plot()

    @property
    def pitch_diameter(self):
        return self._pitch_diameter

    @pitch_diameter.setter
    def pitch_diameter(self, value):
        self.pitch_diameter = value
        self.re_plot()

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, value):
        self._module = value
        self.re_plot()

    def re_plot(self):
        self.I = Involute(self.pressure_angle, self.pitch_diameter, self.module)
        self.plot_func()

    def plot_wheel(self):
        self.ax.lines = []
        x, y = self.I.create_wheel()
        self.ax.plot(x,y, 'kx--')
        self.plot_circle(self.I._pitch_radius, 'r--')
        self.plot_circle(self.I._base_radius, 'r--')

    def plot_single_tooth(self, angle):
        self.ax.lines = []
        x, y = I.create_single_tooth(angle)
        self.ax.plot(x,y)
        plot_circle(self.I._pitch_radius, 'r--')
        plot_circle(self.I._base_radius, 'r--')

    def plot_circle(self, radius, *args, **kwargs):
        x,y = self.I.create_points_on_circle(radius)
        self.ax.plot(x, y, *args, **kwargs)

    def plot_wheels_and_circles(self):
        self.ax.lines = []
        x, y = self.I.create_wheel()
        self.ax.plot(x + self.I._pitch_radius, y, 'k')
        x, y = self.I.create_points_on_circle(self.I._pitch_radius)
        self.ax.plot(x + self.I._pitch_radius, y, 'r--')
        x, y = self.I.create_points_on_circle(self.I._base_radius)
        self.ax.plot(x + self.I._pitch_radius, y, 'r--')

        x, y = self.I.create_wheel()
        self.ax.plot(x - self.I._pitch_radius, y, 'k')
        x, y = self.I.create_points_on_circle(self.I._pitch_radius)
        self.ax.plot(x - self.I._pitch_radius, y, 'r--')
        x, y = self.I.create_points_on_circle(self.I._base_radius)
        self.ax.plot(x - self.I._pitch_radius, y, 'r--')



# create sliders
props = {   "pressure_angle":{"initial": 20, "max":60, "min":1},
            "pitch_diameter":{"initial": 10, "max":100, "min":0.1},
            "module": {"initial": 0.1, "max":1, "min":0.001},
        }

GP = GearsPlotter(props["pressure_angle"]["initial"], props["pitch_diameter"]["initial"], props["module"]["initial"])
GP.plot_wheels_and_circles()

slider_width = 0.7
slider_height = 0.025
sliders = []
slider_axs = []

for index, value in enumerate(props.keys()):
    axs = plt.axes([0.15, 0.05 + index*slider_height, slider_width, slider_height])
    S = Slider(axs, value, props[value]["min"], props[value]["max"], valinit = props[value]["initial"])
    S.on_changed(lambda m: type(GP).__dict__[value].__set__(GP, m))
    slider_axs.append(axs)
    sliders.append(S)

plt.show()
