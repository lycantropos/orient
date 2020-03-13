from prioq.base import PriorityQueue
from reprit.base import generate_repr
from robust.angular import (Orientation,
                            orientation)

from orient.hints import (Point,
                          Segment)
from .event import Event


class EventsQueueKey:
    __slots__ = ('event',)

    def __init__(self, event: Event) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'EventsQueueKey') -> bool:
        if not isinstance(other, EventsQueueKey):
            return NotImplemented
        event, other_event = self.event, other.event
        start_x, start_y = event.start
        other_start_x, other_start_y = other_event.start
        if start_x != other_start_x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return start_x < other_start_x
        elif start_y != other_start_y:
            # different points, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return start_y < other_start_y
        elif event.is_left_endpoint is not other_event.is_left_endpoint:
            # same start, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return not event.is_left_endpoint
        # same start, both events are left endpoints
        # or both are right endpoints
        else:
            other_end_orientation = orientation(event.start,
                                                other_event.end,
                                                event.end)
            # the lowest segment is processed first
            if other_end_orientation is not Orientation.COLLINEAR:
                return other_end_orientation is Orientation.COUNTERCLOCKWISE
            elif event.from_test_contour is not other_event.from_test_contour:
                return not event.from_test_contour
            else:
                end_x, end_y = event.end
                other_end_x, other_end_y = other_event.end
                return end_y < other_end_y


class EventsQueue:
    __slots__ = ('_queue',)

    def __init__(self) -> None:
        self._queue = PriorityQueue(key=EventsQueueKey)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def pop(self) -> Event:
        return self._queue.pop()

    def register_segment(self, segment: Segment,
                         *,
                         from_test_contour: bool) -> None:
        start, end = sorted(segment)
        start_event = Event(True, start, None, from_test_contour)
        end_event = Event(False, end, start_event, from_test_contour)
        start_event.complement = end_event
        self._queue.push(start_event)
        self._queue.push(end_event)

    def divide_segment(self, event: Event, point: Point) -> None:
        left_event = Event(True, point, event.complement,
                           event.from_test_contour)
        right_event = Event(False, point, event, event.from_test_contour)
        event.complement.complement, event.complement = left_event, right_event
        self._queue.push(left_event)
        self._queue.push(right_event)
