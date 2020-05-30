from typing import Dict

from robust.angular import (Orientation,
                            orientation)
from robust.linear import segments_intersection

from orient.hints import (Multisegment,
                          Point,
                          Segment)
from . import bounding_box
from .processing import process_open_linear_queue
from .relation import Relation
from .segment import (relate_point as relate_point_to_segment,
                      relate_segment as relate_segments)
from .sweep import OpenSweeper
from .utils import flatten


def relate_point(multisegment: Multisegment, point: Point) -> Relation:
    return (Relation.DISJOINT
            if all(relate_point_to_segment(segment, point) is Relation.DISJOINT
                   for segment in multisegment)
            else Relation.COMPONENT)


def relate_segment(multisegment: Multisegment, segment: Segment) -> Relation:
    all_components = has_no_touch = has_no_cross = has_no_overlap = True
    # orientations of multisegment's segments
    # which touch given segment in the middle
    middle_touching_orientations = {}  # type: Dict[Point, Orientation]
    components = []
    start, end = segment
    if start > end:
        start, end = end, start
    for index, sub_segment in enumerate(multisegment):
        relation = relate_segments(sub_segment, segment)
        if relation is Relation.COMPONENT:
            return Relation.COMPONENT
        elif relation is Relation.EQUAL:
            return (Relation.EQUAL
                    if all_components and index == len(multisegment) - 1
                    else Relation.COMPONENT)
        elif relation is Relation.COMPOSITE:
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
        elif relation is Relation.OVERLAP:
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
                if relation is Relation.TOUCH:
                    if has_no_touch:
                        has_no_touch = False
                    if has_no_cross:
                        intersection = segments_intersection(sub_segment,
                                                             segment)
                        if intersection != start and intersection != end:
                            sub_start, sub_end = sub_segment
                            non_touched_endpoint = (sub_start
                                                    if intersection == sub_end
                                                    else sub_end)
                            try:
                                previous_orientation = (
                                    middle_touching_orientations[intersection])
                            except KeyError:
                                middle_touching_orientations[intersection] = (
                                    orientation(end, start,
                                                non_touched_endpoint))
                            else:
                                if (orientation(end, start,
                                                non_touched_endpoint)
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
    goal_bounding_box, test_bounding_box = (bounding_box.from_iterables(goal),
                                            bounding_box.from_iterables(test))
    if bounding_box.disjoint_with(goal_bounding_box, test_bounding_box):
        return Relation.DISJOINT
    sweeper = OpenSweeper()
    sweeper.register_segments(goal,
                              from_test=False)
    sweeper.register_segments(test,
                              from_test=True)
    (_, goal_max_x, _, _), (_, test_max_x, _, _) = (goal_bounding_box,
                                                    test_bounding_box)
    return process_open_linear_queue(sweeper, min(goal_max_x, test_max_x))
