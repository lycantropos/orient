from robust.angular import (Orientation,
                            orientation)

from orient.hints import (Point,
                          Segment)
from . import bounding_box
from .location import PointLocation


def contains_point(segment: Segment, point: Point) -> PointLocation:
    start, end = segment
    return (PointLocation.BOUNDARY if point == start or point == end
            else
            (PointLocation.INTERNAL
             if (bounding_box.contains_point(bounding_box.from_points(segment),
                                             point)
                 and orientation(end, start, point) is Orientation.COLLINEAR)
             else PointLocation.EXTERNAL))
