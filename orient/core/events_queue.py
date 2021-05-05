import math
from abc import abstractmethod
from functools import partial
from typing import (Iterable,
                    List,
                    Optional,
                    Sequence)

from ground.base import (Context,
                         Orientation,
                         Relation)
from ground.hints import (Point,
                          Scalar)
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .enums import (OverlapKind,
                    SegmentsRelation)
from .event import (CompoundLeftEvent as CompoundEvent,
                    Event,
                    LeftEvent,
                    LinearLeftEvent as LinearEvent)
from .hints import (Orienteer,
                    SegmentEndpoints)
from .sweep_line import SweepLine
from .utils import all_equal


class EventsQueue:
    __slots__ = 'context', 'key', '_queue'

    def __init__(self, context: Context) -> None:
        self.context = context
        key = self.key = partial(EventsQueueKey, context.angle_orientation)
        self._queue = PriorityQueue(key=key)

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def peek(self) -> Event:
        return self._queue.peek()

    @abstractmethod
    def register(self, segments_endpoints: Iterable[SegmentEndpoints],
                 *,
                 from_test: bool) -> None:
        """
        Registers segments in the events queue.
        """

    @abstractmethod
    def sweep(self, stop_x: Scalar) -> Iterable[LeftEvent]:
        """
        Sweeps plane and emits processed segments' events.
        """

    def _divide_segment(self, event: LeftEvent, break_point: Point) -> None:
        self._queue.push(event.divide(break_point))
        self._queue.push(event.right)


class CompoundEventsQueue(EventsQueue):
    def register(self, segments_endpoints: Iterable[SegmentEndpoints],
                 *,
                 from_test: bool) -> None:
        push = self._queue.push
        for segment_endpoints in segments_endpoints:
            event = CompoundEvent.from_endpoints(segment_endpoints, from_test)
            push(event)
            push(event.right)

    def sweep(self, stop_x: Scalar) -> Iterable[CompoundEvent]:
        sweep_line = SweepLine(self.context)  # type: SweepLine[CompoundEvent]
        queue = self._queue
        start = queue.peek().start if queue else None  # type: Optional[Point]
        same_start_events = []  # type: List[Event]
        while queue:
            event = queue.peek()
            if event.start.x > stop_x:
                # no intersection segments left
                break
            queue.pop()
            if event.start == start:
                same_start_events.append(event)
            else:
                yield from complete_events_relations(same_start_events)
                same_start_events, start = [event], event.start
            if event.is_left:
                sweep_line.add(event)
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                self.compute_position(below_event, event)
                if (above_event is not None
                        and self.detect_intersection(event, above_event)):
                    self.compute_position(event, above_event)
                if (below_event is not None
                        and self.detect_intersection(below_event, event)):
                    self.compute_position(sweep_line.below(below_event),
                                          below_event)
            else:
                event = event.left
                if event in sweep_line:
                    above_event, below_event = (sweep_line.above(event),
                                                sweep_line.below(event))
                    sweep_line.remove(event)
                    if above_event is not None and below_event is not None:
                        self.detect_intersection(below_event, above_event)
        yield from complete_events_relations(same_start_events)

    def detect_intersection(self,
                            below_event: CompoundEvent,
                            event: CompoundEvent) -> bool:
        """
        Populates events queue with intersection events.
        Checks if events' segments overlap and have the same start.
        """
        relation = self.context.segments_relation(below_event, event)
        if relation is Relation.TOUCH or relation is Relation.CROSS:
            point = self.context.segments_intersection(below_event, event)
            if point != below_event.start and point != below_event.end:
                self._divide_segment(below_event, point)
            if point != event.start and point != event.end:
                self._divide_segment(event, point)
        elif relation is not Relation.DISJOINT:
            # segments overlap
            if event.from_test is below_event.from_test:
                raise ValueError('Segments of the same geometry '
                                 'should not overlap.')
            starts_equal = below_event.start == event.start
            ends_equal = below_event.end == event.end
            start_min, start_max = (
                (event, below_event)
                if starts_equal or self.key(event) < self.key(below_event)
                else (below_event, event))
            end_min, end_max = (
                (event.right, below_event.right)
                if ends_equal or (self.key(event.right)
                                  < self.key(below_event.right))
                else (below_event.right,
                      event.right))
            if starts_equal:
                # both line segments are equal or share the left endpoint
                below_event.overlap_kind = event.overlap_kind = (
                    OverlapKind.SAME_ORIENTATION
                    if event.interior_to_left is below_event.interior_to_left
                    else OverlapKind.DIFFERENT_ORIENTATION)
                if not ends_equal:
                    self._divide_segment(end_max.left, end_min.start)
                return True
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.left:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)
        return False

    @staticmethod
    def compute_position(below_event: Optional[CompoundEvent],
                         event: CompoundEvent) -> None:
        if below_event is not None:
            event.other_interior_to_left = (below_event.other_interior_to_left
                                            if (event.from_test
                                                is below_event.from_test)
                                            else below_event.interior_to_left)


