from typing import (Optional,
                    Tuple)

from ground.base import (Context,
                         Relation)
from ground.hints import Box

from . import box
from .contour import (equal as contours_equal,
                      orientation as contour_orientation,
                      point_vertex_line_divides_angle,
                      to_oriented_segments as contour_to_oriented_segments,
                      to_segments as contour_to_segments)
from .hints import (Contour,
                    Multisegment,
                    Point,
                    Region,
                    Segment)
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .segment import (relate_point as relate_point_to_segment,
                      relate_segment as relate_segments)
from .sweep import CompoundSweeper
from .utils import (Orientation,
                    orientation)


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
    for index, edge in enumerate(contour_to_segments(region)):
        if relate_point_to_segment(edge, point,
                                   context=context) is Relation.COMPONENT:
            return index, Relation.COMPONENT
        start, end = edge
        if ((start.y > point_y) is not (end.y > point_y)
                and ((end.y > start.y) is (orientation(start, end, point)
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
    start, end = segment
    for index, edge in enumerate(contour_to_segments(contour)):
        relation_with_edge = relate_segments(edge, segment,
                                             context=context)
        if (relation_with_edge is Relation.COMPONENT
                or relation_with_edge is Relation.EQUAL):
            return Relation.COMPONENT
        elif (relation_with_edge is Relation.OVERLAP
              or relation_with_edge is Relation.COMPOSITE):
            if has_no_overlap:
                has_no_overlap = False
        elif relation_with_edge is Relation.TOUCH:
            edge_start, edge_end = edge
            if has_no_touch:
                has_no_touch = False
            elif (index - last_touched_edge_index == 1
                  and start not in edge and end not in edge
                  and (orientation(start, end, edge_start)
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
    if not has_no_touch and last_touched_edge_index == len(contour) - 1:
        first_edge = first_edge_start, first_edge_end = contour[-1], contour[0]
        if (relate_segments(first_edge, segment,
                            context=context) is Relation.TOUCH
                and start not in first_edge and end not in first_edge
                and (orientation(start, end, first_edge_start)
                     is Orientation.COLLINEAR)
                and point_vertex_line_divides_angle(start, contour[-2],
                                                    first_edge_start,
                                                    first_edge_end,
                                                    context=context)):
            return Relation.CROSS
    return ((Relation.DISJOINT
             if has_no_touch
             else Relation.TOUCH)
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
    start, end = segment
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
            border_orientation = contour_orientation(region,
                                                     context=context)
            positively_oriented = (border_orientation
                                   is Orientation.COUNTERCLOCKWISE)
            edge_start, edge_end = (region[start_index - 1],
                                    region[start_index])
            if start == edge_start:
                prev_start = (region[start_index - 2]
                              if positively_oriented
                              else region[start_index])
                if (orientation(prev_start, edge_start, edge_end)
                        is border_orientation):
                    if (orientation(edge_start, prev_start, end)
                            is border_orientation
                            or orientation(edge_end, edge_start, end)
                            is border_orientation):
                        return Relation.TOUCH
                elif (orientation(edge_start, prev_start, end)
                      is orientation(edge_end, edge_start, end)
                      is border_orientation):
                    return Relation.TOUCH
            elif start == edge_end:
                next_end = (region[(start_index + 1) % len(region)]
                            if positively_oriented
                            else region[len(region) - start_index - 3])
                if (orientation(edge_start, edge_end, next_end)
                        is border_orientation):
                    if (orientation(edge_end, edge_start, end)
                            is border_orientation
                            or orientation(next_end, edge_end, end)
                            is border_orientation):
                        return Relation.TOUCH
                    elif (orientation(edge_end, edge_start, end)
                          is orientation(next_end, edge_end, end)
                          is border_orientation):
                        return Relation.TOUCH
            elif (orientation(edge_end, edge_start, end)
                  is border_orientation):
                return Relation.TOUCH
            edge_start, edge_end = region[end_index - 1], region[end_index]
            if end == edge_start:
                prev_start = (region[end_index - 2]
                              if positively_oriented
                              else region[end_index])
                if (orientation(prev_start, edge_start, edge_end)
                        is border_orientation):
                    if (orientation(edge_start, prev_start, start)
                            is border_orientation
                            or orientation(edge_end, edge_start, start)
                            is border_orientation):
                        return Relation.TOUCH
                elif (orientation(edge_start, prev_start, start)
                      is orientation(edge_end, edge_start, start)
                      is border_orientation):
                    return Relation.TOUCH
            elif end == edge_end:
                next_end = (region[(end_index + 1) % len(region)]
                            if positively_oriented
                            else region[len(region) - end_index - 3])
                if (orientation(edge_start, edge_end, next_end)
                        is border_orientation):
                    if (orientation(edge_end, edge_start, start)
                            is border_orientation
                            or orientation(next_end, edge_end, start)
                            is border_orientation):
                        return Relation.TOUCH
                elif (orientation(edge_end, edge_start, start)
                      is orientation(next_end, edge_end, start)
                      is border_orientation):
                    return Relation.TOUCH
            elif (orientation(edge_end, edge_start, start)
                  is border_orientation):
                return Relation.TOUCH
            return Relation.ENCLOSED


def relate_multisegment(region: Region,
                        multisegment: Multisegment,
                        *,
                        context: Context) -> Relation:
    return (_relate_multisegment(region, multisegment,
                                 box.from_iterables(multisegment,
                                                    context=context),
                                 context=context)
            if multisegment
            else Relation.DISJOINT)


def _relate_multisegment(region: Region,
                         multisegment: Multisegment,
                         multisegment_bounding_box: Box,
                         *,
                         context: Context) -> Relation:
    region_bounding_box = box.from_iterable(region,
                                            context=context)
    if box.disjoint_with(multisegment_bounding_box,
                         region_bounding_box):
        return Relation.DISJOINT
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_segments(region,
                                                   context=context),
                              from_test=False)
    sweeper.register_segments(multisegment,
                              from_test=True)
    return process_linear_compound_queue(sweeper,
                                         min(multisegment_bounding_box.max_x,
                                             region_bounding_box.max_x))


def relate_contour(region: Region, contour: Contour,
                   *,
                   context: Context) -> Relation:
    return _relate_contour(region, contour,
                           box.from_iterable(contour,
                                             context=context),
                           context=context)


def _relate_contour(region: Region,
                    contour: Contour,
                    contour_bounding_box: Box,
                    *,
                    context: Context) -> Relation:
    region_bounding_box = box.from_iterable(region,
                                            context=context)
    if box.disjoint_with(contour_bounding_box, region_bounding_box):
        return Relation.DISJOINT
    if equal(region, contour,
             context=context):
        return Relation.COMPONENT
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_segments(region,
                                                   context=context),
                              from_test=False)
    sweeper.register_segments(contour_to_segments(contour),
                              from_test=True)
    return process_linear_compound_queue(sweeper,
                                         min(contour_bounding_box.max_x,
                                             region_bounding_box.max_x))


def relate_region(goal: Region, test: Region,
                  *,
                  context: Context) -> Relation:
    return _relate_region(goal, test,
                          box.from_iterable(goal,
                                            context=context),
                          box.from_iterable(test,
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
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_segments(goal,
                                                   context=context),
                              from_test=False)
    sweeper.register_segments(to_oriented_segments(test,
                                                   context=context),
                              from_test=True)
    return process_compound_queue(sweeper, min(goal_bounding_box.max_x,
                                               test_bounding_box.max_x))


equal = contours_equal
to_oriented_segments = contour_to_oriented_segments
