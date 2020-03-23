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
    """
    Represents kinds of locations in which segment can be
    in relation to other objects.
    """
    #: have no common points
    EXTERNAL = 0
    #: have at least one point in common, but interiors do not intersect
    TOUCH = 1
    #: have some but not all interior points in common
    CROSS = 2
    #: segment fully lies on the boundary of the object
    BOUNDARY = 3
    #: interior of the segment fully lies in the interior of the object
    #: and at least one of the endpoints lies on the boundary of the object
    ENCLOSED = 4
    #: segment fully lies in the interior of the object
    INTERNAL = 5
