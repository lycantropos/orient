from typing import (Dict,
                    Iterable)

from ground.base import (Context,
                         Orientation,
                         Relation)
from ground.hints import (Multisegment,
                          Point,
                          Segment)

from . import box
from .events_queue import LinearEventsQueue
from .hints import SegmentEndpoints
from .processing import process_open_linear_queue
from .segment import (_relate_segment as relate_segments,
                      relate_point as relate_point_to_segment)
from .utils import to_sorted_pair


def relate_point(multisegment: Multisegment, point: Point,
                 *,
                 context: Context) -> Relation:
    return (Relation.DISJOINT
            if all(relate_point_to_segment(segment, point,
                                           context=context)
                   is Relation.DISJOINT
                   for segment in multisegment.segments)
            else Relation.COMPONENT)


def relate_segment(multisegment: Multisegment, segment: Segment,
                   *,
                   context: Context) -> Relation:
    all_components = has_no_touch = has_no_cross = has_no_overlap = True
    # orientations of multisegment's segments
    # which touch given segment in the middle
    middle_touching_orientations = {}  # type: Dict[Point, Orientation]
    components = []
    start, end = segment_endpoints = segment.start, segment.end
    if start > end:
        start, end = end, start
    for index, sub_segment in enumerate(multisegment.segments):
        sub_segment_start, sub_segment_end = sub_segment_endpoints = (
            sub_segment.start, sub_segment.end)
        relation = relate_segments(sub_segment_start, sub_segment_end, start,
                                   end,
                                   context=context)
        if relation is Relation.COMPONENT:
            return Relation.COMPONENT
        elif relation is Relation.EQUAL:
            return (Relation.EQUAL
                    if (all_components
                        and index == len(multisegment.segments) - 1)
                    else Relation.COMPONENT)
        elif relation is Relation.COMPOSITE:
            if has_no_overlap:
                has_no_overlap = False
            if start in sub_segment_endpoints:
                start = max(sub_segment_endpoints)
                segment_endpoints = start, end
            elif end in sub_segment_endpoints:
                end = min(sub_segment_endpoints)
                segment_endpoints = start, end
            else:
                components.append(to_sorted_pair(sub_segment_endpoints))
        elif relation is Relation.OVERLAP:
            if all_components:
                all_components = False
            if has_no_overlap:
                has_no_overlap = False
            start, end = segment_endpoints = _subtract_segments_overlap(
                    segment_endpoints, sub_segment_endpoints)
        else:
            if all_components:
                all_components = False
            if has_no_overlap:
                if relation is Relation.TOUCH:
                    if has_no_touch:
                        has_no_touch = False
                    if has_no_cross:
                        intersection = context.segments_intersection(
                                sub_segment_start, sub_segment_end, start, end)
                        if intersection != start and intersection != end:
                            sub_start, sub_end = sub_segment_endpoints
                            non_touched_endpoint = (sub_start
                                                    if intersection == sub_end
                                                    else sub_end)
                            try:
                                previous_orientation = (
                                    middle_touching_orientations[intersection])
                            except KeyError:
                                middle_touching_orientations[intersection] = (
                                    context.angle_orientation(
                                            start, end, non_touched_endpoint))
                            else:
                                if (context.angle_orientation(
                                        start, end, non_touched_endpoint)
                                        is not previous_orientation):
                                    has_no_cross = False
                elif has_no_cross and relation is Relation.CROSS:
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


def _subtract_segments_overlap(minuend: SegmentEndpoints,
                               subtrahend: SegmentEndpoints
                               ) -> SegmentEndpoints:
    left_start, left_end, right_start, right_end = sorted(minuend + subtrahend)
    return ((left_start, left_end)
            if left_start in minuend
            else (right_start, right_end))


def relate_multisegment(goal: Multisegment, test: Multisegment,
                        *,
                        context: Context) -> Relation:
    if not (goal.segments and test.segments):
        return Relation.DISJOINT
    goal_bounding_box, test_bounding_box = (
        box.from_multisegment(goal,
                              context=context),
        box.from_multisegment(test,
                              context=context))
    if box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    events_queue = LinearEventsQueue(context)
    events_queue.register(to_segments_endpoints(goal),
                          from_test=False)
    events_queue.register(to_segments_endpoints(test),
                          from_test=True)
    return process_open_linear_queue(events_queue,
                                     min(goal_bounding_box.max_x,
                                         test_bounding_box.max_x))


def to_segments_endpoints(multisegment: Multisegment
                          ) -> Iterable[SegmentEndpoints]:
    return ((segment.start, segment.end) for segment in multisegment.segments)
