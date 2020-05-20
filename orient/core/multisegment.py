from robust.linear import segments_intersection

from orient.hints import (Multisegment,
                          Point,
                          Segment)
from . import bounding_box
from .events_queue import EventsQueue
from .processing import process_linear_queue
from .relation import Relation
from .segment import (relate_point as relate_point_to_segment,
                      relate_segment as relate_segments)
from .utils import flatten


def relate_point(multisegment: Multisegment, point: Point) -> Relation:
    return (Relation.DISJOINT
            if all(relate_point_to_segment(segment, point) is Relation.DISJOINT
                   for segment in multisegment)
            else Relation.COMPONENT)


def relate_segment(multisegment: Multisegment, segment: Segment) -> Relation:
    all_components = has_no_touch = has_no_cross = has_no_overlap = True
    non_endpoints_touch_points = set()
    components = []
    start, end = segment
    if start > end:
        start, end = end, start
    for index, sub_segment in enumerate(multisegment):
        relation_with_edge = relate_segments(sub_segment, segment)
        if relation_with_edge is Relation.COMPONENT:
            return Relation.COMPONENT
        elif relation_with_edge is Relation.EQUAL:
            return (Relation.EQUAL
                    if all_components and index == len(multisegment) - 1
                    else Relation.COMPONENT)
        elif relation_with_edge is Relation.COMPOSITE:
            if has_no_overlap:
                has_no_overlap = False
            if start in sub_segment:
                start = max(sub_segment)
                segment = start, end
            elif end in sub_segment:
                end = min(sub_segment)
                segment = start, end
            else:
                components.append(sort_endpoints(sub_segment))
        elif relation_with_edge is Relation.OVERLAP:
            if all_components:
                all_components = False
            if has_no_overlap:
                has_no_overlap = False
            start, end = segment = _subtract_segments_overlap(segment,
                                                              sub_segment)
        else:
            if all_components:
                all_components = False
            if has_no_overlap:
                if relation_with_edge is Relation.TOUCH:
                    if has_no_touch:
                        has_no_touch = False
                    if has_no_cross:
                        intersection = segments_intersection(sub_segment,
                                                             segment)
                        if intersection != start and intersection != end:
                            if intersection in non_endpoints_touch_points:
                                has_no_cross = False
                            else:
                                non_endpoints_touch_points.add(intersection)
                elif has_no_cross and relation_with_edge is Relation.CROSS:
                    has_no_cross = False
    if has_no_overlap:
        return (Relation.DISJOINT
                if has_no_touch and has_no_cross
                else (Relation.TOUCH
                      if has_no_cross
                      else Relation.CROSS))
    elif components:
        components_iterator = iter(components)
        min_component_start, max_component_end = next(components_iterator)
        components_starts = {min_component_start}
        for component_start, component_end in components_iterator:
            components_starts.add(component_start)
            if min_component_start > component_start:
                min_component_start = component_start
            if max_component_end < component_end:
                max_component_end = component_end
        return ((Relation.EQUAL
                 if all_components
                 else Relation.COMPONENT)
                if (min_component_start == start
                    and max_component_end == end
                    and all(component_end in components_starts
                            or component_end == max_component_end
                            for _, component_end in components))
                else (Relation.COMPOSITE
                      if all_components
                      else Relation.OVERLAP))
    else:
        return (Relation.COMPOSITE
                if all_components
                else Relation.OVERLAP)


def _subtract_segments_overlap(minuend: Segment,
                               subtrahend: Segment) -> Segment:
    left_start, left_end, right_start, right_end = sorted(minuend + subtrahend)
    return ((left_start, left_end)
            if left_start in minuend
            else (right_start, right_end))


def sort_endpoints(segment: Segment) -> Segment:
    start, end = segment
    return (segment
            if start < end
            else (end, start))


def relate_multisegment(goal: Multisegment, test: Multisegment) -> Relation:
    if not (goal and test):
        return Relation.DISJOINT
    goal_bounding_box, test_bounding_box = (
        bounding_box.from_points(flatten(goal)),
        bounding_box.from_points(flatten(test)))
    if bounding_box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test=False)
    register(events_queue, test,
             from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (goal_bounding_box,
                                                    test_bounding_box)
    return process_linear_queue(events_queue, min(goal_max_x, test_max_x))


def register(events_queue: EventsQueue, multisegment: Multisegment,
             *,
             from_test: bool) -> None:
    for segment in multisegment:
        events_queue.register_segment(segment,
                                      from_test=from_test)
