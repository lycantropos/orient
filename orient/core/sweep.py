from itertools import groupby
from typing import (Any,
                    Iterable,
                    Optional)

from robust.linear import (SegmentsRelationship,
                           segments_intersection,
                           segments_relationship)

from orient.hints import Coordinate
from .event import (EdgeKind,
                    Event)
from .events_queue import (EventsQueue,
                           EventsQueueKey)
from .sweep_line import SweepLine


def sweep(events_queue: EventsQueue,
          stop_x: Coordinate) -> Iterable[Event]:
    sweep_line = SweepLine()
    while events_queue:
        event = events_queue.peek()
        start = event.start
        start_x, _ = start
        if start_x > stop_x:
            # no intersection segments left
            return
        events_queue.pop()
        sweep_line.move_to(start_x)
        same_start_events = [event]
        while events_queue and events_queue.peek().start == start:
            same_start_events.append(events_queue.pop())
        if not all_equal(event.from_test
                         for event in same_start_events):
            for event in same_start_events:
                event.set_both_relationships(max(event.relationship,
                                                 SegmentsRelationship.TOUCH))
        for event in same_start_events:
            if event.is_left_endpoint:
                sweep_line.add(event)
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                compute_transition(below_event, event)
                if (above_event is not None
                        and detect_intersection(event, above_event,
                                                events_queue)):
                    compute_transition(below_event, event)
                    compute_transition(event, above_event)
                if (below_event is not None
                        and detect_intersection(below_event, event,
                                                events_queue)):
                    below_below_event = sweep_line.below(below_event)
                    compute_transition(below_below_event, below_event)
                    compute_transition(below_event, event)
            else:
                event = event.complement
                if event in sweep_line:
                    above_event, below_event = (sweep_line.above(event),
                                                sweep_line.below(event))
                    sweep_line.remove(event)
                    if above_event is not None and below_event is not None:
                        detect_intersection(below_event, above_event,
                                            events_queue)
                yield event


def all_equal(values: Iterable[Any]) -> bool:
    groups = groupby(values)
    return next(groups, True) and not next(groups, False)


def compute_transition(below_event: Optional[Event], event: Event) -> None:
    if below_event is None:
        event.in_out, event.other_in_out = False, True
    elif event.from_test is below_event.from_test:
        event.in_out, event.other_in_out = (not below_event.in_out,
                                            below_event.other_in_out)
    else:
        event.in_out, event.other_in_out = (not below_event.other_in_out,
                                            below_event.in_out)


def detect_intersection(below_event: Event,
                        event: Event,
                        events_queue: EventsQueue) -> bool:
    """
    Populates events queue with intersection events.
    Checks if events' segments overlap and have the same start.
    """
    below_segment, segment = below_event.segment, event.segment
    relationship = segments_relationship(below_segment, segment)
    if relationship is SegmentsRelationship.OVERLAP:
        # segments overlap
        if event.from_test is below_event.from_test:
            raise ValueError('Segments of the same object '
                             'should not overlap.')

        starts_equal = event.start == below_event.start
        if starts_equal:
            start_min = start_max = None
        elif EventsQueueKey(event) < EventsQueueKey(below_event):
            start_min, start_max = event, below_event
        else:
            start_min, start_max = below_event, event

        ends_equal = event.end == below_event.end
        if ends_equal:
            end_min = end_max = None
        elif (EventsQueueKey(event.complement)
              < EventsQueueKey(below_event.complement)):
            end_min, end_max = event.complement, below_event.complement
        else:
            end_min, end_max = below_event.complement, event.complement

        if starts_equal:
            # both line segments are equal or share the left endpoint
            below_event.edge_kind = EdgeKind.NON_CONTRIBUTING
            event.edge_kind = (EdgeKind.SAME_TRANSITION
                               if event.in_out is below_event.in_out
                               else EdgeKind.DIFFERENT_TRANSITION)
            if ends_equal:
                event.set_both_relationships(relationship)
                below_event.set_both_relationships(relationship)
            else:
                end_min.set_both_relationships(relationship)
                end_max.complement.relationship = relationship
                events_queue.divide_segment(end_max.complement, end_min.start)
            assert event.segment == below_event.segment
            assert (segments_relationship(event.segment, below_event.segment)
                    is SegmentsRelationship.OVERLAP)
            return True
        elif ends_equal:
            # the line segments share the right endpoint
            start_max.set_both_relationships(relationship)
            start_min.complement.relationship = relationship
            events_queue.divide_segment(start_min, start_max.start)
        elif start_min is end_max.complement:
            # one line segment includes the other one
            start_max.set_both_relationships(relationship)
            start_min_original_relationship = start_min.relationship
            start_min.relationship = relationship
            events_queue.divide_segment(start_min, end_min.start)
            start_min.relationship = start_min_original_relationship
            start_min.complement.relationship = relationship
            events_queue.divide_segment(start_min, start_max.start)
            assert start_max.segment == max(segment, below_segment)
            assert (segments_relationship(event.segment, below_event.segment)
                    is SegmentsRelationship.TOUCH)
        else:
            # no line segment includes the other one
            start_max.relationship = relationship
            events_queue.divide_segment(start_max, end_min.start)
            start_min.complement.relationship = relationship
            events_queue.divide_segment(start_min, start_max.start)
    elif relationship is not SegmentsRelationship.NONE:
        if event.from_test is not below_event.from_test:
            event.set_both_relationships(max(event.relationship, relationship))
            below_event.set_both_relationships(max(below_event.relationship,
                                                   relationship))
        if below_event.start != event.start and below_event.end != event.end:
            # segments do not intersect at endpoints
            point = segments_intersection(below_segment, segment)
            if point != below_event.start and point != below_event.end:
                events_queue.divide_segment(below_event, point)
            if point != event.start and point != event.end:
                events_queue.divide_segment(event, point)
    return False
