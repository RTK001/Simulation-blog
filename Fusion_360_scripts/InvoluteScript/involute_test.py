
from math import pi, atan
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
from involute import Involute

class GearsPlotter():
    def __init__(self, pressure_angle, pitch_diameter, module, second_wheel_start = 0, planet_diameter = None):
        self._pressure_angle = pressure_angle
        self._pitch_diameter = pitch_diameter
        self._module = module
        self._second_wheel_start = second_wheel_start
        self.I = Involute(pressure_angle, pitch_diameter, module)
        self.fig = plt.figure(figsize = [8,8])
        self.ax = plt.axes([0.05, 0.2, 0.9, 0.8])

        if planet_diameter is None:
            self._planet_pitch_diameter = self._pitch_diameter
        else:
            self._planet_pitch_diameter = planet_diameter
        self.planet_I = Involute(pressure_angle, self._planet_pitch_diameter, module)

        self.plot_funcs = [ self.plot_wheels_and_circles,
                            self.plot_single_tooth,
                            self.plot_teeth_from_involutes,
                            self.plot_planetary_gearset,]

        self.plot_funcs_dict =  {str(i).split("GearsPlotter.")[1].split("of ")[0]:i for i in self.plot_funcs}

        self.plot_func = self.plot_funcs[3]

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

    @property
    def planet_pitch_diameter(self):
        return self._planet_pitch_diameter

    @planet_pitch_diameter.setter
    def planet_pitch_diameter(self, value):
        self._planet_pitch_diameter = value
        self.re_plot()

    def set_plot_func(self, val):
        self.plot_func = self.plot_funcs_dict[val]
        self.re_plot()

    def re_plot(self):
        self.I = Involute(self.pressure_angle, self.pitch_diameter, self.module)
        self.planet_I = Involute(self.pressure_angle, self.planet_pitch_diameter, self.module)
        self.plot_func()

    def plot_text(self):
        if self.text is None:
            self.text = plt.text(0.75, 0.95, "Number of teeth: " + str(self.I._number_of_teeth), transform = self.ax.transAxes)
            self.text2 = plt.text(0.75, 0.9, "Number of planet teeth: " + str(self.planet_I._number_of_teeth), transform = self.ax.transAxes)
        else:
            self.text.set_text("Number of teeth: " + str(self.I._number_of_teeth))
            self.text2.set_text("Number of planet teeth: " + str(self.planet_I._number_of_teeth))

    def plot_wheel(self):
        self.ax.lines = []
        self.ax.patches = []
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

    def plot_teeth_from_involutes(self, angle = 0):
        self.ax.lines = []
        self.ax.patches = []
        x,y = self.I.create_involute1(start_angle=angle)
        self.ax.plot(x,y,'k')
        x,y = self.I.create_involute2(start_angle=angle)
        self.ax.plot(x,y,'k')
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
        self.ax.plot(x + self.I._pitch_radius, y, 'k')
        x, y = self.I.create_points_on_circle(self.I._pitch_radius)
        self.ax.plot(x + self.I._pitch_radius, y, 'r--')
        x, y = self.I.create_points_on_circle(self.I._base_radius)
        self.ax.plot(x + self.I._pitch_radius, y, 'r--')

        second_wheel_start = self.second_wheel_start
        if self.I._number_of_teeth % 2 == 1:
            second_wheel_start += pi / self.I._number_of_teeth
        x, y = self.I.create_wheel(start_angle = second_wheel_start)
        self.ax.fill(x - self.I._pitch_radius, y, 'k', alpha=0.5, facecolor = "blue")
        self.ax.plot(x - self.I._pitch_radius, y, 'k')
        x, y = self.I.create_points_on_circle(self.I._pitch_radius)
        self.ax.plot(x - self.I._pitch_radius, y, 'r--')
        x, y = self.I.create_points_on_circle(self.I._base_radius)
        self.ax.plot(x - self.I._pitch_radius, y, 'r--')
        self.plot_text()

    def plot_planetary_gearset(self):
        self.ax.lines = []
        self.ax.patches = []
        locations = [(1,0), (-1,0), (0,1), (0,-1)]

        x, y = self.I.create_wheel()
        self.ax.fill(x, y, 'k', alpha=0.5, facecolor = "green")
        x, y = self.I.create_points_on_circle(self.I._pitch_radius)
        self.ax.plot(x, y, 'r--')
        x, y = self.I.create_points_on_circle(self.I._base_radius)
        self.ax.plot(x, y, 'r--')

        for x_loc, y_loc in locations:
            second_wheel_start = self.second_wheel_start

            if x_loc == 0:
                if y_loc > 0:
                    angle_to_sun = pi/2
                else:
                    angle_to_sun = -pi/2
            else:
                if x_loc > 0:
                    angle_to_sun = atan(y_loc / x_loc)
                else:
                    angle_to_sun = atan(y_loc / x_loc) + pi

            angle_to_rotate = angle_to_sun * (1 + (self.I._number_of_teeth / self.planet_I._number_of_teeth)) + second_wheel_start
            print(angle_to_rotate * 180 / pi)

            x_loc *= (self.pitch_diameter + self.planet_pitch_diameter)/2
            y_loc *= (self.pitch_diameter + self.planet_pitch_diameter)/2
            x, y = self.planet_I.create_wheel(angle_to_rotate + pi)

            self.ax.fill(x + x_loc, y + y_loc, 'k', alpha=0.5, facecolor = "green")
            self.ax.plot(x + x_loc, y + y_loc, 'xk')
            self.plot_text()
        print("")


# create sliders
props = {   "pressure_angle":{"initial": 20, "max":60, "min":1},
            "pitch_diameter":{"initial": 20, "max":100, "min":0.1},
            "module": {"initial": 1, "max":1, "min":0.001},
            "second_wheel_start": {"initial": 0, "max":4 * pi, "min":-4*pi},
            "planet_pitch_diameter":{"initial": 20, "max":100, "min":0.1},
        }

GP = GearsPlotter(props["pressure_angle"]["initial"], props["pitch_diameter"]["initial"], props["module"]["initial"])
GP.plot_planetary_gearset()

# Add functions outside for loop, as lambda will only capture last value in loop (lazy evaluation).
props["pressure_angle"]["func"] = lambda m: GearsPlotter.__dict__["pressure_angle"].__set__(GP, float(m))
props["pitch_diameter"]["func"] = lambda m: GearsPlotter.__dict__["pitch_diameter"].__set__(GP, float(m))
props["module"]["func"] = lambda m: GearsPlotter.__dict__["module"].__set__(GP, float(m))
props["second_wheel_start"]["func"] = lambda m: GearsPlotter.__dict__["second_wheel_start"].__set__(GP, float(m))
props["planet_pitch_diameter"]["func"] = lambda m: GearsPlotter.__dict__["planet_pitch_diameter"].__set__(GP, float(m))

slider_width = 0.5
slider_height = 0.025
buttons_width = 0.2
sliders = []
slider_axs = []

buttonAx = plt.axes([ 0.2 + slider_width, 0.01, buttons_width, slider_height * len(props.keys())])
Buttons = RadioButtons(buttonAx, GP.plot_funcs_dict.keys(), active = 3)
Buttons.on_clicked(GP.set_plot_func)

for index, value in enumerate(props.keys()):
    axs = plt.axes([0.15, 0.01 + index*slider_height, slider_width, slider_height])
    sliders.append(Slider(axs, value, props[value]["min"], props[value]["max"], valinit = props[value]["initial"]))
    sliders[-1].on_changed(props[value]["func"])
    slider_axs.append(axs)

plt.show()
