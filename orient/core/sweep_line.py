from typing import Optional

from dendroid import red_black
from reprit.base import generate_repr

from .event import Event
from .utils import (Orientation,
                    orientation)


class SweepLine:
    __slots__ = 'current_x', '_tree'

    def __init__(self) -> None:
        self._tree = red_black.set_(key=SweepLineKey)

    __repr__ = generate_repr(__init__)

    def __contains__(self, event: Event) -> bool:
        return event in self._tree

    def add(self, event: Event) -> None:
        self._tree.add(event)

    def remove(self, event: Event) -> None:
        self._tree.remove(event)

    def above(self, event: Event) -> Optional[Event]:
        try:
            return self._tree.next(event)
        except ValueError:
            return None

    def below(self, event: Event) -> Optional[Event]:
        try:
            return self._tree.prev(event)
        except ValueError:
            return None


class SweepLineKey:
    __slots__ = 'event',

    def __init__(self, event: Event) -> None:
        self.event = event

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
        other_start_orientation = orientation(start, end, other_start)
        other_end_orientation = orientation(start, end, other_end)
        if other_start_orientation is other_end_orientation:
            return (event.from_test
                    if other_start_orientation is Orientation.COLLINEAR
                    else (other_start_orientation
                          is Orientation.COUNTERCLOCKWISE))
        start_orientation = orientation(other_start, other_end, start)
        end_orientation = orientation(other_start, other_end, end)
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
