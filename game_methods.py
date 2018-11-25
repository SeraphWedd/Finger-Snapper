import pygame as pg
import math
from math import sqrt

def crop_image(image, image_rect, crop_rect):
    '''Receives a surface, it's rect, and the rect of image to be cropped.
Returns a surface.'''
    ix, iy, iw, ih = image_rect
    cx, cy, cw, ch = crop_rect
    #Trim from topleft of image to topleft of crop_rect
    temp = pg.transform.chop(image, (0, 0, cx, cy))
    #Trim from bottomright of crop_rect to bottomright of image (temp)
    return pg.transform.chop(temp, (cw, ch, iw-cx-cw, ih-cy-ch))

def make_text_object(text, font, color):
    '''Creates a surf and rect from a text.'''
    surf = font.render(text, True, color)
    return surf, surf.get_rect()

def int_to_str(n):
    '''Converts long integer into a comma separated string.'''
    neg = (n < 0)
    num = str(abs(n))
    if len(num) < 4:
        return str(n)
    else:
        i = len(num)-3
        while i > 0:
            num = num[:i] + ',' + num[i:]
            i -= 3
        if neg:
            return '-' + num
        else:
            return num

def color_mixer(color1, colors):
    '''Mixes color1 with all color passed by colors.'''
    r1, g1, b1 = color1
    
    for color in colors:
        if hasattr(color, '__getitem__'):
            r2, g2, b2 = color
            r1 += r2
            g1 += g2
            b1 += b2
            r1, g1, b1 = [int(x) for x in [r1/2, g1/2, b1/2]]
        else:
            r2, g2, b2 = colors
            r1 += r2
            g1 += g2
            b1 += b2
            r1, g1, b1 = [int(x) for x in [r1/2, g1/2, b1/2]]
            return (r1, g1, b1)
    return (r1, g1, b1)

def get_angle(p1, p2):
    '''p1 is origin and p2 is the target dest.'''
    x1, y1 = p1
    x2, y2 = p2
    if x2 == x1: #Undefined slope
        if y2 > y1: return -90
        else: return 90
    elif y2 == y1: #0 slope
        if x2 > x1: return 0
        else: return 180
    slope = (y2-y1)/(x2-x1)
    angle = math.atan(slope) * 180/math.pi
    if (y2 - y1) > 0 and (x2 - x1) > 0:
        return angle
    elif (y2 - y1) > 0 and (x2 - x1) < 0:
        return 180 + angle
    elif (y2 - y1) < 0 and (x2 - x1) < 0:
        return angle - 180
    elif (y2 - y1) < 0 and (x2 - x1) > 0:
        return angle


####################################################################
### Function/Class from the gameobjects module modified for python3
####################################################################

def format_number(n, accuracy=6):
    """Formats a number in a friendly manner
    (removes trailing zeros and unneccesary point."""

    fs = "%."+str(accuracy)+"f"
    str_n = fs%float(n)
    if '.' in str_n:
        str_n = str_n.rstrip('0').rstrip('.')
    if str_n == "-0":
        str_n = "0"
    return str_n


