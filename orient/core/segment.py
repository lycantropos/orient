from ground.base import (Context,
                         Location, 
                         Relation)
from ground.hints import (Point,
                          Segment)


def locate_point(segment: Segment,
                 point: Point,
                 context: Context) -> Location:
    return (Location.BOUNDARY
            if context.segment_contains_point(segment, point)
            else Location.EXTERIOR)


def relate_segment(goal: Segment,
                   test: Segment,
                   context: Context) -> Relation:
    return context.segments_relation(test, goal)
