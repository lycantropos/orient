from enum import (IntEnum,
                  unique)


@unique
class PointLocation(IntEnum):
    """
    Represents kinds of locations in which point can be
    in relation to other objects.
    """
    #: point lies in the exterior of the object
    EXTERNAL = 0
    #: point lies on the boundary of the object
    BOUNDARY = 1
    #: point lies in the interior of the object
    INTERNAL = 2


@unique
class SegmentLocation(IntEnum):
    EXTERNAL = 0
    TOUCH = 1
    CROSS = 2
    BOUNDARY = 3
    ENCLOSED = 4
    INTERNAL = 5
