from itertools import chain
from typing import Iterable

from robust.angular import (Orientation,
                            orientation as angle_orientation)

from orient.hints import (Contour,
                          Multisegment,
                          Point,
                          Segment)
from . import bounding_box
from .processing import (process_closed_linear_queue,
                         process_open_linear_queue)
from .relation import Relation
from .segment import (relate_point as relate_point_to_segment,
                      relate_segment as relate_segments)
from .sweep import (ClosedSweeper,
                    OpenSweeper)


def relate_point(contour: Contour, point: Point) -> Relation:
    return (Relation.DISJOINT
            if all(relate_point_to_segment(edge, point) is Relation.DISJOINT
                   for edge in to_segments(contour))
            else Relation.COMPONENT)


def relate_segment(contour: Contour, segment: Segment) -> Relation:
    has_no_touch = has_no_cross = True
    last_touched_edge_index = last_touched_edge_start = None
    start, end = segment
    for index, edge in enumerate(to_segments(contour)):
        relation_with_edge = relate_segments(edge, segment)
        if (relation_with_edge is Relation.COMPONENT
                or relation_with_edge is Relation.EQUAL):
            return Relation.COMPONENT
        elif (relation_with_edge is Relation.OVERLAP
              or relation_with_edge is Relation.COMPOSITE):
            return Relation.OVERLAP
        elif relation_with_edge is Relation.TOUCH:
            edge_start, edge_end = edge
            if has_no_touch:
                has_no_touch = False
            elif (has_no_cross
                  and index - last_touched_edge_index == 1
                  and start not in edge and end not in edge
                  and (angle_orientation(end, start, edge_start)
                       is Orientation.COLLINEAR)
                  and point_vertex_line_divides_angle(
                            start, last_touched_edge_start,
                            edge_start, edge_end)):
                has_no_cross = False
            last_touched_edge_index = index
            last_touched_edge_start = edge_start
        elif has_no_cross and relation_with_edge is Relation.CROSS:
            has_no_cross = False
    if (has_no_cross
            and not has_no_touch
            and last_touched_edge_index == len(contour) - 1):
        first_edge = first_edge_start, first_edge_end = contour[-1], contour[0]
        if (relate_segments(first_edge, segment) is Relation.TOUCH
                and start not in first_edge and end not in first_edge
                and (angle_orientation(end, start, first_edge_start)
                     is Orientation.COLLINEAR)
                and point_vertex_line_divides_angle(start, contour[-2],
                                                    first_edge_start,
                                                    first_edge_end)):
            has_no_cross = False
    return ((Relation.DISJOINT
             if has_no_touch
             else Relation.TOUCH)
            if has_no_cross
            else Relation.CROSS)


def point_vertex_line_divides_angle(point: Point,
                                    first_ray_point: Point,
                                    vertex: Point,
                                    second_ray_point: Point) -> bool:
    return (angle_orientation(first_ray_point, vertex, point)
            is angle_orientation(point, vertex, second_ray_point))


def relate_multisegment(contour: Contour,
                        multisegment: Multisegment) -> Relation:
    if not multisegment:
        return Relation.DISJOINT
    contour_bounding_box, multisegment_bounding_box = (
        bounding_box.from_iterable(contour),
        bounding_box.from_iterables(multisegment))
    if bounding_box.disjoint_with(contour_bounding_box,
                                  multisegment_bounding_box):
        return Relation.DISJOINT
    sweeper = OpenSweeper()
    sweeper.register_segments(to_segments(contour),
                              from_test=False)
    sweeper.register_segments(multisegment,
                              from_test=True)
    (_, contour_max_x, _, _), (_, multisegment_max_x, _, _) = (
        contour_bounding_box, multisegment_bounding_box)
    return process_open_linear_queue(sweeper,
                                     min(contour_max_x, multisegment_max_x))


def relate_contour(goal: Contour, test: Contour) -> Relation:
    goal_bounding_box, test_bounding_box = (bounding_box.from_iterable(goal),
                                            bounding_box.from_iterable(test))
    if bounding_box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    if equal(goal, test):
        return Relation.EQUAL
    sweeper = ClosedSweeper()
    sweeper.register_segments(to_segments(goal),
                              from_test=False)
    sweeper.register_segments(to_segments(test),
                              from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (goal_bounding_box,
                                                    test_bounding_box)
    return process_closed_linear_queue(sweeper,
                                       min(goal_max_x, test_max_x))


def equal(left: Contour, right: Contour) -> bool:
    if len(left) != len(right):
        return False
    try:
        index = right.index(left[0])
    except ValueError:
        return False
    same_oriented = orientation(left) is orientation(right)
    right_step = 1 if same_oriented else -1
    size = len(left)
    indices = chain(zip(range(size),
                        range(index, size)
                        if same_oriented
                        else range(index, -1, right_step)),
                    zip(range(size - index
                              if same_oriented
                              else index + 1,
                              size),
                        range(index)
                        if same_oriented
                        else range(size - 1, index - 1, right_step)))
    return all(left[left_index] == right[right_index]
               for left_index, right_index in indices)


def orientation(contour: Contour) -> Orientation:
    index = min(range(len(contour)),
                key=contour.__getitem__)
    return angle_orientation(contour[index], contour[index - 1],
                             contour[(index + 1) % len(contour)])


def to_segments(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))