class LinearEventsQueue(EventsQueue):
    def register(self, segments_endpoints: Iterable[SegmentEndpoints],
                 *,
                 from_test: bool) -> None:
        push = self._queue.push
        for segment_endpoints in segments_endpoints:
            event = LinearEvent.from_endpoints(segment_endpoints, from_test)
            push(event)
            push(event.right)

    def sweep(self, stop_x: Scalar) -> Iterable[LinearEvent]:
        sweep_line = SweepLine(self.context)  # type: SweepLine[LinearEvent]
        queue = self._queue
        start = queue.peek().start if queue else None  # type: Optional[Point]
        same_start_events = []  # type: List[Event]
        while queue:
            event = queue.peek()
            if event.start.x > stop_x:
                # no intersection segments left
                break
            queue.pop()
            if event.start == start:
                same_start_events.append(event)
            else:
                self.detect_crossing_angles(same_start_events)
                yield from complete_events_relations(same_start_events)
                same_start_events, start = [event], event.start
            if event.is_left:
                sweep_line.add(event)
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                if above_event is not None:
                    self.detect_intersection(event, above_event)
                if below_event is not None:
                    self.detect_intersection(below_event, event)
            else:
                event = event.left
                if event in sweep_line:
                    above_event, below_event = (sweep_line.above(event),
                                                sweep_line.below(event))
                    sweep_line.remove(event)
                    if above_event is not None and below_event is not None:
                        self.detect_intersection(below_event, above_event)
        self.detect_crossing_angles(same_start_events)
        yield from complete_events_relations(same_start_events)

    def detect_crossing_angles(self, same_start_events: Sequence[Event]
                               ) -> None:
        if (len(same_start_events) < 4
                or not (1 < sum(event.from_test for event in same_start_events)
                        < len(same_start_events) - 1)):
            # for crossing angles there should be at least two pairs
            # of segments from different origins
            return
        from_test_events, from_goal_events = [], []
        for event in same_start_events:
            (from_test_events
             if event.from_test
             else from_goal_events).append(event)
        start = same_start_events[0].start
        point_event_cosine = self._to_point_event_cosine
        base_event = min(from_goal_events,
                         key=partial(point_event_cosine,
                                     from_goal_events[0].end))
        base_end = base_event.end
        largest_angle_event = min(from_goal_events,
                                  key=partial(point_event_cosine, base_end))
        largest_angle_end = largest_angle_event.end
        base_orientation = self.context.angle_orientation(
                start, base_end, largest_angle_end)
        if not all_equal(self._point_in_angle(test_event.end, start, base_end,
                                              largest_angle_end,
                                              base_orientation)
                         for test_event in from_test_events):
            for event in same_start_events:
                left_event = event if event.is_left else event.left
                left_event.relation = max(left_event.relation,
                                          SegmentsRelation.CROSS)

    def detect_intersection(self,
                            below_event: LinearEvent,
                            event: LinearEvent) -> None:
        """
        Populates events queue with intersection events.
        """
        relation = self.context.segments_relation(below_event, event)
        if relation is Relation.TOUCH or relation is Relation.CROSS:
            point = self.context.segments_intersection(below_event, event)
            if point != below_event.start and point != below_event.end:
                self._divide_segment(below_event, point)
            if point != event.start and point != event.end:
                self._divide_segment(event, point)
        elif relation is not Relation.DISJOINT:
            # segments overlap
            if event.from_test is below_event.from_test:
                raise ValueError('Segments of the same geometry '
                                 'should not overlap.')
            starts_equal = below_event.start == event.start
            ends_equal = below_event.end == event.end
            start_min, start_max = (
                (event, below_event)
                if starts_equal or self.key(event) < self.key(below_event)
                else (below_event, event))
            end_min, end_max = (
                (event.right, below_event.right)
                if ends_equal or (self.key(event.right)
                                  < self.key(below_event.right))
                else (below_event.right,
                      event.right))
            if starts_equal:
                # both line segments are equal or share the left endpoint
                if not ends_equal:
                    self._divide_segment(end_max.left, end_min.start)
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.left:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)

    def _point_in_angle(self,
                        point: Point,
                        vertex: Point,
                        first_ray_point: Point,
                        second_ray_point: Point,
                        angle_orientation: Orientation) -> bool:
        first_half_orientation = self.context.angle_orientation(
                vertex, first_ray_point, point)
        second_half_orientation = self.context.angle_orientation(
                second_ray_point, vertex, point)
        return (second_half_orientation is angle_orientation
                if first_half_orientation is Orientation.COLLINEAR
                else (first_half_orientation is angle_orientation
                      if second_half_orientation is Orientation.COLLINEAR
                      else (first_half_orientation is second_half_orientation
                            is (angle_orientation
                                # if angle is degenerate
                                or Orientation.COUNTERCLOCKWISE))))

    def _to_point_event_cosine(self, point: Point, event: Event) -> Scalar:
        return (self.context.dot_product(event.start, point, event.start,
                                         event.end)
                / math.sqrt(self.context.points_squared_distance(event.start,
                                                                 event.end)))


