from functools import partial
from typing import (Generic,
                    Optional,
                    TypeVar)

from dendroid import red_black
from ground.base import (Context,
                         Orientation)
from reprit.base import generate_repr

from .event import LeftEvent
from .hints import Orienteer

Event = TypeVar('Event',
                bound=LeftEvent)


class SweepLine(Generic[Event]):
    __slots__ = 'context', '_set'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._set = red_black.set_(key=partial(SweepLineKey,
                                               context.angle_orientation))

    __repr__ = generate_repr(__init__)

    def __contains__(self, event: Event) -> bool:
        return event in self._set

    def add(self, event: Event) -> None:
        self._set.add(event)

    def remove(self, event: Event) -> None:
        self._set.remove(event)

    def above(self, event: Event) -> Optional[Event]:
        try:
            return self._set.next(event)
        except ValueError:
            return None

    def below(self, event: Event) -> Optional[Event]:
        try:
            return self._set.prev(event)
        except ValueError:
            return None


class SweepLineKey:
    __slots__ = 'event', 'orienteer'

    def __init__(self, orienteer: Orienteer, event: Event) -> None:
        self.orienteer, self.event = orienteer, event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'SweepLineKey') -> bool:
        """
        Checks if the segment (or at least the point) associated with event
        is lower than other's.
        """
        event, other_event = self.event, other.event
        if event is other_event:
            return False
        start, end = event.start, event.end
        other_start, other_end = other_event.start, other_event.end
        other_start_orientation = self.orienteer(start, end, other_start)
        other_end_orientation = self.orienteer(start, end, other_end)
        if other_start_orientation is other_end_orientation:
            return (event.from_test
                    if other_start_orientation is Orientation.COLLINEAR
                    else (other_start_orientation
                          is Orientation.COUNTERCLOCKWISE))
        start_orientation = self.orienteer(other_start, other_end, start)
        end_orientation = self.orienteer(other_start, other_end, end)
        if start_orientation is end_orientation:
            return start_orientation is Orientation.CLOCKWISE
        elif other_start_orientation is Orientation.COLLINEAR:
            return other_end_orientation is Orientation.COUNTERCLOCKWISE
        elif start_orientation is Orientation.COLLINEAR:
            return end_orientation is Orientation.CLOCKWISE
        elif end_orientation is Orientation.COLLINEAR:
            return start_orientation is Orientation.CLOCKWISE
        else:
            return other_start_orientation is Orientation.COUNTERCLOCKWISE
