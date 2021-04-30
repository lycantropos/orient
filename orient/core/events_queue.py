import math
from abc import abstractmethod
from functools import partial
from typing import (Generic,
                    Iterable,
                    List,
                    Optional,
                    Type)

from ground.base import (Context,
                         Orientation,
                         Relation)
from ground.hints import (Point,
                          Scalar)
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .enums import (OverlapKind,
                    SegmentsRelation)
from .event import (CompoundEvent,
                    Event,
                    LinearEvent)
from .hints import (Orienteer,
                    SegmentEndpoints)
from .sweep_line import SweepLine
from .utils import all_equal


class EventsQueue(Generic[Event]):
    __slots__ = 'context', 'key', '_queue'

    event_cls = None  # type: Type[Event]

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
    def divide_segment(self, event: Event, point: Point) -> None:
        """
        Divides segment into parts at given point.
        """

    @abstractmethod
    def register(self, endpoints: Iterable[SegmentEndpoints],
                 *,
                 from_test: bool) -> None:
        """
        Registers segments in the events queue.
        """

    @abstractmethod
    def sweep(self, stop_x: Scalar) -> Iterable[Event]:
        """
        Sweeps plane and emits processed segments' events.
        """

    def _segments_relation(self,
                           first: Event,
                           second: Event) -> SegmentsRelation:
        result = self.context.segments_relation(first, second)
        return (SegmentsRelation.DISJOINT if result is Relation.DISJOINT
                else (SegmentsRelation.TOUCH if result is Relation.TOUCH
                      else (SegmentsRelation.CROSS if result is Relation.CROSS
                            else SegmentsRelation.OVERLAP)))


class CompoundEventsQueue(EventsQueue[CompoundEvent]):
    event_cls = CompoundEvent

    def register(self, endpoints: Iterable[SegmentEndpoints],
                 *,
                 from_test: bool) -> None:
        for start, end in endpoints:
            inside_on_left = True
            if start > end:
                start, end = end, start
                inside_on_left = False
            start_event = self.event_cls(True, start, None, from_test,
                                         SegmentsRelation.DISJOINT,
                                         inside_on_left)
            end_event = self.event_cls(False, end, start_event, from_test,
                                       SegmentsRelation.DISJOINT,
                                       inside_on_left)
            start_event.complement = end_event
            self._queue.push(start_event)
            self._queue.push(end_event)

    def divide_segment(self, event: CompoundEvent, break_point: Point) -> None:
        left_event = event.complement.complement = self.event_cls(
                True, break_point, event.complement, event.from_test,
                event.complement.relation, event.interior_to_left)
        right_event = event.complement = self.event_cls(
                False, break_point, event, event.from_test, event.relation,
                event.interior_to_left)
        self._queue.push(left_event)
        self._queue.push(right_event)

    def sweep(self, stop_x: Scalar) -> Iterable[CompoundEvent]:
        sweep_line = SweepLine(self.context)
        queue = self._queue
        while queue:
            event = queue.peek()
            start = event.start
            if start.x > stop_x:
                # no intersection segments left
                return
            queue.pop()
            same_start_events = [event]
            while queue and queue.peek().start == start:
                same_start_events.append(queue.pop())
            if not all_equal(event.from_test for event in same_start_events):
                for event in same_start_events:
                    event.set_both_relations(max(event.relation,
                                                 SegmentsRelation.TOUCH))
            for event in same_start_events:
                if event.is_left_endpoint:
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
                    event = event.complement
                    if event in sweep_line:
                        above_event, below_event = (sweep_line.above(event),
                                                    sweep_line.below(event))
                        sweep_line.remove(event)
                        if above_event is not None and below_event is not None:
                            self.detect_intersection(below_event, above_event)
                    yield event

    def detect_intersection(self, below_event: CompoundEvent,
                            event: CompoundEvent) -> bool:
        """
        Populates events queue with intersection events.
        Checks if events' segments overlap and have the same start.
        """
        relation = self._segments_relation(below_event, event)
        if relation is SegmentsRelation.OVERLAP:
            # segments overlap
            if event.from_test is below_event.from_test:
                raise ValueError('Segments of the same object '
                                 'should not overlap.')
            starts_equal = below_event.start == event.start
            ends_equal = below_event.end == event.end
            start_min, start_max = ((None, None)
                                    if starts_equal
                                    else ((event, below_event)
                                          if (self.key(event)
                                              < self.key(below_event))
                                          else (below_event, event)))
            end_min, end_max = ((None, None)
                                if ends_equal
                                else
                                ((event.complement, below_event.complement)
                                 if (self.key(event.complement)
                                     < self.key(below_event.complement))
                                 else (below_event.complement,
                                       event.complement)))
            if starts_equal:
                # both line segments are equal or share the left endpoint
                below_event.overlap_kind = event.overlap_kind = (
                    OverlapKind.SAME_ORIENTATION
                    if event.interior_to_left is below_event.interior_to_left
                    else OverlapKind.DIFFERENT_ORIENTATION)
                if ends_equal:
                    event.set_both_relations(relation)
                    below_event.set_both_relations(relation)
                else:
                    end_min.set_both_relations(relation)
                    end_max.complement.relation = relation
                    self.divide_segment(end_max.complement, end_min.start)
                return True
            elif ends_equal:
                # the line segments share the right endpoint
                start_max.set_both_relations(relation)
                start_min.complement.relation = relation
                self.divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                start_max.set_both_relations(relation)
                start_min_original_relation = start_min.relation
                start_min.relation = relation
                self.divide_segment(start_min, end_min.start)
                start_min.relation = start_min_original_relation
                start_min.complement.relation = relation
                self.divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                start_max.relation = relation
                self.divide_segment(start_max, end_min.start)
                start_min.complement.relation = relation
                self.divide_segment(start_min, start_max.start)
        elif relation is not SegmentsRelation.DISJOINT:
            point = self.context.segments_intersection(below_event, event)
            if point != below_event.start and point != below_event.end:
                self.divide_segment(below_event, point)
            if point != event.start and point != event.end:
                self.divide_segment(event, point)
            if event.from_test is not below_event.from_test:
                event.set_both_relations(max(event.relation,
                                             relation))
                below_event.set_both_relations(max(below_event.relation,
                                                   relation))
        return False

    @staticmethod
    def compute_position(below_event: Optional[CompoundEvent],
                         event: CompoundEvent) -> None:
        if below_event is not None:
            event.other_interior_to_left = (below_event.other_interior_to_left
                                            if (event.from_test
                                                is below_event.from_test)
                                            else below_event.interior_to_left)


