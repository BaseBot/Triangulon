__author__ = 'tom'
from math import cos, sin, pi, radians, sqrt
import operator


class HoloChassis:
    """
    An assembly of wheels at various positions and angles which can be driven independently to create a holonomic drive
    system. A holonomic system is one where number of degrees of freedom in the system is equal to the number of
    directly controllable degrees of freedom, so for a chassis intended to move in two dimensions the degrees of freedom
    are two axes of translation and one of rotation. For a full holonomic system we therefore need at least three wheels
    defined.
    """

    def __init__(self, wheels):
        """
        Create a new chassis, specifying a set of wheels.
        
        :param wheels:
            A sequence of :class:`triangula.chassis.HoloChassis.OmniWheel` objects defining the wheels for this chassis.
        """
        self.wheels = wheels

    def get_wheel_speeds(self, dx, dy, rotation, x_origin=0, y_origin=0):
        """
        Calculate speeds to drive each wheel in the chassis at to attain the specified rotation / translation 3-vector.

        :param float dx:
            Desired translation along the x-axis specified in millimetres per second.
        :param float dy:
            Desired translation along the y-axis specified in millimetres per second.
        :param float rotation:
            Desired anguar velocity, specified in degrees per second where positive values correspond to clockwise
            rotation of the chassis when viewed from above.
        :param float x_origin:
            Optional, can define the centre of rotation to be something other than 0,0
        :param float y_origin:
            Optional, can define the centre of rotation to be something other than 0,0
        :return:
            A sequence of floats defining the revolutions per second required to obtain the appropriate overall motion.
            The sequence contains one speed for each previously specified wheel, there is no limiting in operation so
            this can potentially return results which are not physically possible, a subsequent processing step may be
            required to detect this condition and either scale all motion back or revisit the motion plan to try to find
            a better target vector.
        """

        def velocity_at(x, y):
            return Vector2(x, y)

    class OmniWheel:
        """
        Defines a single omni-wheel within a chassis assembly. Omni-wheels are wheels formed from rollers, where the
        motion of the roller is perpendicular to the motion of the primary wheel. This is distinct from a mechanum wheel
        where the rollers are at an angle (normally around 40-30 degrees) to the primary wheel. Omni-wheels must be
        positioned on the chassis with non-parallel unit vectors, mechanum wheels can in some cases be positioned with
        all unit vectors parallel.

        A wheel has a location relative to the chassis centre and a vector describing the direction of motion of the
        wheel when driven with a positive angular velocity. The location is specified in millimetres, and the magnitude
        of the wheel vector should be equal to the number of millimetres travelled in a single revolution. This allows
        for different sized wheels to be handled within the same chassis.
        """

        def __init__(self, x, y, angle=None, radius=None, dx=None, dy=None):
            """
            Create a new omni-wheel object, specifying the position and either a direction vector directly or the angle
            in degrees clockwise from the position Y axis along with the radius of the wheel.

            :param float x:
                The x coordinate of the wheel's contact point with the surface, specified relative to the centre of the
                chassis. Units are millimetres.
            :param float y:
                The y coordinate of the wheel's contact point with the surface, specified relative to the centre of the
                chassis. Units are millimetres.
            :param angle:
                The angle, specified in degrees from the positive Y axis where positive values are clockwise from this
                axis when viewed from above, of the direction of travel of the wheel when driven with a positive speed.
                If this value is specified then radius must also be specified and dx,dy left as None.
            :param radius:
                The radius in millimetres of the wheel, measuring from the centre to the contact point with the surface,
                this may be hard to determine for some wheels based on their geometry, particularly for wheels with
                cylindrical rollers, as the radius will vary. For these cases it may be worth directly measuring the
                circumference of the entire assembly and calculating radius rather than measuring directly. This is used
                to determine the magnitude of the direction vector. If this is not None then the angle must also be
                specified, and dx,dy left as None.
            :param dx:
                The x component of a vector defining the translation of the wheel's contact point after a full
                revolution of the wheel. If this is specified then dy must also be specified and both angle and radius
                must be left as None.
            :param dy:
                The y component of a vector defining the translation of the wheel's contact point after a full
                revolution of the wheel. If this is specified then dy must also be specified and both angle and radius
                must be left as None.
            """
            self.x = x
            self.y = y
            if angle is None and radius is None and dx is not None and dy is not None:
                #  Specify wheel based on direct vector """
                self.dx = dx
                self.dy = dy
            elif angle is not None and radius is not None and dx is None and dy is None:
                # Specify based on angle from positive Y axis and radius """
                angle_rads = radians(angle)
                circumference = 2 * pi * radius
                self.dx = sin(angle_rads) * circumference
                self.dy = cos(angle_rads) * circumference
            else:
                raise ValueError('Must specify exactly one of angle and radius or dx,dy vector')


class Vector2:
    """
    Two dimensional vector, used internally in many places. Substantially derived from original project found at
    http://pyeuclid.googlecode.com/svn/trunk/euclid.py
    """

    def __init__(self, x=0, y=0):
        """
        :param float x:
            X component
        :param float y:
            Y component
        """
        self.x = x
        self.y = y

    def __copy__(self):
        return self.__class__(self.x, self.y)

    copy = __copy__

    def __eq__(self, other):
        if isinstance(other, Vector2):
            return self.x == other.x and self.y == other.y
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return self.x == other[0] and self.y == other[1]

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self.x != 0 or self.y != 0

    def __len__(self):
        return 2

    def dot(self, other):
        assert isinstance(other, Vector2)
        return self.x * other.x + self.y * other.y

    def cross(self):
        return Vector2(self.y, -self.x)

    def __abs__(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    magnitude = __abs__

    def magnitude_squared(self):
        return self.x ** 2 + \
               self.y ** 2

    def normalized(self):
        d = self.magnitude()
        if d:
            return Vector2(self.x / d,
                           self.y / d)
        return self.copy()

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return Vector2(self.x + other[0], self.y + other[1])

    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
        else:
            self.x += other[0]
            self.y += other[1]
        return self

    def __getitem__(self, key):
        return (self.x, self.y)[key]

    def __setitem__(self, key, value):
        l = [self.x, self.y]
        l[key] = value
        self.x, self.y = l

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return Vector2(self.x - other[0], self.y - other[1])

    def __rsub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x - self.x, other.y - self.y)
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return Vector2(other.x - self[0], other.y - self[1])

    def __mul__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(self.x * other, self.y * other)

    __rmul__ = __mul__

    def __imul__(self, other):
        assert type(other) in (int, long, float)
        self.x *= other
        self.y *= other
        return self

    def __div__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.div(self.x, other), operator.div(self.y, other))

    def __rdiv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.div(other, self.x), operator.div(other, self.y))

    def __floordiv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.floordiv(self.x, other), operator.floordiv(self.y, other))

    def __rfloordiv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.floordiv(other, self.x), operator.floordiv(other, self.y))

    def __truediv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.truediv(self.x, other), operator.truediv(self.y, other))

    def __rtruediv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.truediv(other, self.x), operator.truediv(other, self.y))

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    __pos__ = __copy__
