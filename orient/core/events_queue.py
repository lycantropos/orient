from functools import partial
from typing import (Callable,
                    cast)

from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .angular import (Orientation,
                      to_orientation)
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
            other_end_orientation = to_orientation(event.start,
                                                   other_event.end,
                                                   event.end)
            # the lowest segment is processed first
            if other_end_orientation is not Orientation.COLLINEAR:
                return other_end_orientation is Orientation.COUNTERCLOCKWISE
            elif event.from_left_contour is not other_event.from_left_contour:
                return not event.from_left_contour
            else:
                end_x, end_y = event.end
                other_end_x, other_end_y = other_event.end
                return end_y < other_end_y


EventsQueue = cast(Callable[[], PriorityQueue[Event]],
                   partial(PriorityQueue[Event],
                           key=EventsQueueKey))
