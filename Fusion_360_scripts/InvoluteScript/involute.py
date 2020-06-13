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
        self.points_per_involute = 10

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

    def sanitise_start_angle(self, start_angle, narrow_range_sanitise = False):
        start_angle %= 2 * pi
        if start_angle < 0:
            start_angle += 2 * pi
        involute_start_angle = start_angle - self._base_to_pitch_angle

        # constrain value to be within +90 degree quadrant
        if narrow_range_sanitise:
            loopcounter = 0
            while involute_start_angle < 0 or involute_start_angle > (pi / 2 - self._angle_between_teeth):
                if involute_start_angle < 0:
                    involute_start_angle += self._angle_between_teeth
                else:
                    involute_start_angle -= self._angle_between_teeth
                loopcounter += 1
                if loopcounter > 100:
                    print("infinite loop when rotating gears")
                    break
            start_angle = involute_start_angle + self._base_to_pitch_angle

        return start_angle

    def calculate_involute(self, start_radius, end_radius, a = 0, inverse = False):
        t_max = sqrt((end_radius / start_radius)**2 - 1) # Formula worked out by hand. It seems to work. Fortunately.
        if not inverse:
            t = linspace(a, a + t_max, self.points_per_involute)
            x_prime = start_radius * (cos(t) + (t-a) * sin(t))
            y_prime = start_radius * (sin(t) - (t-a) * cos(t))
        else:
            a += pi/2 # to correct for mirroring curve
            t = linspace(a, a + t_max, self.points_per_involute)
            x_prime = start_radius * (sin(t) - (t-a) * cos(t))
            y_prime = start_radius * (cos(t) + (t-a) * sin(t))

        return x_prime, y_prime

    def create_points_on_circle(self, radius, start_angle = 0, end_angle = 360, input_radians = False):
        start_angle = self.sanitise_start_angle(start_angle)
        if input_radians:
            t = arange(start_angle, end_angle, self._angular_resolution)
        else:
            t = arange(radians(start_angle), radians(end_angle), self._angular_resolution)
        x = array(radius * cos(t))
        y = array(radius * sin(t))
        return x, y

    def create_involute1(self, start_angle):
        #start_angle = self.sanitise_start_angle(start_angle, True)
        start_angle = start_angle - self._base_to_pitch_angle # involute is drawn from base circle, but top level meshing is determined at pitch circle
        x_coords, y_coords = (self._dedendum_radius * cos(start_angle), self._dedendum_radius * sin(start_angle))
        x_involute1, y_involute1 = self.calculate_involute(self._effective_base_radius, self._addendum_radius, a = start_angle)
        if self._effective_base_radius > self._dedendum_radius:
            x_involute1 = append(x_coords, x_involute1)
            y_involute1 = append(y_coords, y_involute1)
        return x_involute1, y_involute1

    def create_involute2(self, start_angle):
        #start_angle = self.sanitise_start_angle(start_angle, True)
        start_angle = start_angle - self._base_to_pitch_angle # involute is drawn from base circle, but top level meshing is determined at pitch circle
        inverse_profile_start_angle = -start_angle - (pi * self.module / self._pitch_radius + 2 * self._base_to_pitch_angle)

        x_coords, y_coords = (self._dedendum_radius * cos(start_angle + self._dedendum_start_angle), self._dedendum_radius * sin(start_angle + self._dedendum_start_angle))
        x_involute2, y_involute2 = self.calculate_involute(self._effective_base_radius, self._addendum_radius, a = inverse_profile_start_angle, inverse = True)
        if self._effective_base_radius > self._dedendum_radius:
            x_involute2 = append(x_coords, x_involute2)
            y_involute2 = append(y_coords, y_involute2)
        return x_involute2, y_involute2


    def create_single_tooth(self, start_angle):
        #start_angle = self.sanitise_start_angle(start_angle)
        start_angle = start_angle - self._base_to_pitch_angle # involute is drawn from base circle, but top level meshing is determined at pitch circle
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

    def rotate_coords(self, x, y, angle):
        x_coords = x * cos(angle) - y * sin(angle)
        y_coords = x * sin(angle) + y * cos(angle)
        return x_coords, y_coords

    def create_wheel(self, start_angle = 0):
        start_angle = self.sanitise_start_angle(start_angle, False)
        x_coords = empty(0)
        y_coords = empty(0)
        start_angles = linspace(start_angle, start_angle + 2*pi, self._number_of_teeth)
        x_coords_tooth, y_coords_tooth = self.create_single_tooth(start_angles[0])
        #x_coords = append(x_coords, x_coords_tooth)
        #y_coords = append(y_coords, y_coords_tooth)
        for a in start_angles:
            #x,y = self.create_single_tooth(a)
            x, y = self.rotate_coords(x_coords_tooth, y_coords_tooth, a)
            x_coords = append(x_coords, x)
            y_coords = append(y_coords, y)
        return x_coords, y_coords
