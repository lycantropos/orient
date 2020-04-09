from robust.angular import (Orientation,
                            orientation)

from orient.hints import (Point,
                          Segment)
from . import bounding_box
from .relation import Relation


def relate_point(segment: Segment, point: Point) -> Relation:
    start, end = segment
    return (
        Relation.COMPONENT
        if (point == start or point == end
            or (bounding_box.contains_point(bounding_box.from_points(segment),
                                            point)
                and orientation(end, start, point) is Orientation.COLLINEAR))
        else Relation.DISJOINT)
