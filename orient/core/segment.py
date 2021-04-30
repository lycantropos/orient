from ground.base import (Context,
                         Relation)
from ground.hints import (Point,
                          Segment)


def relate_point(segment: Segment,
                 point: Point,
                 context: Context) -> Relation:
    return (Relation.COMPONENT
            if context.segment_contains_point(segment, point)
            else Relation.DISJOINT)


def relate_segment(goal: Segment,
                   test: Segment,
                   context: Context) -> Relation:
    return context.segments_relation(test, goal)
