from ground.base import (Context,
                         Relation)
from ground.hints import (Point,
                          Segment)


def relate_point(segment: Segment,
                 point: Point,
                 *,
                 context: Context) -> Relation:
    return _relate_point(segment.start, segment.end, point,
                         context=context)


def _relate_point(start: Point,
                  end: Point,
                  point: Point,
                  *,
                  context: Context) -> Relation:
    return (Relation.COMPONENT
            if context.segment_contains_point(start, end, point)
            else Relation.DISJOINT)


def relate_segment(goal: Segment,
                   test: Segment,
                   *,
                   context: Context) -> Relation:
    return _relate_segment(goal.start, goal.end, test.start, test.end,
                           context=context)


def _relate_segment(goal_start: Point,
                    goal_end: Point,
                    test_start: Point,
                    test_end: Point,
                    *,
                    context: Context) -> Relation:
    return context.segments_relation(test_start, test_end, goal_start,
                                     goal_end)
