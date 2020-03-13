from robust.linear import (SegmentsRelationship,
                           segments_intersection,
                           segments_relationship)

from .event import Event
from .events_queue import (EventsQueue,
                           EventsQueueKey)
from .sweep_line import SweepLine


def sweep(events_queue: EventsQueue) -> bool:
    sweep_line = SweepLine()
    while events_queue:
        event = events_queue.pop()
        start_x, _ = event.start
        sweep_line.move_to(start_x)
        if event.is_left_endpoint:
            sweep_line.add(event)
            above_event, below_event = (sweep_line.above(event),
                                        sweep_line.below(event))
            if below_event is None:
                event.below_from_goal_contour_in_out = event.from_test_contour
            else:
                possible_intersection(below_event, event, events_queue)
            if above_event is not None:
                possible_intersection(event, above_event, events_queue)
            if (event.from_test_contour
                    and event.below_from_goal_contour_in_out):
                return False
        else:
            event = event.complement
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    detect_intersection(below_event, above_event, events_queue)
    return True


def possible_intersection(below_event: Event,
                          event: Event,
                          events_queue: EventsQueue) -> None:
    detect_intersection(below_event, event, events_queue)
    compute_transition(below_event, event)


def compute_transition(below_event: Event, event: Event) -> None:
    event.below_from_goal_contour_in_out = (
        below_event.below_from_goal_contour_in_out
        if event.from_test_contour
        else not below_event.below_from_goal_contour_in_out)


def detect_intersection(below_event: Event,
                        event: Event,
                        events_queue: EventsQueue) -> None:
    below_segment, segment = below_event.segment, event.segment
    relationship = segments_relationship(below_segment, segment)
    if relationship is SegmentsRelationship.NONE:
        # no intersection
        return
    elif relationship is SegmentsRelationship.OVERLAP:
        # segments overlap
        if below_event.from_test_contour is event.from_test_contour:
            raise ValueError('Edges of the same polygon should not overlap.')

        sorted_events = []
        starts_equal = event.start == below_event.start
        if starts_equal:
            sorted_events.append(None)
        elif EventsQueueKey(below_event) > EventsQueueKey(event):
            sorted_events.append(event)
            sorted_events.append(below_event)
        else:
            sorted_events.append(below_event)
            sorted_events.append(event)

        ends_equal = event.end == below_event.end
        if ends_equal:
            sorted_events.append(None)
        elif (EventsQueueKey(below_event.complement)
              > EventsQueueKey(event.complement)):
            sorted_events.append(event.complement)
            sorted_events.append(below_event.complement)
        else:
            sorted_events.append(below_event.complement)
            sorted_events.append(event.complement)

        if starts_equal:
            # both line segments are equal or share the left endpoint
            if not ends_equal:
                events_queue.divide_segment(sorted_events[2].complement,
                                            sorted_events[1].start)
        elif ends_equal:
            # the line segments share the right endpoint
            events_queue.divide_segment(sorted_events[0],
                                        sorted_events[1].start)
        else:
            events_queue.divide_segment(
                    sorted_events[0]
                    # one line segment includes the other one
                    if sorted_events[0] is sorted_events[3].complement
                    # no line segment includes the other one
                    else sorted_events[1],
                    sorted_events[2].start)
            events_queue.divide_segment(sorted_events[0],
                                        sorted_events[1].start)
    else:
        # segments intersect
        if event.start == below_event.start or event.end == below_event.end:
            # segments intersect at an endpoint of both line segments
            return
        point = segments_intersection(below_segment, segment)
        if point != below_event.start and point != below_event.end:
            events_queue.divide_segment(below_event, point)
        if point != event.start and point != event.end:
            events_queue.divide_segment(event, point)
