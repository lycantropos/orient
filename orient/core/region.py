from typing import (Optional,
                    Tuple)

from ground.base import (Context,
                         Location,
                         Orientation,
                         Relation)
from ground.hints import (Box,
                          Contour,
                          Multisegment,
                          Point,
                          Segment)

from . import box
from .contour import (
    equal as contours_equal,
    orientation as contour_orientation,
    point_vertex_line_divides_angle,
    to_edges_endpoints as contour_to_edges_endpoints,
    to_oriented_edges_endpoints as contour_to_oriented_segments
)
from .events_queue import CompoundEventsQueue
from .hints import Region
from .multisegment import to_segments_endpoints
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .segment import (locate_point as locate_point_in_segment,
                      relate_segment as relate_segments)


def locate_point(region: Region,
                 point: Point,
                 context: Context) -> Location:
    _, location = _locate_point(region, point, context)
    return location


def _locate_point(region: Region,
                  point: Point,
                  context: Context) -> Tuple[Optional[int], Location]:
    result = False
    point_y = point.y
    for index, edge in enumerate(context.contour_segments(region)):
        if locate_point_in_segment(edge, point, context) is Location.BOUNDARY:
            return index, Location.BOUNDARY
        start, end = edge.start, edge.end
        if ((start.y > point_y) is not (end.y > point_y)
                and ((end.y > start.y)
                     is (context.angle_orientation(start, end, point)
                         is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return None, (Location.INTERIOR if result else Location.EXTERIOR)


def _relate_segment_to_contour(contour: Contour,
                               segment: Segment,
                               context: Context) -> Relation:
    # similar to segment-in-contour check
    # but cross has higher priority over overlap
    # because cross with contour will be considered as cross with region
    # whereas overlap with contour can't be an overlap with region
    # and should be classified by further analysis
    has_no_touch = has_no_overlap = True
    last_touched_edge_index = last_touched_edge_start = None
    start, end = segment.start, segment.end
    for index, edge in enumerate(context.contour_segments(contour)):
        edge_start, edge_end = edge_endpoints = edge.start, edge.end
        relation_with_edge = relate_segments(edge, segment, context)
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
                                                      context)):
                return Relation.CROSS
            last_touched_edge_index = index
            last_touched_edge_start = edge_start
        elif relation_with_edge is Relation.CROSS:
            return Relation.CROSS
    vertices = contour.vertices
    if not has_no_touch and last_touched_edge_index == len(vertices) - 1:
        first_edge_endpoints = first_edge_start, first_edge_end = (
            vertices[-1], vertices[0]
        )
        if (relate_segments(context.segment_cls(first_edge_start,
                                                first_edge_end), segment,
                            context) is Relation.TOUCH
                and start not in first_edge_endpoints
                and end not in first_edge_endpoints
                and (context.angle_orientation(start, end, first_edge_start)
                     is Orientation.COLLINEAR)
                and point_vertex_line_divides_angle(start, vertices[-2],
                                                    first_edge_start,
                                                    first_edge_end, context)):
            return Relation.CROSS
    return ((Relation.DISJOINT if has_no_touch else Relation.TOUCH)
            if has_no_overlap
            else Relation.OVERLAP)


def relate_segment(region: Region,
                   segment: Segment,
                   context: Context) -> Relation:
    relation_with_contour = _relate_segment_to_contour(region, segment,
                                                       context)
    if (relation_with_contour is Relation.CROSS
            or relation_with_contour is Relation.COMPONENT):
        return relation_with_contour
    start, end = segment.start, segment.end
    start_index, start_location = _locate_point(region, start, context)
    if relation_with_contour is Relation.DISJOINT:
        return (Relation.DISJOINT
                if start_location is Location.EXTERIOR
                else Relation.WITHIN)
    elif start_location is Location.EXTERIOR:
        return Relation.TOUCH
    elif start_location is Location.INTERIOR:
        return Relation.ENCLOSED
    else:
        end_index, end_location = _locate_point(region, end, context)
        if end_location is Location.EXTERIOR:
            return Relation.TOUCH
        elif end_location is Location.INTERIOR:
            return Relation.ENCLOSED
        else:
            angle_orientation = context.angle_orientation
            border_orientation = contour_orientation(region, context)
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
                        context: Context) -> Relation:
    multisegment_bounding_box = context.segments_box(multisegment.segments)
    region_bounding_box = context.contour_box(region)
    if box.disjoint_with(multisegment_bounding_box, region_bounding_box):
        return Relation.DISJOINT
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_segments(region, context),
                          from_test=False)
    events_queue.register(to_segments_endpoints(multisegment),
                          from_test=True)
    return process_linear_compound_queue(events_queue,
                                         min(multisegment_bounding_box.max_x,
                                             region_bounding_box.max_x))


def relate_contour(region: Region,
                   contour: Contour,
                   context: Context) -> Relation:
    return _relate_contour(region, contour, context.contour_box(contour),
                           context)


def _relate_contour(region: Region,
                    contour: Contour,
                    contour_bounding_box: Box,
                    context: Context) -> Relation:
    region_bounding_box = context.contour_box(region)
    if box.disjoint_with(contour_bounding_box, region_bounding_box):
        return Relation.DISJOINT
    if equal(region, contour, context):
        return Relation.COMPONENT
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_segments(region, context),
                          from_test=False)
    events_queue.register(contour_to_edges_endpoints(contour),
                          from_test=True)
    return process_linear_compound_queue(events_queue,
                                         min(contour_bounding_box.max_x,
                                             region_bounding_box.max_x))


def relate_region(goal: Region,
                  test: Region,
                  context: Context) -> Relation:
    return _relate_region(goal, test, context.contour_box(goal),
                          context.contour_box(test), context)


def _relate_region(goal: Region,
                   test: Region,
                   goal_bounding_box: Box,
                   test_bounding_box: Box,
                   context: Context) -> Relation:
    if box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    if equal(goal, test, context):
        return Relation.EQUAL
    events_queue = CompoundEventsQueue(context)
    events_queue.register(to_oriented_segments(goal, context),
                          from_test=False)
    events_queue.register(to_oriented_segments(test, context),
                          from_test=True)
    return process_compound_queue(events_queue, min(goal_bounding_box.max_x,
                                                    test_bounding_box.max_x))


equal = contours_equal
to_oriented_segments = contour_to_oriented_segments
