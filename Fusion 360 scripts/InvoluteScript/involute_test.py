
from math import pi
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from involute import Involute

class GearsPlotter():
    def __init__(self, pressure_angle, pitch_diameter, module, second_wheel_start = 0):
        self._pressure_angle = pressure_angle
        self._pitch_diameter = pitch_diameter
        self._module = module
        self._second_wheel_start = second_wheel_start
        self.I = Involute(pressure_angle, pitch_diameter, module)
        self.fig = plt.figure(figsize = [8,8])
        self.ax = plt.axes([0.05, 0.05 + 0.1, 0.9, 0.8])
        self.plot_func = self.plot_wheels_and_circles
        #self.plot_func = self.plot_single_tooth
        self.text = None
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
        self._pitch_diameter = value
        self.re_plot()

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, value):
        self._module = value
        self.re_plot()

    @property
    def second_wheel_start(self):
        return self._second_wheel_start

    @second_wheel_start.setter
    def second_wheel_start(self, value):
        self._second_wheel_start = value
        self.re_plot()

    def re_plot(self):
        self.I = Involute(self.pressure_angle, self.pitch_diameter, self.module)
        self.plot_func()

    def plot_text(self):
        if self.text is None:
            self.text = plt.text(0.8, 0.95, "Number of teeth: " + str(self.I._number_of_teeth), transform = self.ax.transAxes)
        else:
            self.text.set_text("Number of teeth: " + str(self.I._number_of_teeth))

    def plot_wheel(self):
        self.ax.lines = []
        x, y = self.I.create_wheel()
        self.ax.plot(x,y, 'k')
        self.plot_text()
        self.plot_circle(self.I._pitch_radius, 'r--')
        self.plot_circle(self.I._base_radius, 'r--')


    def plot_single_tooth(self, angle = 0):
        self.ax.lines = []
        self.ax.patches = []
        x, y = self.I.create_single_tooth(angle)
        self.ax.plot(x,y)
        self.plot_text()
        self.plot_circle(self.I._pitch_radius, 'r--')
        self.plot_circle(self.I._base_radius, 'r--')

    def plot_circle(self, radius, *args, **kwargs):
        x,y = self.I.create_points_on_circle(radius)
        self.ax.plot(x, y, *args, **kwargs)

    def plot_wheels_and_circles(self):
        self.ax.lines = []
        self.ax.patches = []
        x, y = self.I.create_wheel()
        self.ax.fill(x + self.I._pitch_radius, y, 'k', alpha=0.5, facecolor = "green")
        x, y = self.I.create_points_on_circle(self.I._pitch_radius)
        self.ax.plot(x + self.I._pitch_radius, y, 'r--')
        x, y = self.I.create_points_on_circle(self.I._base_radius)
        self.ax.plot(x + self.I._pitch_radius, y, 'r--')

        second_wheel_start = self.second_wheel_start
        if self.I._number_of_teeth % 2 == 1:
            second_wheel_start += self.I.module * pi
        x, y = self.I.create_wheel(start_angle = second_wheel_start)
        self.ax.fill(x - self.I._pitch_radius, y, 'k', alpha=0.5, facecolor = "blue")
        x, y = self.I.create_points_on_circle(self.I._pitch_radius)
        self.ax.plot(x - self.I._pitch_radius, y, 'r--')
        x, y = self.I.create_points_on_circle(self.I._base_radius)
        self.ax.plot(x - self.I._pitch_radius, y, 'r--')
        self.plot_text()



# create sliders
props = {   "pressure_angle":{"initial": 20, "max":60, "min":1},
            "pitch_diameter":{"initial": 10, "max":100, "min":0.1},
            "module": {"initial": 0.1, "max":1, "min":0.001},
            "second_wheel_start": {"initial": 0, "max":pi/2, "min":0},
        }

GP = GearsPlotter(props["pressure_angle"]["initial"], props["pitch_diameter"]["initial"], props["module"]["initial"])
GP.plot_wheels_and_circles()

# Add functions outside for loop, as lambda will only capture last value in loop (lazy evaluation).
props["pressure_angle"]["func"] = lambda m: GearsPlotter.__dict__["pressure_angle"].__set__(GP, float(m))
props["pitch_diameter"]["func"] = lambda m: GearsPlotter.__dict__["pitch_diameter"].__set__(GP, float(m))
props["module"]["func"] = lambda m: GearsPlotter.__dict__["module"].__set__(GP, float(m))
props["second_wheel_start"]["func"] = lambda m: GearsPlotter.__dict__["second_wheel_start"].__set__(GP, float(m))

slider_width = 0.7
slider_height = 0.025
sliders = []
slider_axs = []

for index, value in enumerate(props.keys()):
    axs = plt.axes([0.15, 0.01 + index*slider_height, slider_width, slider_height])
    sliders.append(Slider(axs, value, props[value]["min"], props[value]["max"], valinit = props[value]["initial"]))
    sliders[-1].on_changed(props[value]["func"])
    slider_axs.append(axs)

plt.show()
