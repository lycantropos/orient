from itertools import chain

from robust.angular import (Orientation,
                            orientation as angle_orientation)
from robust.linear import (SegmentsRelationship,
                           segments_relationship)

from orient.hints import (Contour,
                          Point,
                          Region,
                          Segment)
from . import bounding_box
from .contour import (equal as contours_equal,
                      relate_segment as relate_segment_to_contour,
                      to_segments as contour_to_segments)
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .relation import Relation
from .segment import relate_point as relate_point_to_segment
from .sweep import ClosedSweeper
from .utils import flatten


def relate_point(region: Region, point: Point) -> Relation:
    result = False
    _, point_y = point
    for edge in to_segments(region):
        if relate_point_to_segment(edge, point) is Relation.COMPONENT:
            return Relation.COMPONENT
        start, end = edge
        (_, start_y), (_, end_y) = start, end
        if ((start_y > point_y) is not (end_y > point_y)
                and ((end_y > start_y) is (angle_orientation(end, start, point)
                                           is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return (Relation.WITHIN
            if result
            else Relation.DISJOINT)


def relate_segment(region: Region, segment: Segment) -> Relation:
    relation_with_contour = relate_segment_to_contour(region, segment)
    if (relation_with_contour is Relation.CROSS
            or relation_with_contour is Relation.COMPONENT):
        return relation_with_contour
    start, end = segment
    start_relation = relate_point(region, start)
    if relation_with_contour is Relation.DISJOINT:
        return (Relation.DISJOINT
                if start_relation is Relation.DISJOINT
                else Relation.WITHIN)
    elif start_relation is Relation.DISJOINT:
        return Relation.TOUCH
    elif start_relation is Relation.WITHIN:
        return Relation.ENCLOSED
    else:
        end_relation = relate_point(region, end)
        if end_relation is Relation.DISJOINT:
            return Relation.TOUCH
        elif end_relation is Relation.WITHIN:
            return Relation.ENCLOSED
        else:
            start_index = end_index = None
            start_is_not_vertex = end_is_not_vertex = True
            overlaps_with_edges = relation_with_contour is Relation.OVERLAP
            for index, edge in enumerate(to_segments(region)):
                if (start_index is None
                        and (relate_point_to_segment(edge, start)
                             is Relation.COMPONENT)):
                    start_index = index
                    edge_start, edge_end = edge
                    if overlaps_with_edges:
                        if (segments_relationship(segment, edge)
                                is SegmentsRelationship.OVERLAP):
                            start = (max if start < end else min)(edge_start,
                                                                  edge_end)
                        elif (start == edge_start
                              and (segments_relationship(
                                        segment,
                                        (region[index - 2], edge_start))
                                   is SegmentsRelationship.OVERLAP)):
                            edge_start, edge_end = (region[index - 2],
                                                    edge_start)
                            start_index = (start_index - 1) % len(region)
                            start = (max if start < end else min)(edge_start,
                                                                  edge_end)
                        elif (start == edge_end
                              and (segments_relationship(
                                        segment,
                                        (edge_end,
                                         region[(index + 1) % len(region)]))
                                   is SegmentsRelationship.OVERLAP)):
                            edge_start, edge_end = (
                                edge_end, region[(index + 1) % len(region)])
                            start_index = (start_index + 1) % len(region)
                            start = (max if start < end else min)(edge_start,
                                                                  edge_end)
                    if start == edge_start:
                        start_is_not_vertex = False
                    elif start == edge_end:
                        start_index += 1
                        start_is_not_vertex = False
                if (end_index is None
                        and (relate_point_to_segment(edge, end)
                             is Relation.COMPONENT)):
                    end_index = index
                    edge_start, edge_end = edge
                    if overlaps_with_edges:
                        if (segments_relationship(segment, edge)
                                is SegmentsRelationship.OVERLAP):
                            end = (max if end < start else min)(edge_start,
                                                                edge_end)
                        elif (end == edge_start
                              and (segments_relationship(
                                        segment,
                                        (region[index - 2], edge_start))
                                   is SegmentsRelationship.OVERLAP)):
                            edge_start, edge_end = (region[index - 2],
                                                    edge_start)
                            end_index = (end_index - 1) % len(region)
                            end = (max if end < start else min)(edge_start,
                                                                edge_end)
                        elif (end == edge_end
                              and (segments_relationship(
                                        segment,
                                        (edge_end,
                                         region[(index + 1) % len(region)]))
                                   is SegmentsRelationship.OVERLAP)):
                            edge_start, edge_end = (
                                edge_end, region[(index + 1) % len(region)])
                            end_index = (end_index + 1) % len(region)
                            end = (max if end < start else min)(edge_start,
                                                                edge_end)
                    if end == edge_start:
                        end_is_not_vertex = False
                    elif end == edge_end:
                        end_index += 1
                        end_is_not_vertex = False
                if start_index is not None and end_index is not None:
                    break
            start_index = (start_index - 1) % len(region)
            end_index = (end_index - 1) % len(region)
            if start_index > end_index:
                start, end = end, start
                start_index, end_index = end_index, start_index
                start_is_not_vertex, end_is_not_vertex = (end_is_not_vertex,
                                                          start_is_not_vertex)
            first_part_min_index, second_part_min_index = (
                min(chain(range(start_index + start_is_not_vertex),
                          range(end_index + 1, len(region))),
                    key=region.__getitem__),
                min(range(start_index + 1,
                          end_index + end_is_not_vertex),
                    key=region.__getitem__))
            first_part_min_vertex, second_part_min_vertex = (
                region[first_part_min_index], region[second_part_min_index])
            if first_part_min_vertex > start:
                if start > end:
                    first_part_orientation = angle_orientation(
                            end, start, region[(end_index + 1) % len(region)])
                else:
                    first_part_orientation = angle_orientation(
                            start,
                            region[start_index + start_is_not_vertex - 1], end)
            elif first_part_min_vertex > end:
                first_part_orientation = angle_orientation(
                        end, start, region[(end_index + 1) % len(region)])
            elif first_part_min_index + 1 == start_index + start_is_not_vertex:
                first_part_orientation = angle_orientation(
                        first_part_min_vertex,
                        region[first_part_min_index - 1], start)
            elif first_part_min_index == (end_index + 1) % len(region):
                first_part_orientation = angle_orientation(
                        first_part_min_vertex,
                        end, region[(first_part_min_index + 1) % len(region)])
            else:
                first_part_orientation = angle_orientation(
                        first_part_min_vertex,
                        region[first_part_min_index - 1],
                        region[(first_part_min_index + 1) % len(region)])
            if second_part_min_vertex > start:
                if start > end:
                    second_part_orientation = angle_orientation(
                            end, region[end_index + end_is_not_vertex - 1],
                            start)
                else:
                    second_part_orientation = angle_orientation(
                            start, end, region[start_index + 1])
            elif second_part_min_vertex > end:
                second_part_orientation = angle_orientation(
                        end, region[end_index + end_is_not_vertex - 1], start)
            elif second_part_min_index == start_index + 1:
                second_part_orientation = angle_orientation(
                        second_part_min_vertex, start,
                        region[second_part_min_index + 1]
                        if second_part_min_index + 1 < len(region)
                        else end)
            elif second_part_min_index + 1 == end_index + end_is_not_vertex:
                second_part_orientation = angle_orientation(
                        second_part_min_vertex,
                        region[second_part_min_index - 1], end)
            else:
                second_part_orientation = angle_orientation(
                        second_part_min_vertex,
                        region[second_part_min_index - 1],
                        region[second_part_min_index + 1])
            return (Relation.ENCLOSED
                    if first_part_orientation is second_part_orientation
                    else Relation.TOUCH)


def relate_multisegment(region: Region, multisegment: Contour) -> Relation:
    if not multisegment:
        return Relation.DISJOINT
    multisegment_bounding_box, region_bounding_box = (
        bounding_box.from_points(flatten(multisegment)),
        bounding_box.from_points(region))
    if bounding_box.disjoint_with(multisegment_bounding_box,
                                  region_bounding_box):
        return Relation.DISJOINT
    sweeper = ClosedSweeper()
    sweeper.register_segments(to_segments(region),
                              from_test=False)
    sweeper.register_segments(multisegment,
                              from_test=True)
    (_, multisegment_max_x, _, _), (_, region_max_x, _, _) = (
        multisegment_bounding_box, region_bounding_box)
    return process_linear_compound_queue(sweeper, min(multisegment_max_x,
                                                      region_max_x))


def relate_contour(region: Region, contour: Contour) -> Relation:
    contour_bounding_box, region_bounding_box = (
        bounding_box.from_points(contour), bounding_box.from_points(region))
    if bounding_box.disjoint_with(contour_bounding_box, region_bounding_box):
        return Relation.DISJOINT
    if equal(region, contour):
        return Relation.COMPONENT
    sweeper = ClosedSweeper()
    sweeper.register_segments(to_segments(region),
                              from_test=False)
    sweeper.register_segments(contour_to_segments(contour),
                              from_test=True)
    (_, contour_max_x, _, _), (_, region_max_x, _, _) = (contour_bounding_box,
                                                         region_bounding_box)
    return process_linear_compound_queue(sweeper, min(contour_max_x,
                                                      region_max_x))


def relate_region(goal: Region, test: Region) -> Relation:
    goal_bounding_box, test_bounding_box = (bounding_box.from_points(goal),
                                            bounding_box.from_points(test))
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
    return process_compound_queue(sweeper, min(goal_max_x, test_max_x))


equal = contours_equal
to_segments = contour_to_segments