class LinearEventsQueue(EventsQueue[LinearEvent]):
    event_cls = LinearEvent

    def register(self, endpoints: Iterable[SegmentEndpoints],
                 *,
                 from_test: bool) -> None:
        for start, end in endpoints:
            if start > end:
                start, end = end, start
            start_event = self.event_cls(True, start, None, from_test,
                                         SegmentsRelation.DISJOINT)
            end_event = self.event_cls(False, end, start_event, from_test,
                                       SegmentsRelation.DISJOINT)
            start_event.complement = end_event
            self._queue.push(start_event)
            self._queue.push(end_event)

    def divide_segment(self, event: Event, break_point: Point) -> None:
        left_event = event.complement.complement = self.event_cls(
                True, break_point, event.complement, event.from_test,
                event.complement.relation)
        right_event = event.complement = self.event_cls(
                False, break_point, event, event.from_test, event.relation)
        self._queue.push(left_event)
        self._queue.push(right_event)

    def sweep(self, stop_x: Scalar) -> Iterable[LinearEvent]:
        sweep_line = SweepLine(self.context)
        queue = self._queue
        prev_start = None
        prev_from_same_events = []  # type: List[LinearEvent]
        prev_from_other_events = []  # type: List[LinearEvent]
        while queue:
            event = queue.peek()
            start = event.start
            if start.x > stop_x:
                # no intersection segments left
                return
            queue.pop()
            same_start_events = [event]
            from_same_events, from_other_events = (
                ((prev_from_same_events + [event], prev_from_other_events)
                 if event.from_test is prev_from_same_events[0].from_test
                 else ((prev_from_other_events + [event],
                        prev_from_same_events)))
                if start == prev_start
                else ([event], []))
            while queue and queue.peek().start == start:
                next_event = queue.pop()
                same_start_events.append(next_event)
                (from_same_events
                 if next_event.from_test is event.from_test
                 else from_other_events).append(next_event)
            if from_other_events:
                if len(from_same_events) > 1 and len(from_other_events) > 1:
                    point_event_cosine = self._to_point_event_cosine
                    base_event = min(from_same_events,
                                     key=partial(point_event_cosine,
                                                 event.end))
                    base_end = base_event.end
                    largest_angle_event = min(from_same_events,
                                              key=partial(point_event_cosine,
                                                          base_end))
                    largest_angle_end = largest_angle_event.end
                    base_orientation = self.context.angle_orientation(
                            start, base_end, largest_angle_end)
                    relation = (
                        SegmentsRelation.TOUCH
                        if all_equal(self._point_in_angle(other_event.end,
                                                          base_end, start,
                                                          largest_angle_end,
                                                          base_orientation)
                                     for other_event in from_other_events)
                        else SegmentsRelation.CROSS)
                else:
                    relation = SegmentsRelation.TOUCH
                for event in same_start_events:
                    event.set_both_relations(max(event.relation, relation))
            for event in same_start_events:
                if event.is_left_endpoint:
                    sweep_line.add(event)
                    above_event, below_event = (sweep_line.above(event),
                                                sweep_line.below(event))
                    if above_event is not None:
                        self.detect_intersection(event, above_event)
                    if below_event is not None:
                        self.detect_intersection(below_event, event)
                else:
                    event = event.complement
                    if event in sweep_line:
                        above_event, below_event = (sweep_line.above(event),
                                                    sweep_line.below(event))
                        sweep_line.remove(event)
                        if above_event is not None and below_event is not None:
                            self.detect_intersection(below_event, above_event)
                    yield event
            prev_start = start
            prev_from_same_events, prev_from_other_events = (from_same_events,
                                                             from_other_events)

    def detect_intersection(self, below_event: LinearEvent, event: LinearEvent
                            ) -> None:
        """
        Populates events queue with intersection events.
        """
        relation = self._segments_relation(below_event, event)
        if relation is SegmentsRelation.OVERLAP:
            # segments overlap
            if event.from_test is below_event.from_test:
                raise ValueError('Segments of the same object '
                                 'should not overlap.')
            starts_equal = below_event.start == event.start
            ends_equal = below_event.end == event.end
            start_min, start_max = ((None, None)
                                    if starts_equal
                                    else
                                    ((event, below_event)
                                     if self.key(event) < self.key(below_event)
                                     else (below_event, event)))
            end_min, end_max = ((None, None)
                                if ends_equal
                                else
                                ((event.complement, below_event.complement)
                                 if (self.key(event.complement)
                                     < self.key(below_event.complement))
                                 else (below_event.complement,
                                       event.complement)))
            if starts_equal:
                # both line segments are equal or share the left endpoint
                if ends_equal:
                    event.set_both_relations(relation)
                    below_event.set_both_relations(relation)
                else:
                    end_min.set_both_relations(relation)
                    end_max.complement.relation = relation
                    self.divide_segment(end_max.complement, end_min.start)
            elif ends_equal:
                # the line segments share the right endpoint
                start_max.set_both_relations(relation)
                start_min.complement.relation = relation
                self.divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                start_max.set_both_relations(relation)
                start_min_original_relation = start_min.relation
                start_min.relation = relation
                self.divide_segment(start_min, end_min.start)
                start_min.relation = start_min_original_relation
                start_min.complement.relation = relation
                self.divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                start_max.relation = relation
                self.divide_segment(start_max, end_min.start)
                start_min.complement.relation = relation
                self.divide_segment(start_min, start_max.start)
        elif relation is not SegmentsRelation.DISJOINT:
            point = self.context.segments_intersection(below_event, event)
            if point != below_event.start and point != below_event.end:
                self.divide_segment(below_event, point)
            if point != event.start and point != event.end:
                self.divide_segment(event, point)
            if event.from_test is not below_event.from_test:
                event.set_both_relations(max(event.relation, relation))
                below_event.set_both_relations(max(below_event.relation,
                                                   relation))

    def _to_point_event_cosine(self, point: Point, event: Event) -> Scalar:
        return (self.context.dot_product(event.start, point, event.start,
                                         event.end)
                / math.sqrt(self.context.points_squared_distance(event.start,
                                                                 event.end)))

    def _point_in_angle(self, point: Point,
                        first_ray_point: Point,
                        vertex: Point,
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
        elif event.is_left_endpoint is not other_event.is_left_endpoint:
            # same start, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return other_event.is_left_endpoint
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
                              if event.is_left_endpoint
                              else Orientation.CLOCKWISE)))
