from itertools import chain
from typing import Iterable

from ground.base import (Context,
                         Orientation,
                         Relation)
from ground.hints import (Contour,
                          Multisegment,
                          Point,
                          Segment)

from . import box
from .events_queue import (CompoundEventsQueue,
                           LinearEventsQueue)
from .hints import SegmentEndpoints
from .multisegment import to_segments_endpoints
from .processing import (process_closed_linear_queue,
                         process_open_linear_queue)
from .segment import (relate_point as relate_point_to_segment,
                      relate_segment as relate_segments)


def relate_point(contour: Contour, point: Point, context: Context) -> Relation:
    return (Relation.DISJOINT
            if all(relate_point_to_segment(edge, point, context)
                   is Relation.DISJOINT
                   for edge in context.contour_edges(contour))
            else Relation.COMPONENT)


def relate_segment(contour: Contour,
                   segment: Segment,
                   context: Context) -> Relation:
    angle_orientation = context.angle_orientation
    has_no_touch = has_no_cross = True
    last_touched_edge_index = last_touched_edge_start = None
    start, end = segment.start, segment.end
    for index, edge in enumerate(context.contour_edges(contour)):
        edge_start, edge_end = edge_endpoints = edge.start, edge.end
        relation_with_edge = relate_segments(edge, segment, context)
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
                                                      context)):
                has_no_cross = False
            last_touched_edge_index = index
            last_touched_edge_start = edge_start
        elif has_no_cross and relation_with_edge is Relation.CROSS:
            has_no_cross = False
    vertices = contour.vertices
    if (has_no_cross
            and not has_no_touch
            and last_touched_edge_index == len(vertices) - 1):
        first_edge_endpoints = first_edge_start, first_edge_end = (
            vertices[-1], vertices[0])
        if (relate_segments(context.segment_cls(first_edge_start,
                                                first_edge_end), segment,
                            context) is Relation.TOUCH
                and start not in first_edge_endpoints
                and end not in first_edge_endpoints
                and (angle_orientation(start, end, first_edge_start)
                     is Orientation.COLLINEAR)
                and point_vertex_line_divides_angle(start, vertices[-2],
                                                    first_edge_start,
                                                    first_edge_end,
                                                    context)):
            has_no_cross = False
    return ((Relation.DISJOINT if has_no_touch else Relation.TOUCH)
            if has_no_cross
            else Relation.CROSS)


def point_vertex_line_divides_angle(point: Point,
                                    first_ray_point: Point,
                                    vertex: Point,
                                    second_ray_point: Point,
                                    context: Context) -> bool:
    return (context.angle_orientation(vertex, first_ray_point, point)
            is context.angle_orientation(vertex, point, second_ray_point))


def relate_multisegment(contour: Contour,
                        multisegment: Multisegment,
                        context: Context) -> Relation:
    contour_bounding_box = context.contour_box(contour)
    multisegment_bounding_box = context.segments_box(multisegment.segments)
    if box.disjoint_with(contour_bounding_box, multisegment_bounding_box):
        return Relation.DISJOINT
    events_queue = LinearEventsQueue(context)
    events_queue.register(to_edges_endpoints(contour),
                          from_test=False)
    events_queue.register(to_segments_endpoints(multisegment),
                          from_test=True)
    return process_open_linear_queue(events_queue,
                                     min(contour_bounding_box.max_x,
                                         multisegment_bounding_box.max_x))


def relate_contour(goal: Contour, test: Contour, context: Context) -> Relation:
    goal_bounding_box, test_bounding_box = (context.contour_box(goal),
                                            context.contour_box(test))
    if box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    if equal(goal, test, context):
        return Relation.EQUAL
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_edges_endpoints(goal, context),
                          from_test=False)
    events_queue.register(to_oriented_edges_endpoints(test, context),
                          from_test=True)
    return process_closed_linear_queue(events_queue,
                                       min(goal_bounding_box.max_x,
                                           test_bounding_box.max_x))


def equal(left: Contour, right: Contour, context: Context) -> bool:
    left_vertices, right_vertices = left.vertices, right.vertices
    if len(left_vertices) != len(right_vertices):
        return False
    try:
        index = right_vertices.index(left_vertices[0])
    except ValueError:
        return False
    same_oriented = orientation(left, context) is orientation(right, context)
    right_step = 1 if same_oriented else -1
    size = len(left_vertices)
    indices = chain(zip(range(size),
                        range(index, size)
                        if same_oriented
                        else range(index, -1, right_step)),
                    zip(range(size - index if same_oriented else index + 1,
                              size),
                        range(index)
                        if same_oriented
                        else range(size - 1, index - 1, right_step)))
    return all(left_vertices[left_index] == right_vertices[right_index]
               for left_index, right_index in indices)


def orientation(contour: Contour, context: Context) -> Orientation:
    vertices = contour.vertices
    index = min(range(len(vertices)),
                key=vertices.__getitem__)
    return context.angle_orientation(vertices[index - 1], vertices[index],
                                     vertices[(index + 1) % len(vertices)])


def to_edges_endpoints(contour: Contour) -> Iterable[SegmentEndpoints]:
    vertices = contour.vertices
    return ((vertices[index - 1], vertices[index])
            for index in range(len(vertices)))


def to_oriented_edges_endpoints(contour: Contour,
                                context: Context,
                                clockwise: bool = False
                                ) -> Iterable[SegmentEndpoints]:
    vertices = contour.vertices
    return (((vertices[index - 1], vertices[index])
             for index in range(len(vertices)))
            if (orientation(contour, context)
                is (Orientation.CLOCKWISE
                    if clockwise
                    else Orientation.COUNTERCLOCKWISE))
            else ((vertices[index], vertices[index - 1])
                  for index in range(len(vertices) - 1, -1, -1)))
