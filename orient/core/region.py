from typing import (Optional,
                    Tuple)

from robust.angular import (Orientation,
                            orientation as angle_orientation)

from orient.hints import (Contour,
                          Multisegment,
                          Point,
                          Region,
                          Segment)
from . import bounding
from .contour import (equal as contours_equal,
                      orientation as contour_orientation,
                      point_vertex_line_divides_angle,
                      to_oriented_segments as contour_to_oriented_segments,
                      to_segments as contour_to_segments)
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .relation import Relation
from .segment import (relate_point as relate_point_to_segment,
                      relate_segment as relate_segments)
from .sweep import CompoundSweeper


def relate_point(region: Region, point: Point) -> Relation:
    _, relation = _relate_point(region, point)
    return relation


def _relate_point(region: Region, point: Point) -> Tuple[Optional[int],
                                                         Relation]:
    result = False
    _, point_y = point
    for index, edge in enumerate(contour_to_segments(region)):
        if relate_point_to_segment(edge, point) is Relation.COMPONENT:
            return index, Relation.COMPONENT
        start, end = edge
        (_, start_y), (_, end_y) = start, end
        if ((start_y > point_y) is not (end_y > point_y)
                and ((end_y > start_y) is (angle_orientation(end, start, point)
                                           is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return None, (Relation.WITHIN
                  if result
                  else Relation.DISJOINT)


def _relate_segment_to_contour(contour: Contour, segment: Segment) -> Relation:
    # similar to segment-in-contour check
    # but cross has higher priority over overlap
    # because cross with contour will be considered as cross with region
    # whereas overlap with contour can't be an overlap with region
    # and should be classified by further analysis
    has_no_touch = has_no_overlap = True
    last_touched_edge_index = last_touched_edge_start = None
    start, end = segment
    for index, edge in enumerate(contour_to_segments(contour)):
        relation_with_edge = relate_segments(edge, segment)
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
                  and (angle_orientation(end, start, edge_start)
                       is Orientation.COLLINEAR)
                  and point_vertex_line_divides_angle(start,
                                                      last_touched_edge_start,
                                                      edge_start, edge_end)):
                return Relation.CROSS
            last_touched_edge_index = index
            last_touched_edge_start = edge_start
        elif relation_with_edge is Relation.CROSS:
            return Relation.CROSS
    if not has_no_touch and last_touched_edge_index == len(contour) - 1:
        first_edge = first_edge_start, first_edge_end = contour[-1], contour[0]
        if (relate_segments(first_edge, segment) is Relation.TOUCH
                and start not in first_edge and end not in first_edge
                and (angle_orientation(end, start, first_edge_start)
                     is Orientation.COLLINEAR)
                and point_vertex_line_divides_angle(start, contour[-2],
                                                    first_edge_start,
                                                    first_edge_end)):
            return Relation.CROSS
    return ((Relation.DISJOINT
             if has_no_touch
             else Relation.TOUCH)
            if has_no_overlap
            else Relation.OVERLAP)


def relate_segment(region: Region, segment: Segment) -> Relation:
    relation_with_contour = _relate_segment_to_contour(region, segment)
    if (relation_with_contour is Relation.CROSS
            or relation_with_contour is Relation.COMPONENT):
        return relation_with_contour
    start, end = segment
    start_index, start_relation = _relate_point(region, start)
    if relation_with_contour is Relation.DISJOINT:
        return (Relation.DISJOINT
                if start_relation is Relation.DISJOINT
                else Relation.WITHIN)
    elif start_relation is Relation.DISJOINT:
        return Relation.TOUCH
    elif start_relation is Relation.WITHIN:
        return Relation.ENCLOSED
    else:
        end_index, end_relation = _relate_point(region, end)
        if end_relation is Relation.DISJOINT:
            return Relation.TOUCH
        elif end_relation is Relation.WITHIN:
            return Relation.ENCLOSED
        else:
            border_orientation = contour_orientation(region)
            positively_oriented = (border_orientation
                                   is Orientation.COUNTERCLOCKWISE)
            edge_start, edge_end = (region[start_index - 1],
                                    region[start_index])
            if start == edge_start:
                prev_start = (region[start_index - 2]
                              if positively_oriented
                              else region[start_index])
                if (angle_orientation(edge_start, prev_start, edge_end)
                        is border_orientation):
                    if (angle_orientation(prev_start, edge_start, end)
                            is border_orientation
                            or angle_orientation(edge_start, edge_end,
                                                 end)
                            is border_orientation):
                        return Relation.TOUCH
                elif (angle_orientation(prev_start, edge_start, end)
                      is angle_orientation(edge_start, edge_end, end)
                      is border_orientation):
                    return Relation.TOUCH
            elif start == edge_end:
                next_end = (region[(start_index + 1) % len(region)]
                            if positively_oriented
                            else region[len(region) - start_index - 3])
                if (angle_orientation(edge_end, edge_start, next_end)
                        is border_orientation):
                    if (angle_orientation(edge_start, edge_end, end)
                            is border_orientation
                            or angle_orientation(edge_end, next_end,
                                                 end)
                            is border_orientation):
                        return Relation.TOUCH
                    elif (angle_orientation(edge_start, edge_end, end)
                          is angle_orientation(edge_end, next_end, end)
                          is border_orientation):
                        return Relation.TOUCH
            elif (angle_orientation(edge_start, edge_end, end)
                  is border_orientation):
                return Relation.TOUCH
            edge_start, edge_end = region[end_index - 1], region[end_index]
            if end == edge_start:
                prev_start = (region[end_index - 2]
                              if positively_oriented
                              else region[end_index])
                if (angle_orientation(edge_start, prev_start, edge_end)
                        is border_orientation):
                    if (angle_orientation(prev_start, edge_start,
                                          start)
                            is border_orientation
                            or angle_orientation(edge_start, edge_end,
                                                 start)
                            is border_orientation):
                        return Relation.TOUCH
                elif (angle_orientation(prev_start, edge_start, start)
                      is angle_orientation(edge_start, edge_end, start)
                      is border_orientation):
                    return Relation.TOUCH
            elif end == edge_end:
                next_end = (region[(end_index + 1) % len(region)]
                            if positively_oriented
                            else region[len(region) - end_index - 3])
                if (angle_orientation(edge_end, edge_start, next_end)
                        is border_orientation):
                    if (angle_orientation(edge_start, edge_end, start)
                            is border_orientation
                            or angle_orientation(edge_end, next_end,
                                                 start)
                            is border_orientation):
                        return Relation.TOUCH
                elif (angle_orientation(edge_start, edge_end, start)
                      is angle_orientation(edge_end, next_end, start)
                      is border_orientation):
                    return Relation.TOUCH
            elif (angle_orientation(edge_start, edge_end, start)
                  is border_orientation):
                return Relation.TOUCH
            return Relation.ENCLOSED


def relate_multisegment(region: Region,
                        multisegment: Multisegment) -> Relation:
    return (_relate_multisegment(region, multisegment,
                                 bounding.box_from_iterables(multisegment))
            if multisegment
            else Relation.DISJOINT)


def _relate_multisegment(region: Region,
                         multisegment: Multisegment,
                         multisegment_bounding_box: bounding.Box
                         ) -> Relation:
    region_bounding_box = bounding.box_from_iterable(region)
    if bounding.box_disjoint_with(multisegment_bounding_box,
                                  region_bounding_box):
        return Relation.DISJOINT
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_segments(region),
                              from_test=False)
    sweeper.register_segments(multisegment,
                              from_test=True)
    (_, multisegment_max_x, _, _), (_, region_max_x, _, _) = (
        multisegment_bounding_box, region_bounding_box)
    return process_linear_compound_queue(sweeper, min(multisegment_max_x,
                                                      region_max_x))


def relate_contour(region: Region, contour: Contour) -> Relation:
    return _relate_contour(region, contour,
                           bounding.box_from_iterable(contour))


def _relate_contour(region: Region,
                    contour: Contour,
                    contour_bounding_box: bounding.Box
                    ) -> Relation:
    region_bounding_box = bounding.box_from_iterable(region)
    if bounding.box_disjoint_with(contour_bounding_box, region_bounding_box):
        return Relation.DISJOINT
    if equal(region, contour):
        return Relation.COMPONENT
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_segments(region),
                              from_test=False)
    sweeper.register_segments(contour_to_segments(contour),
                              from_test=True)
    (_, contour_max_x, _, _), (_, region_max_x, _, _) = (contour_bounding_box,
                                                         region_bounding_box)
    return process_linear_compound_queue(sweeper, min(contour_max_x,
                                                      region_max_x))


def relate_region(goal: Region, test: Region) -> Relation:
    return _relate_region(goal, test, bounding.box_from_iterable(goal),
                          bounding.box_from_iterable(test))


def _relate_region(goal: Region,
                   test: Region,
                   goal_bounding_box: bounding.Box,
                   test_bounding_box: bounding.Box) -> Relation:
    if bounding.box_disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    if equal(goal, test):
        return Relation.EQUAL
    sweeper = CompoundSweeper()
    sweeper.register_segments(to_oriented_segments(goal),
                              from_test=False)
    sweeper.register_segments(to_oriented_segments(test),
                              from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (goal_bounding_box,
                                                    test_bounding_box)
    return process_compound_queue(sweeper, min(goal_max_x, test_max_x))


equal = contours_equal
to_oriented_segments = contour_to_oriented_segments
