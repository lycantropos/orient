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
            or (bounding_box
                .contains_point(bounding_box.from_iterable(segment), point)
                and orientation(end, start, point) is Orientation.COLLINEAR))
        else Relation.DISJOINT)


def relate_segment(goal: Segment, test: Segment) -> Relation:
    if goal == test or goal == test[::-1]:
        return Relation.EQUAL
    goal_start, goal_end = goal
    test_start, test_end = test
    if goal_start > goal_end:
        goal_start, goal_end = goal_end, goal_start
    if test_start > test_end:
        test_start, test_end = test_end, test_start
    goal_start_orientation = orientation(test_start, test_end, goal_start)
    goal_end_orientation = orientation(test_start, test_end, goal_end)
    if goal_start_orientation is goal_end_orientation:
        if goal_start_orientation is Orientation.COLLINEAR:
            if goal_start == test_start:
                return (Relation.COMPOSITE
                        if goal_end < test_end
                        else Relation.COMPONENT)
            elif goal_end == test_end:
                return (Relation.COMPOSITE
                        if test_start < goal_start
                        else Relation.COMPONENT)
            elif goal_start == test_end or goal_end == test_start:
                return Relation.TOUCH
            elif test_start < goal_start < test_end:
                return (Relation.COMPOSITE
                        if goal_end < test_end
                        else Relation.OVERLAP)
            elif goal_start < test_start < goal_end:
                return (Relation.COMPONENT
                        if test_end < goal_end
                        else Relation.OVERLAP)
            else:
                return Relation.DISJOINT
        else:
            return Relation.DISJOINT
    elif goal_start_orientation is Orientation.COLLINEAR:
        return (Relation.TOUCH
                if test_start <= goal_start <= test_end
                else Relation.DISJOINT)
    elif goal_end_orientation is Orientation.COLLINEAR:
        return (Relation.TOUCH
                if test_start <= goal_end <= test_end
                else Relation.DISJOINT)
    else:
        test_start_orientation = orientation(goal_end, goal_start, test_start)
        test_end_orientation = orientation(goal_end, goal_start, test_end)
        if test_start_orientation is test_end_orientation:
            return Relation.DISJOINT
        elif test_start_orientation is Orientation.COLLINEAR:
            return (Relation.TOUCH
                    if goal_start < test_start < goal_end
                    else Relation.DISJOINT)
        elif test_end_orientation is Orientation.COLLINEAR:
            return (Relation.TOUCH
                    if goal_start < test_end < goal_end
                    else Relation.DISJOINT)
        else:
            return Relation.CROSS
