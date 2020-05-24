
import math

from pdb import set_trace

def allow_arrays(func):
    def wrapper(*args):
        if len(args) == 1 and isinstance(*args, array):
            arr = args[0]
            return array([func(arr[i]) for i in range(len(arr))])
        elif len(args) == 1:
            return func(*args)
        else:
            raise(NotImplemented)
    return wrapper

def allow_array_interaction(func):
    def wrapper(*args):
        if isinstance(args[1], array):
            if len(args[0]) != len(args[1]):
                raise(NotImplemented)
            return array([func(args[0][i], args[1][i]) for i in range(len(args[0]))])
        else:
            if isinstance(args[0], array):
                return array([func(args[0][i], args[1]) for i in range(len(args[0]))])
            else:
                return array([func(args[0], args[1][i]) for i in range(len(args[1]))])
    return wrapper

@allow_arrays
def radians(angle):
    return math.radians(angle)

@allow_arrays
def cos(angle):
    if not isinstance(angle, float) and len(angle) > 1:
        pass
    return math.cos(angle)

@allow_arrays
def sin(angle):
    return math.sin(angle)

@allow_arrays
def tan(angle):
    return math.tan(angle)

@allow_arrays
def sqrt(val):
    return math.sqrt(val)

pi = math.pi # needed to provide fakeNumpy version of pi


class array(list):
    @allow_array_interaction
    def __mul__(self, other):
        return float.__mul__(self, other)

    @allow_array_interaction
    def __rmul__(self, other):
        return float.__rmul__(self, other)

    @allow_array_interaction
    def __add__(self, other):
        return float.__add__(self, other)

    @allow_array_interaction
    def __sub__(self, other):
        return float.__sub__(self, other)


def append(arr1, arr2):
    if not isinstance(arr1, array):
        arr1 = array([arr1])
    if not isinstance(arr2, array):
        arr2 = array([arr2])
    return array(list.__add__(arr1, arr2))

def flip(arr, axis):
    return array(arr[-1:0:-1])

def empty(size):
    return array()

def arange(start, end, increment):
    range_length = int(math.floor((end-start) / increment))
    arr = array((start + i*increment for i in range(range_length)))
    if start + (range_length * increment) < end:
        # Add end point if
        arr = append(arr, end)
    elif start + (range_length * increment) > end:
        arr = arr[0:-2]
        arr = append(arr, end)
    return arr

def linspace(start, end, number_items):
    increment = (end - start)/number_items
    return array((start + i*increment for i in range(number_items)))
