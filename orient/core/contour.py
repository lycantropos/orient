from itertools import chain
from typing import Iterable

from ground.base import (Context,
                         Relation)
from ground.hints import (Point,
                          Segment)

from . import box
from .hints import (Contour,
                    Multisegment,
                    SegmentEndpoints)
from .multisegment import to_segments_endpoints
from .processing import (process_closed_linear_queue,
                         process_open_linear_queue)
from .segment import (_relate_point as relate_point_to_segment,
                      _relate_segment as relate_segments)
from .sweep import (CompoundSweeper,
                    LinearSweeper)
from .utils import (Orientation,
                    orientation as angle_orientation)


def relate_point(contour: Contour, point: Point,
                 *,
                 context: Context) -> Relation:
    return (Relation.DISJOINT
            if all(relate_point_to_segment(edge_start, edge_end, point,
                                           context=context)
                   is Relation.DISJOINT
                   for edge_start, edge_end in to_edges_endpoints(contour))
            else Relation.COMPONENT)


def relate_segment(contour: Contour, segment: Segment,
                   *,
                   context: Context) -> Relation:
    has_no_touch = has_no_cross = True
    last_touched_edge_index = last_touched_edge_start = None
    start, end = segment.start, segment.end
    for index, edge_endpoints in enumerate(to_edges_endpoints(contour)):
        edge_start, edge_end = edge_endpoints
        relation_with_edge = relate_segments(edge_start, edge_end, start, end,
                                             context=context)
        if (relation_with_edge is Relation.COMPONENT
                or relation_with_edge is Relation.EQUAL):
            return Relation.COMPONENT
        elif (relation_with_edge is Relation.OVERLAP
              or relation_with_edge is Relation.COMPOSITE):
            return Relation.OVERLAP
        elif relation_with_edge is Relation.TOUCH:
            if has_no_touch:
                has_no_touch = False
            elif (has_no_cross
                  and index - last_touched_edge_index == 1
                  and start not in edge_endpoints and end not in edge_endpoints
                  and (angle_orientation(start, end, edge_start)
                       is Orientation.COLLINEAR)
                  and point_vertex_line_divides_angle(start,
                                                      last_touched_edge_start,
                                                      edge_start, edge_end,
                                                      context=context)):
                has_no_cross = False
            last_touched_edge_index = index
            last_touched_edge_start = edge_start
        elif has_no_cross and relation_with_edge is Relation.CROSS:
            has_no_cross = False
    if (has_no_cross
            and not has_no_touch
            and last_touched_edge_index == len(contour) - 1):
        first_edge_endpoints = first_edge_start, first_edge_end = (contour[-1],
                                                                   contour[0])
        if (relate_segments(first_edge_start, first_edge_end, start, end,
                            context=context) is Relation.TOUCH
                and start not in first_edge_endpoints
                and end not in first_edge_endpoints
                and (angle_orientation(start, end, first_edge_start)
                     is Orientation.COLLINEAR)
                and point_vertex_line_divides_angle(start, contour[-2],
                                                    first_edge_start,
                                                    first_edge_end,
                                                    context=context)):
            has_no_cross = False
    return ((Relation.DISJOINT
             if has_no_touch
             else Relation.TOUCH)
            if has_no_cross
            else Relation.CROSS)


def point_vertex_line_divides_angle(point: Point,
                                    first_ray_point: Point,
                                    vertex: Point,
                                    second_ray_point: Point,
                                    *,
                                    context: Context) -> bool:
    return (angle_orientation(vertex, first_ray_point, point)
            is angle_orientation(vertex, point, second_ray_point))


def relate_multisegment(contour: Contour,
                        multisegment: Multisegment,
                        *,
                        context: Context) -> Relation:
    if not multisegment:
        return Relation.DISJOINT
    contour_bounding_box, multisegment_bounding_box = (
        box.from_iterable(contour,
                          context=context),
        box.from_multisegment(multisegment,
                              context=context))
    if box.disjoint_with(contour_bounding_box,
                         multisegment_bounding_box):
        return Relation.DISJOINT
    sweeper = LinearSweeper()
    sweeper.register_segments(to_edges_endpoints(contour),
                              from_test=False)
    sweeper.register_segments(to_segments_endpoints(multisegment),
                              from_test=True)
    return process_open_linear_queue(sweeper,
                                     min(contour_bounding_box.max_x,
                                         multisegment_bounding_box.max_x))


def relate_contour(goal: Contour, test: Contour,
                   *,
                   context: Context) -> Relation:
    goal_bounding_box, test_bounding_box = (box.from_iterable(goal,
                                                              context=context),
                                            box.from_iterable(test,
                                                              context=context))
    if box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    if equal(goal, test,
             context=context):
        return Relation.EQUAL
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_edges_endpoints(goal,
                                                          context=context),
                              from_test=False)
    sweeper.register_segments(to_oriented_edges_endpoints(test,
                                                          context=context),
                              from_test=True)
    return process_closed_linear_queue(sweeper,
                                       min(goal_bounding_box.max_x,
                                           test_bounding_box.max_x))


def equal(left: Contour, right: Contour,
          *,
          context: Context) -> bool:
    if len(left) != len(right):
        return False
    try:
        index = right.index(left[0])
    except ValueError:
        return False
    same_oriented = (orientation(left,
                                 context=context)
                     is orientation(right,
                                    context=context))
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


def orientation(contour: Contour,
                *,
                context: Context) -> Orientation:
    index = min(range(len(contour)),
                key=contour.__getitem__)
    return angle_orientation(contour[index - 1], contour[index],
                             contour[(index + 1) % len(contour)])


def to_edges_endpoints(contour: Contour) -> Iterable[SegmentEndpoints]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))


def to_oriented_edges_endpoints(contour: Contour,
                                *,
                                clockwise: bool = False,
                                context: Context
                                ) -> Iterable[SegmentEndpoints]:
    return (((contour[index - 1], contour[index])
             for index in range(len(contour)))
            if (orientation(contour,
                            context=context)
                is (Orientation.CLOCKWISE
                    if clockwise
                    else Orientation.COUNTERCLOCKWISE))
            else ((contour[index], contour[index - 1])
                  for index in range(len(contour) - 1, -1, -1)))
