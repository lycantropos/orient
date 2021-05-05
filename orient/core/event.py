from abc import (ABC,
                 abstractmethod)
from reprlib import recursive_repr
from typing import Optional

from ground.hints import Point
from reprit.base import generate_repr

from .enums import (OverlapKind,
                    SegmentsRelation)
from .hints import SegmentEndpoints


class Event(ABC):
    left = None  # type: Optional[LeftEvent]
    right = None  # type: Optional[RightEvent]

    __slots__ = ()

    @property
    @abstractmethod
    def end(self) -> Point:
        """Returns end of the event."""

    @property
    @abstractmethod
    def from_goal(self) -> bool:
        """Checks if the event's segment is from goal geometry."""

    @property
    @abstractmethod
    def from_test(self) -> bool:
        """Checks if the event's segment is from test geometry."""

    @property
    @abstractmethod
    def is_left(self) -> bool:
        """
        Checks if the event corresponds to a leftmost endpoint of the segment.
        """

    @property
    @abstractmethod
    def original_end(self) -> Point:
        """Returns original end of the event's segment."""

    @property
    @abstractmethod
    def original_start(self) -> Point:
        """Returns original start of the event's segment."""

    @property
    @abstractmethod
    def start(self) -> Point:
        """Returns start of the event."""


class LeftEvent(Event):
    is_left = True

    @abstractmethod
    def divide(self, break_point: Point) -> 'LeftEvent':
        """Divides the event at given break point and returns tail."""


class RightEvent(Event):
    is_left = False

    __slots__ = 'left', '_original_start', '_start'

    def __init__(self,
                 start: Point,
                 left: LeftEvent,
                 original_start: Point) -> None:
        self.left, self._original_start, self._start = (left, original_start,
                                                        start)

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.left.start

    @property
    def from_goal(self) -> bool:
        return self.left.from_goal

    @property
    def from_test(self) -> bool:
        return self.left.from_test

    @property
    def original_end(self) -> Point:
        return self.left.original_start

    @property
    def original_start(self) -> Point:
        return self._original_start

    @property
    def start(self) -> Point:
        return self._start


class LinearLeftEvent(LeftEvent):
    @classmethod
    def from_endpoints(cls, endpoints, from_test: bool) -> 'LinearLeftEvent':
        start, end = endpoints
        if start > end:
            start, end = end, start
        result = cls(start, None, start, from_test, SegmentsRelation.DISJOINT)
        result.right = RightEvent(end, result, end)
        return result

    __slots__ = ('right', 'relation', '_from_test', '_original_start',
                 '_start')

    def __init__(self,
                 start: Point,
                 right: Optional[RightEvent],
                 original_start: Point,
                 from_test: bool,
                 relation: SegmentsRelation) -> None:
        self.right, self._original_start, self._start = (right, original_start,
                                                         start)
        self._from_test = from_test
        self.relation = relation

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.right.start

    @property
    def from_goal(self) -> bool:
        return not self.from_test

    @property
    def from_test(self) -> bool:
        return self._from_test

    @property
    def original_end(self) -> Point:
        return self.right.original_start

    @property
    def original_start(self) -> Point:
        return self._original_start

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, break_point: Point) -> 'LinearLeftEvent':
        tail = self.right.left = LinearLeftEvent(break_point, self.right,
                                                 self.original_start,
                                                 self.from_test, self.relation)
        self.right = RightEvent(break_point, self, self.original_end)
        return tail


class CompoundLeftEvent(LeftEvent):
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_test: bool) -> 'CompoundLeftEvent':
        start, end = segment_endpoints
        inside_on_left = True
        if start > end:
            start, end = end, start
            inside_on_left = False
        result = cls(start, None, start, from_test,
                     SegmentsRelation.DISJOINT, inside_on_left)
        result.right = RightEvent(end, result, end)
        return result

    __slots__ = ('right', 'interior_to_left', 'other_interior_to_left',
                 'overlap_kind', 'relation', '_from_test', '_original_start',
                 '_start')

    def __init__(self,
                 start: Point,
                 right: Optional[RightEvent],
                 original_start: Point,
                 from_test: bool,
                 relation: SegmentsRelation,
                 interior_to_left: bool) -> None:
        self.right, self._original_start, self._start = (right, original_start,
                                                         start)
        self._from_test = from_test
        self.relation = relation
        self.overlap_kind = OverlapKind.NONE
        self.interior_to_left = interior_to_left
        self.other_interior_to_left = False

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.right.start

    @property
    def from_goal(self) -> bool:
        return not self.from_test

    @property
    def from_test(self) -> bool:
        return self._from_test

    @property
    def inside(self) -> bool:
        """
        Checks if the segment enclosed by
        or lies within the region of the intersection.
        """
        return (self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    @property
    def is_common_polyline_component(self) -> bool:
        """
        Checks if the segment is a component of intersection's polyline.
        """
        return self.overlap_kind is OverlapKind.DIFFERENT_ORIENTATION

    @property
    def is_common_region_boundary(self) -> bool:
        """
        Checks if the segment is a boundary of intersection's region.
        """
        return self.overlap_kind is OverlapKind.SAME_ORIENTATION

    @property
    def original_end(self) -> Point:
        return self.right.original_start

    @property
    def original_start(self) -> Point:
        return self._original_start

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return (not self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, break_point: Point) -> 'CompoundLeftEvent':
        tail = self.right.left = CompoundLeftEvent(
                break_point, self.right, self.original_start, self.from_test,
                self.relation, self.interior_to_left)
        self.right = RightEvent(break_point, self, self.original_end)
        return tail
