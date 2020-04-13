from typing import Iterable

from robust.angular import (Orientation,
                            orientation as angle_orientation)

from orient.hints import (Contour,
                          Point,
                          Segment)
from . import bounding_box
from .events_queue import EventsQueue
from .processing import process_linear_queue
from .relation import Relation
from .segment import (relate_point as relate_point_to_segment,
                      relate_segment as relate_segments)


def relate_point(contour: Contour, point: Point) -> Relation:
    if not bounding_box.contains_point(bounding_box.from_points(contour),
                                       point):
        return Relation.DISJOINT
    return (Relation.DISJOINT
            if all(relate_point_to_segment(edge, point) is Relation.DISJOINT
                   for edge in edges(contour))
            else Relation.COMPONENT)


def relate_segment(contour: Contour, segment: Segment) -> Relation:
    return (Relation.DISJOINT
            if bounding_box.disjoint_with(bounding_box.from_points(contour),
                                          bounding_box.from_points(segment))
            else _relate_segment(contour, segment))


def _relate_segment(contour: Contour, segment: Segment) -> Relation:
    has_touch = has_cross = False
    previous_touch_index = previous_touch_edge_start = None
    start, end = segment
    for index, edge in enumerate(edges(contour)):
        relation_with_edge = relate_segments(edge, segment)
        if (relation_with_edge is Relation.COMPONENT
                or relation_with_edge is Relation.EQUAL):
            return Relation.COMPONENT
        elif (relation_with_edge is Relation.OVERLAP
              or relation_with_edge is Relation.COMPOSITE):
            return Relation.OVERLAP
        elif relation_with_edge is Relation.TOUCH:
            edge_start, edge_end = edge
            if has_touch:
                if (not has_cross
                        and index - previous_touch_index == 1
                        and start not in edge and end not in edge
                        and (angle_orientation(end, start, edge_start)
                             is Orientation.COLLINEAR)
                        and _point_vertex_line_divides_angle(
                                start, previous_touch_edge_start,
                                edge_start, edge_end)):
                    has_cross = True
            else:
                has_touch = True
            previous_touch_index, previous_touch_edge_start = index, edge_start
        elif not has_cross and relation_with_edge is Relation.CROSS:
            has_cross = True
    if (not has_cross
            and has_touch
            and previous_touch_index == len(contour) - 1):
        first_edge = first_edge_start, first_edge_end = contour[-1], contour[0]
        if (relate_segments(first_edge, segment) is Relation.TOUCH
                and start not in first_edge and end not in first_edge
                and (angle_orientation(end, start, first_edge_start)
                     is Orientation.COLLINEAR)
                and _point_vertex_line_divides_angle(start, contour[-2],
                                                     first_edge_start,
                                                     first_edge_end)):
            has_cross = True
    return (Relation.CROSS
            if has_cross
            else (Relation.TOUCH
                  if has_touch
                  else Relation.DISJOINT))


def _point_vertex_line_divides_angle(point: Point,
                                     first_ray_point: Point,
                                     vertex: Point,
                                     second_ray_point: Point) -> bool:
    return (angle_orientation(first_ray_point, vertex, point)
            is angle_orientation(point, vertex, second_ray_point))


def orientation(contour: Contour) -> Orientation:
    index = min(range(len(contour)),
                key=contour.__getitem__)
    return angle_orientation(contour[index], contour[index - 1],
                             contour[(index + 1) % len(contour)])


def relate_contour(goal: Contour, test: Contour) -> Relation:
    test_bounding_box = bounding_box.from_points(test)
    if bounding_box.disjoint_with(bounding_box.from_points(goal),
                                  test_bounding_box):
        return Relation.DISJOINT
    if equal(goal, test):
        return Relation.EQUAL
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test=False)
    register(events_queue, test,
             from_test=True)
    _, test_max_x, _, _ = test_bounding_box
    return process_linear_queue(events_queue, test_max_x)


def equal(left: Contour, right: Contour) -> bool:
    if len(left) != len(right):
        return False
    if orientation(left) is not orientation(right):
        right = right[:1] + right[:0:-1]
    size = len(left)
    start = 0
    while start < size:
        try:
            index = right.index(left[0], start)
        except ValueError:
            return False
        else:
            left_index = 0
            for left_index, right_index in zip(range(size),
                                               range(index, size)):
                if left[left_index] != right[right_index]:
                    break
            else:
                for left_index, right_index in zip(range(left_index + 1, size),
                                                   range(index)):
                    if left[left_index] != right[right_index]:
                        break
                else:
                    return True
            start = index + 1


def register(events_queue: EventsQueue, contour: Contour,
             *,
             from_test: bool) -> None:
    for edge in edges(contour):
        events_queue.register_segment(edge,
                                      from_test=from_test)


def edges(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))
