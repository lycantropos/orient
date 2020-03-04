from robust.linear import (SegmentsRelationship,
                           segments_intersection,
                           segments_relationship)

from orient.hints import (Contour,
                          Point,
                          Segment)
from .event import Event
from .events_queue import (EventsQueue,
                           EventsQueueKey)
from .sweep_line import SweepLine
from .utils import (contour_to_bounding_box,
                    contour_to_segments)


def sweep(left: Contour,
          right: Contour) -> bool:
    events_queue = EventsQueue()
    for segment in contour_to_segments(left):
        register_segment(segment, True, events_queue)
    for segment in contour_to_segments(right):
        register_segment(segment, False, events_queue)
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
                event.below_from_right_contour_in_out = event.from_left_contour
            else:
                compute_transition(below_event, event, events_queue)
            if above_event is not None:
                compute_transition(event, above_event, events_queue)
            if (event.from_left_contour
                    and event.below_from_right_contour_in_out):
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


def compute_transition(below_event: Event,
                       event: Event,
                       events_queue: EventsQueue) -> None:
    if detect_intersection(below_event, event, events_queue) == 2:
        if event.from_left_contour:
            event.below_from_right_contour_in_out = (
                below_event.below_from_right_contour_in_out)
        else:
            event.below_from_right_contour_in_out = (
                not below_event.below_from_right_contour_in_out)
    elif event.from_left_contour:
        event.below_from_right_contour_in_out = (
            below_event.below_from_right_contour_in_out)
    else:
        event.below_from_right_contour_in_out = (
            not below_event.below_from_right_contour_in_out)


def register_segment(segment: Segment,
                     from_left_contour: bool,
                     events_queue: EventsQueue) -> None:
    start, end = sorted(segment)
    start_event = Event(True, start, None, from_left_contour)
    end_event = Event(False, end, start_event, from_left_contour)
    start_event.complement = end_event
    events_queue.push(start_event)
    events_queue.push(end_event)


def detect_intersection(event: Event,
                        above_event: Event,
                        events_queue: EventsQueue) -> int:
    segment, above_segment = event.segment, above_event.segment
    relationship = segments_relationship(segment, above_segment)
    if relationship is SegmentsRelationship.NONE:
        # no intersection
        return 0
    elif relationship is SegmentsRelationship.CROSS:
        # segments intersect
        if (event.start == above_event.start
                or event.end == above_event.end):
            # segments intersect at an endpoint of both line segments
            return 0
        point = segments_intersection(segment, above_segment)
        if event.start != point and event.end != point:
            divide_segment(event, point, events_queue)
        if above_event.start != point and above_event.end != point:
            divide_segment(above_event, point, events_queue)
        return 1
    # segments overlap
    if event.from_left_contour is above_event.from_left_contour:
        raise ValueError('Edges of the same polygon should not overlap.')

    sorted_events = []
    starts_equal = event.start == above_event.start
    if starts_equal:
        sorted_events.append(None)
    elif EventsQueueKey(event) > EventsQueueKey(above_event):
        sorted_events.append(above_event)
        sorted_events.append(event)
    else:
        sorted_events.append(event)
        sorted_events.append(above_event)

    ends_equal = event.end == above_event.end
    if ends_equal:
        sorted_events.append(None)
    elif (EventsQueueKey(event.complement)
          > EventsQueueKey(above_event.complement)):
        sorted_events.append(above_event.complement)
        sorted_events.append(event.complement)
    else:
        sorted_events.append(event.complement)
        sorted_events.append(above_event.complement)

    if starts_equal:
        # both line segments are equal or share the left endpoint
        if not ends_equal:
            divide_segment(sorted_events[2].complement, sorted_events[1].start,
                           events_queue)
        return 2
    elif ends_equal:
        # the line segments share the right endpoint
        divide_segment(sorted_events[0], sorted_events[1].start, events_queue)
        return 3
    else:
        divide_segment(sorted_events[0]
                       # one line segment includes the other one
                       if sorted_events[0] is sorted_events[3].complement
                       # no line segment includes the other one
                       else sorted_events[1],
                       sorted_events[2].start,
                       events_queue)
        divide_segment(sorted_events[0], sorted_events[1].start, events_queue)
        return 3


def divide_segment(event: Event,
                   point: Point,
                   events_queue: EventsQueue) -> None:
    left_event = Event(True, point, event.complement, event.from_left_contour)
    right_event = Event(False, point, event, event.from_left_contour)
    event.complement.complement, event.complement = left_event, right_event
    events_queue.push(left_event)
    events_queue.push(right_event)


def bounding_box_in_bounding_box(left: Contour, right: Contour) -> bool:
    ((left_x_min, left_x_max, left_y_min, left_y_max),
     (right_x_min, right_x_max, right_y_min, right_y_max)) = (
        contour_to_bounding_box(left), contour_to_bounding_box(right))
    return (right_x_min <= left_x_min and left_x_max <= right_x_max
            and right_y_min <= left_y_min and left_y_max <= right_y_max)