class EventsQueueKey:
    __slots__ = 'orienteer', 'event'

    def __init__(self, orienteer: Orienteer, event: Event) -> None:
        self.orienteer, self.event = orienteer, event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'EventsQueueKey') -> bool:
        event, other_event = self.event, other.event
        start, other_start = event.start, other_event.start
        if start.x != other_start.x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return start.x < other_start.x
        elif start.y != other_start.y:
            # different points, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return start.y < other_start.y
        elif event.is_left is not other_event.is_left:
            # same start, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return other_event.is_left
        # same start, both events are left endpoints
        # or both are right endpoints
        else:
            other_end_orientation = self.orienteer(event.start, event.end,
                                                   other_event.end)
            return (other_event.from_test
                    if other_end_orientation is Orientation.COLLINEAR
                    else (other_end_orientation
                          # the lowest segment is processed first
                          is (Orientation.COUNTERCLOCKWISE
                              if event.is_left
                              else Orientation.CLOCKWISE)))


def complete_events_relations(same_start_events: Sequence[Event]
                              ) -> Iterable[Event]:
    for offset, first in enumerate(same_start_events,
                                   start=1):
        first_left = first if first.is_left else first.left
        for second_index in range(offset, len(same_start_events)):
            second = same_start_events[second_index]
            second_left = second if second.is_left else second.left
            if second_left.from_test is first_left.from_test:
                continue
            elif (first_left.start == second_left.start
                    and first_left.end == second_left.end):
                first_left.relation = second_left.relation = (
                    SegmentsRelation.OVERLAP)
            else:
                relation = (SegmentsRelation.TOUCH
                            if (first.start == first.original_start
                                or second.start == second.original_start)
                            else SegmentsRelation.CROSS)
                first_left.relation = max(first_left.relation, relation)
                second_left.relation = max(second_left.relation, relation)
        yield first_left
