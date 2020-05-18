try:
    #import numpy as np
    # due to import structure, each function needs to be imported individually, rather than the whole module.
    from fakeNumpy import radians, cos, sin, tan, sqrt, pi, array, append, flip, empty, arange, linspace
    #from numpy import radians, cos, sin, tan, sqrt, pi, array, append, flip, empty, arange, linspace
except ImportError:
    from .fakeNumpy import radians, cos, sin, tan, sqrt, pi, array, append, flip, empty, arange, linspace


class Involute():

    '''
     Creating and plotting an involute gear

    Inputs:
        - Pressure angle
        - Module
        - Pitch diameter

     1. Calculate useful parameters for drawing the gear, such as:
        Number of teeth, and angle between each tooth
        Addendum radius (Pitch radius + module)
        Dedendum radius (Pitch radius - 1.25 * module)


     2. Draw a single tooth:
        calculate the first involute profile
        calculate the addendum Arc
        calculate the second (mirrored) involute profile
        calculate the dedendum Arc

    3. create the whole wheel by creating each tooth individually

    '''

    def __init__(self, pressure_angle, pitch_diameter, module):
        self.pressure_angle = pressure_angle
        self.pitch_diameter = pitch_diameter
        self.module = module
        self.calculate_parameters()

    def calculate_parameters(self):
        # calculate derived physical parameters
        self._pitch_radius = self.pitch_diameter / 2
        self._number_of_teeth = int(self._pitch_radius / self.module)
        # redefine module to snap to integer number of teeth
        self.module =  self._pitch_radius / self._number_of_teeth
        self._angle_between_teeth = pi * self.module / self._pitch_radius

        # Calculate addendum and dedendum based on metric gear definition,
        # https://www.sdp-si.com/resources/elements-of-metric-gear-technology/
        self._addendum_radius = self._pitch_radius + self.module
        self._dedendum_radius = self._pitch_radius - 1.25 * self.module
        self._base_radius = self._pitch_radius * sin(pi/2 - radians(self.pressure_angle))
        self._effective_base_radius = max(self._base_radius, self._dedendum_radius) # if dedendum is larger than base circle, use that.
        self._angular_resolution = self._angle_between_teeth / 10

        # Calculate useful parameters for solver
        x, y = self.calculate_involute(self._effective_base_radius, self._pitch_radius)
        self._base_to_pitch_angle = tan(y[-1]/x[-1]) - tan(y[0]/x[0]) # Angle between the involute start (at base circle) to involute/pitch circle intersection

        x, y = self.calculate_involute(self._effective_base_radius, self._addendum_radius)
        self._base_to_addendum_angle = tan(y[-1]/x[-1]) - tan(y[0]/x[0]) # Angle between the involute start (at base circle) to involute/pitch circle intersection

        self._pitch_to_addendum_angle = self._base_to_addendum_angle - self._base_to_pitch_angle

        # calculate start angles for circular arcs, relative to the tooth start angle
        self._addendum_start_angle = self._base_to_addendum_angle
        self._addendum_end_angle = self._addendum_start_angle + self._angle_between_teeth - 2 * self._pitch_to_addendum_angle

        self._dedendum_start_angle = self._angle_between_teeth + 2 * self._base_to_pitch_angle
        self._dedendum_end_angle = self._dedendum_start_angle + self._angle_between_teeth - 2 * self._base_to_pitch_angle


    def calculate_involute(self, start_radius, end_radius, a = 0, inverse = False):
        t_max = sqrt((end_radius / start_radius)**2 - 1) # Formula worked out by hand. It seems to work. Fortunately.
        if not inverse:
            t = linspace(a, a + t_max, 50)
            x_prime = start_radius * (cos(t) + (t-a) * sin(t))
            y_prime = start_radius * (sin(t) - (t-a) * cos(t))
        else:
            a += pi/2 # to correct for mirroring curve
            t = linspace(a, a + t_max, 50)
            x_prime = start_radius * (sin(t) - (t-a) * cos(t))
            y_prime = start_radius * (cos(t) + (t-a) * sin(t))

        return x_prime, y_prime

    def create_points_on_circle(self, radius, start_angle = 0, end_angle = 360, input_radians = False):
        if input_radians:
            t = arange(start_angle, end_angle, self._angular_resolution)
        else:
            t = arange(radians(start_angle), radians(end_angle), self._angular_resolution)
        x = array(radius * cos(t))
        y = array(radius * sin(t))
        return x, y

    def create_involute1(self, start_angle):
        x_coords, y_coords = (self._dedendum_radius * cos(start_angle), self._dedendum_radius * sin(start_angle))
        x_involute1, y_involute1 = self.calculate_involute(self._effective_base_radius, self._addendum_radius, a = start_angle)
        x_coords = append(x_coords, x_involute1)
        y_coords = append(y_coords, y_involute1)
        return x_coords, y_coords

    def create_involute2(self, start_angle):
        inverse_profile_start_angle = -start_angle - (pi * self.module / self._pitch_radius + 2 * self._base_to_pitch_angle)

        x_coords, y_coords = (self._dedendum_radius * cos(start_angle + self._dedendum_start_angle), self._dedendum_radius * sin(start_angle + self._dedendum_start_angle))
        x_involute2, y_involute2 = self.calculate_involute(self._effective_base_radius, self._addendum_radius, a = inverse_profile_start_angle, inverse = True)
        x_coords = append(x_coords, x_involute2)
        y_coords = append(y_coords, y_involute2)
        return x_coords, y_coords


    def create_single_tooth(self, start_angle):
        x_coords, y_coords = (self._dedendum_radius * cos(start_angle), self._dedendum_radius * sin(start_angle))

        x_involute1, y_involute1 = self.calculate_involute(self._effective_base_radius, self._addendum_radius, a = start_angle)
        x_coords = append(x_coords, x_involute1)
        y_coords = append(y_coords, y_involute1)

        x_addendum, y_addendum = self.create_points_on_circle(self._addendum_radius, self._addendum_start_angle + start_angle, self._addendum_end_angle + start_angle, input_radians=True)
        x_coords = append(x_coords, x_addendum)
        y_coords = append(y_coords, y_addendum)

        # calculate angle between beginning of tooth profiles - distance between teeth at pitch, plus 2 * distance between pitch and base.
        inverse_profile_start_angle = -start_angle - (pi * self.module / self._pitch_radius + 2 * self._base_to_pitch_angle)
        x_involute2, y_involute2 = self.calculate_involute(self._effective_base_radius, self._addendum_radius, a = inverse_profile_start_angle, inverse = True)

        x_coords = append(x_coords, flip(x_involute2, 0))
        y_coords = append(y_coords, flip(y_involute2, 0))

        x_dedendum, y_dedendum = self.create_points_on_circle(self._dedendum_radius, self._dedendum_start_angle + start_angle,  self._dedendum_end_angle + start_angle, input_radians = True)
        x_coords = append(x_coords, x_dedendum)
        y_coords = append(y_coords, y_dedendum)

        return x_coords, y_coords

    def create_wheel(self, start_angle = 0):
        x_coords = empty(0)
        y_coords = empty(0)
        start_angles = linspace(start_angle, start_angle + 2*pi, self._number_of_teeth)
        for a in start_angles:
            x,y = self.create_single_tooth(a)
            x_coords = append(x_coords, x)
            y_coords = append(y_coords, y)
        return x_coords, y_coords
