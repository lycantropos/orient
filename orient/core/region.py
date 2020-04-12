from robust.angular import (Orientation,
                            orientation as angle_orientation)

from orient.hints import (Contour,
                          Point,
                          Region,
                          Segment)
from . import bounding_box
from .contour import (_relate_segment as relate_segment_to_contour,
                      edges as boundary_edges,
                      equal as contours_equal,
                      register as register_contour)
from .events_queue import EventsQueue
from .processing import (process_compound_queue,
                         process_linear_compound_queue)
from .relation import Relation
from .segment import relate_point as relate_point_to_segment


def relate_point(region: Region, point: Point) -> Relation:
    if not bounding_box.contains_point(bounding_box.from_points(region),
                                       point):
        return Relation.DISJOINT
    result = False
    _, point_y = point
    for edge in boundary_edges(region):
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
    if bounding_box.disjoint_with(bounding_box.from_points(region),
                                  bounding_box.from_points(segment)):
        return Relation.DISJOINT
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
    else:
        return (Relation.TOUCH
                if (start_relation is Relation.DISJOINT
                    or relate_point(region, end) is Relation.DISJOINT)
                else Relation.ENCLOSED)


def relate_contour(region: Region, contour: Contour) -> Relation:
    test_bounding_box = bounding_box.from_points(contour)
    if bounding_box.disjoint_with(bounding_box.from_points(region),
                                  test_bounding_box):
        return Relation.DISJOINT
    if equal(region, contour):
        return Relation.COMPONENT
    events_queue = EventsQueue()
    register(events_queue, region,
             from_test=False)
    register_contour(events_queue, contour,
                     from_test=True)
    _, test_max_x, _, _ = test_bounding_box
    return process_linear_compound_queue(events_queue, test_max_x)


def relate_region(goal: Region, test: Region) -> Relation:
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
    return process_compound_queue(events_queue, test_max_x)


equal = contours_equal
register = register_contour