class Vector2(object):

    __slots__ = ('_v',)

    _gameobjects_vector = 2


    def __init__(self, x=0., y=0.):
        """Initialise a vector

        @type x: number
        @param x: The x value (defaults to 0.), or a container of 2 values
        @type x: number
        @param y: The y value (defaults to 0.)

        """
        if hasattr(x, "__getitem__"):
            x, y = x
            self._v = [float(x), float(y)]
        else:
            self._v = [float(x), float(y)]

    def _get_length(self):
        x, y = self._v
        return sqrt(x*x + y*y)
    def _set_length(self, length):
        v = self._v
        try:
            x, y = v
            l = length / sqrt(x*x +y*y)
        except ZeroDivisionError:
            v[0] = 0.0
            v[1] = 0.0
            return self
        v[0] *= l
        v[1] *= l
    length = property(_get_length, _set_length, None, "Length of the vector")


    @classmethod
    def from_floats(cls, x, y):
        vec = cls.__new__(cls, object)
        vec._v = [x, y]
        return vec


    @classmethod
    def from_iter(cls, iterable):
        """Creates a Vector2 object from an iterable.

        @param iterable: An iterable of at least 2 numeric values

        """
        next = iter(iterable).next
        vec = cls.__new__(cls, object)
        vec._v = [float(next()), float(next())]
        return vec


    @classmethod
    def from_points(cls, p1, p2):
        """Creates a Vector2 object between two points.
        @param p1: First point
        @param p2: Second point

        """
        v = cls.__new__(cls, object)
        x, y = p1
        xx, yy = p2
        v._v = [float(xx-x), float(yy-y)]
        return v

    @classmethod
    def _from_float_sequence(cls, sequence):
        v = cls.__new__(cls, object)
        v._v = list(sequence[:2])
        return v

    def copy(self):
        """Returns a copy of this object."""
        vec = self.__new__(self.__class__, object)
        vec._v = self._v[:]
        return vec

    def get_x(self):
        return self._v[0]
    def set_x(self, x):
        try:
            self._v[0] = 1.0 * x
        except:
            raise TypeError("Must be a number")
    x = property(get_x, set_x, None, "x component.")

    def get_y(self):
        return self._v[1]
    def set_y(self, y):
        try:
            self._v[1] = 1.0 * y
        except:
            raise TypeError("Must be a number")
    y = property(get_y, set_y, None, "y component.")

    def __str__(self):

        x, y = self._v
        return "(%s, %s)" % (format_number(x), format_number(y))

    def __repr__(self):

        x, y = self._v
        return "Vector2(%s, %s)" % (x, y)

    def __iter__(self):

        return iter(self._v[:])

    def __len__(self):

        return 2

    def __getitem__(self, index):
        """Gets a component as though the vector were a list."""
        try:
            return self._v[index]
        except IndexError:
            raise(IndexError, "There are 2 values in this object, \
index should be 0 or 1")

    def __setitem__(self, index, value):
        """Sets a component as though the vector were a list."""

        try:
            self._v[index] = 1.0 * value
        except IndexError:
            raise(IndexError, "There are 2 values in this object, \
index should be 0 or 1!")
        except TypeError:
            raise(TypeError, "Must be a number")


    def __eq__(self, rhs):
        x, y = self._v
        xx, yy = rhs
        return x == xx and y == yy

    def __ne__(self, rhs):
        x, y = self._v
        xx, yy, = rhs
        return x != xx or y != yy

    def __hash__(self):

        return hash(self._v)

    def __add__(self, rhs):
        x, y = self._v
        xx, yy = rhs
        return Vector2.from_floats(x+xx, y+yy)


    def __iadd__(self, rhs):
        xx, yy = rhs
        v = self._v
        v[0] += xx
        v[1] += yy
        return self

    def __radd__(self, lhs):
        x, y = self._v
        xx, yy = lhs
        return self.from_floats(x+xx, y+yy)

    def __sub__(self, rhs):
        x, y = self._v
        xx, yy = rhs
        return Vector2.from_floats(x-xx, y-yy)

    def __rsub__(self, lhs):
        x, y = self._v
        xx, yy = lhs
        return self.from_floats(xx-x, yy-y)

    def _isub__(self, rhs):

        xx, yy = rhs
        v = self._v
        v[0] -= xx
        v[1] -= yy
        return self


    def __mul__(self, rhs):
        """Return the result of multiplying this vector with a scalar or a vector-list object."""
        x, y = self._v
        if hasattr(rhs, "__getitem__"):
            xx, yy = rhs
            return Vector2.from_floats(x*xx, y*yy)
        else:
            return Vector2.from_floats(x*rhs, y*rhs)


    def __imul__(self, rhs):
        """Multiplys this vector with a scalar or a vector-list object."""
        if hasattr(rhs, "__getitem__"):
            xx, yy = rhs
            v = self._v
            v[0] *= xx
            v[1] *= yy
        else:
            v = self._v
            v[0] *= rhs
            v[1] *= rhs
        return self

    def __rmul__(self, lhs):

        x, y = self._v
        if hasattr(lhs, "__getitem__"):
            xx, yy = lhs
        else:
            xx = lhs
            yy = lhs
        return self.from_floats(x*xx, y*yy)


    def __div__(self, rhs):
        """Return the result of dividing this vector by a scalar or a \
vector-list object."""
        x, y = self._v
        if hasattr(rhs, "__getitem__"):
            xx, yy, = rhs
            return Vector2.from_floats(x/xx, y/yy)
        else:
            return Vector2.from_floats(x/rhs, y/rhs)


    def __idiv__(self, rhs):
        """Divides this vector with a scalar or a vector-list object."""
        if hasattr(rhs, "__getitem__"):
            xx, yy = rhs
            v = self._v
            v[0] /= xx
            v[1] /= yy
        else:
            v = self._v
            v[0] /= rhs
            v[1] /= rhs
        return self

    def __rdiv__(self, lhs):

        x, y = self._v
        if hasattr(lhs, "__getitem__"):
            xx, yy = lhs
        else:
            xx = lhs
            yy = lhs
        return self.from_floats(xx/x, yy/x)

    def __neg__(self):
        """Return the negation of this vector."""
        x, y = self._v
        return Vector2.from_floats(-x, -y)

    def __pos__(self):

        return self.copy()

    def __nonzero__(self):

        x, y = self._v
        return bool(x or y)

    def __call__(self, keys):

        """Used to swizzle a vector.

        @type keys: string
        @param keys: A string containing a list of component names
        >>> vec = Vector(1, 2)
        >>> vec('yx')
        (1, 2)

        """

        ord_x = ord('x')
        v = self._v
        return tuple( v[ord(c) - ord_x] for c in keys )


    def as_tuple(self):
        """Converts this vector to a tuple.

        @rtype: Tuple
        @return: Tuple containing the vector components
        """
        return tuple(self._v)


    def get_length(self):
        """Returns the length of this vector."""
        x, y = self._v
        return sqrt(x*x + y*y)
    get_magnitude = get_length


    def normalise(self):
        """Normalises this vector."""
        v = self._v
        x, y = v
        l = sqrt(x*x +y*y)
        try:
            v[0] /= l
            v[1] /= l
        except ZeroDivisionError:
            v[0] = 0.
            v[1] = 0.
        return self
    normalize = normalise

    def get_normalised(self):
        x, y = self._v
        l = sqrt(x*x +y*y)
        try:
            return Vector2.from_floats(x/l, y/l)
        except ZeroDivisionError:
            return Vector2.from_floats(x, y)
    get_normalized = get_normalised

    def get_distance_to(self, p):
        """Returns the distance to a point.

        @param: A Vector2 or list-like object with at least 2 values.
        @return: distance
        """
        x, y = self._v
        xx, yy = p
        dx = xx-x
        dy = yy-y
        return sqrt( dx*dx + dy*dy )
    
if __name__ == "__main__":
    pass
