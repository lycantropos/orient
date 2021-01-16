from typing import (Optional,
                    Tuple)

from ground.base import (Context,
                         Orientation,
                         Relation)
from ground.hints import (Box,
                          Contour,
                          Multisegment,
                          Point,
                          Segment)

from . import box
from .contour import (equal as contours_equal,
                      orientation as contour_orientation,
                      point_vertex_line_divides_angle,
                      to_edges_endpoints as contour_to_edges_endpoints,
                      to_oriented_edges_endpoints
                      as contour_to_oriented_segments)
from .events_queue import CompoundEventsQueue
from .hints import Region
from .multisegment import to_segments_endpoints
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .segment import (_relate_point as relate_point_to_segment,
                      _relate_segment as relate_segments)


def relate_point(region: Region, point: Point,
                 *,
                 context: Context) -> Relation:
    _, relation = _relate_point(region, point,
                                context=context)
    return relation


def _relate_point(region: Region, point: Point,
                  *,
                  context: Context) -> Tuple[Optional[int],
                                             Relation]:
    result = False
    point_y = point.y
    for index, (start, end) in enumerate(contour_to_edges_endpoints(region)):
        if relate_point_to_segment(start, end, point,
                                   context=context) is Relation.COMPONENT:
            return index, Relation.COMPONENT
        if ((start.y > point_y) is not (end.y > point_y)
                and ((end.y > start.y)
                     is (context.angle_orientation(start, end, point)
                         is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return None, (Relation.WITHIN if result else Relation.DISJOINT)


def _relate_segment_to_contour(contour: Contour, segment: Segment,
                               *,
                               context: Context) -> Relation:
    # similar to segment-in-contour check
    # but cross has higher priority over overlap
    # because cross with contour will be considered as cross with region
    # whereas overlap with contour can't be an overlap with region
    # and should be classified by further analysis
    has_no_touch = has_no_overlap = True
    last_touched_edge_index = last_touched_edge_start = None
    start, end = segment.start, segment.end
    for index, edge_endpoints in enumerate(contour_to_edges_endpoints(
            contour)):
        edge_start, edge_end = edge_endpoints
        relation_with_edge = relate_segments(edge_start, edge_end, start, end,
                                             context=context)
        if (relation_with_edge is Relation.COMPONENT
                or relation_with_edge is Relation.EQUAL):
            return Relation.COMPONENT
        elif (relation_with_edge is Relation.OVERLAP
              or relation_with_edge is Relation.COMPOSITE):
            if has_no_overlap:
                has_no_overlap = False
        elif relation_with_edge is Relation.TOUCH:
            if has_no_touch:
                has_no_touch = False
            elif (index - last_touched_edge_index == 1
                  and start not in edge_endpoints and end not in edge_endpoints
                  and (context.angle_orientation(start, end, edge_start)
                       is Orientation.COLLINEAR)
                  and point_vertex_line_divides_angle(start,
                                                      last_touched_edge_start,
                                                      edge_start, edge_end,
                                                      context=context)):
                return Relation.CROSS
            last_touched_edge_index = index
            last_touched_edge_start = edge_start
        elif relation_with_edge is Relation.CROSS:
            return Relation.CROSS
    vertices = contour.vertices
    if not has_no_touch and last_touched_edge_index == len(vertices) - 1:
        first_edge_endpoints = first_edge_start, first_edge_end = (
            vertices[-1], vertices[0])
        if (relate_segments(first_edge_start, first_edge_end, start, end,
                            context=context) is Relation.TOUCH
                and start not in first_edge_endpoints
                and end not in first_edge_endpoints
                and (context.angle_orientation(start, end, first_edge_start)
                     is Orientation.COLLINEAR)
                and point_vertex_line_divides_angle(start, vertices[-2],
                                                    first_edge_start,
                                                    first_edge_end,
                                                    context=context)):
            return Relation.CROSS
    return ((Relation.DISJOINT if has_no_touch else Relation.TOUCH)
            if has_no_overlap
            else Relation.OVERLAP)


def relate_segment(region: Region, segment: Segment,
                   *,
                   context: Context) -> Relation:
    relation_with_contour = _relate_segment_to_contour(region, segment,
                                                       context=context)
    if (relation_with_contour is Relation.CROSS
            or relation_with_contour is Relation.COMPONENT):
        return relation_with_contour
    start, end = segment.start, segment.end
    start_index, start_relation = _relate_point(region, start,
                                                context=context)
    if relation_with_contour is Relation.DISJOINT:
        return (Relation.DISJOINT
                if start_relation is Relation.DISJOINT
                else Relation.WITHIN)
    elif start_relation is Relation.DISJOINT:
        return Relation.TOUCH
    elif start_relation is Relation.WITHIN:
        return Relation.ENCLOSED
    else:
        end_index, end_relation = _relate_point(region, end,
                                                context=context)
        if end_relation is Relation.DISJOINT:
            return Relation.TOUCH
        elif end_relation is Relation.WITHIN:
            return Relation.ENCLOSED
        else:
            angle_orientation = context.angle_orientation
            border_orientation = contour_orientation(region,
                                                     context=context)
            positively_oriented = (border_orientation
                                   is Orientation.COUNTERCLOCKWISE)
            vertices = region.vertices
            edge_start, edge_end = (vertices[start_index - 1],
                                    vertices[start_index])
            if start == edge_start:
                prev_start = (vertices[start_index - 2]
                              if positively_oriented
                              else vertices[start_index])
                if (angle_orientation(prev_start, edge_start, edge_end)
                        is border_orientation):
                    if (angle_orientation(edge_start, prev_start, end)
                            is border_orientation
                            or angle_orientation(edge_end, edge_start, end)
                            is border_orientation):
                        return Relation.TOUCH
                elif (angle_orientation(edge_start, prev_start, end)
                      is angle_orientation(edge_end, edge_start, end)
                      is border_orientation):
                    return Relation.TOUCH
            elif start == edge_end:
                next_end = (vertices[(start_index + 1) % len(vertices)]
                            if positively_oriented
                            else vertices[len(vertices) - start_index - 3])
                if (angle_orientation(edge_start, edge_end, next_end)
                        is border_orientation):
                    if (angle_orientation(edge_end, edge_start, end)
                            is border_orientation
                            or angle_orientation(next_end, edge_end, end)
                            is border_orientation):
                        return Relation.TOUCH
                    elif (angle_orientation(edge_end, edge_start, end)
                          is angle_orientation(next_end, edge_end, end)
                          is border_orientation):
                        return Relation.TOUCH
            elif (angle_orientation(edge_end, edge_start, end)
                  is border_orientation):
                return Relation.TOUCH
            edge_start, edge_end = vertices[end_index - 1], vertices[end_index]
            if end == edge_start:
                prev_start = (vertices[end_index - 2]
                              if positively_oriented
                              else vertices[end_index])
                if (angle_orientation(prev_start, edge_start, edge_end)
                        is border_orientation):
                    if (angle_orientation(edge_start, prev_start, start)
                            is border_orientation
                            or angle_orientation(edge_end, edge_start, start)
                            is border_orientation):
                        return Relation.TOUCH
                elif (angle_orientation(edge_start, prev_start, start)
                      is angle_orientation(edge_end, edge_start, start)
                      is border_orientation):
                    return Relation.TOUCH
            elif end == edge_end:
                next_end = (vertices[(end_index + 1) % len(vertices)]
                            if positively_oriented
                            else vertices[len(vertices) - end_index - 3])
                if (angle_orientation(edge_start, edge_end, next_end)
                        is border_orientation):
                    if (angle_orientation(edge_end, edge_start, start)
                            is border_orientation
                            or angle_orientation(next_end, edge_end, start)
                            is border_orientation):
                        return Relation.TOUCH
                elif (angle_orientation(edge_end, edge_start, start)
                      is angle_orientation(next_end, edge_end, start)
                      is border_orientation):
                    return Relation.TOUCH
            elif (angle_orientation(edge_end, edge_start, start)
                  is border_orientation):
                return Relation.TOUCH
            return Relation.ENCLOSED


def relate_multisegment(region: Region,
                        multisegment: Multisegment,
                        *,
                        context: Context) -> Relation:
    return (_relate_multisegment(region, multisegment,
                                 box.from_multisegment(multisegment,
                                                       context=context),
                                 context=context)
            if multisegment.segments
            else Relation.DISJOINT)


def _relate_multisegment(region: Region,
                         multisegment: Multisegment,
                         multisegment_bounding_box: Box,
                         *,
                         context: Context) -> Relation:
    region_bounding_box = box.from_contour(region,
                                           context=context)
    if box.disjoint_with(multisegment_bounding_box,
                         region_bounding_box):
        return Relation.DISJOINT
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_segments(region,
                                               context=context),
                          from_test=False)
    events_queue.register(to_segments_endpoints(multisegment),
                          from_test=True)
    return process_linear_compound_queue(events_queue,
                                         min(multisegment_bounding_box.max_x,
                                             region_bounding_box.max_x))


def relate_contour(region: Region, contour: Contour,
                   *,
                   context: Context) -> Relation:
    return _relate_contour(region, contour,
                           box.from_contour(contour,
                                            context=context),
                           context=context)


def _relate_contour(region: Region,
                    contour: Contour,
                    contour_bounding_box: Box,
                    *,
                    context: Context) -> Relation:
    region_bounding_box = box.from_contour(region,
                                           context=context)
    if box.disjoint_with(contour_bounding_box, region_bounding_box):
        return Relation.DISJOINT
    if equal(region, contour,
             context=context):
        return Relation.COMPONENT
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_segments(region,
                                               context=context),
                          from_test=False)
    events_queue.register(contour_to_edges_endpoints(contour),
                          from_test=True)
    return process_linear_compound_queue(events_queue,
                                         min(contour_bounding_box.max_x,
                                             region_bounding_box.max_x))


def relate_region(goal: Region, test: Region,
                  *,
                  context: Context) -> Relation:
    return _relate_region(goal, test,
                          box.from_contour(goal,
                                           context=context),
                          box.from_contour(test,
                                           context=context),
                          context=context)


def _relate_region(goal: Region,
                   test: Region,
                   goal_bounding_box: Box,
                   test_bounding_box: Box,
                   *,
                   context: Context) -> Relation:
    if box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    if equal(goal, test,
             context=context):
        return Relation.EQUAL
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_segments(goal,
                                               context=context),
                          from_test=False)
    events_queue.register(to_oriented_segments(test,
                                               context=context),
                          from_test=True)
    return process_compound_queue(events_queue, min(goal_bounding_box.max_x,
                                                    test_bounding_box.max_x))


equal = contours_equal
to_oriented_segments = contour_to_oriented_segments
