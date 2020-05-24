import math
from abc import abstractmethod
from functools import partial
from itertools import groupby
from typing import (Any,
                    Generic,
                    Iterable,
                    List,
                    Optional,
                    Type)

from reprit.base import generate_repr
from robust.angular import (Orientation,
                            orientation)
from robust.linear import (SegmentsRelationship,
                           segments_intersection,
                           segments_relationship)
from robust.projection import signed_length

from orient.hints import (Coordinate,
                          Point,
                          Segment)
from .event import (ClosedEvent,
                    EdgeKind,
                    Event,
                    OpenEvent)
from .events_queue import (EventsQueue,
                           EventsQueueKey)
from .sweep_line import SweepLine


class Sweeper(Generic[Event]):
    event_cls = None  # type: Type[Event]

    def __init__(self) -> None:
        self._events_queue = EventsQueue()

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._events_queue)

    def peek(self) -> Event:
        return self._events_queue.peek()

    def register_segments(self, segments: Iterable[Segment],
                          *,
                          from_test: bool) -> None:
        for start, end in segments:
            if start > end:
                start, end = end, start
            start_event = self.event_cls(True, start, None, from_test,
                                         SegmentsRelationship.NONE)
            end_event = self.event_cls(False, end, start_event, from_test,
                                       SegmentsRelationship.NONE)
            start_event.complement = end_event
            self._events_queue.push(start_event)
            self._events_queue.push(end_event)

    def divide_segment(self, event: Event, point: Point) -> None:
        left_event = self.event_cls(True, point, event.complement,
                                    event.from_test,
                                    event.complement.relationship)
        right_event = self.event_cls(False, point, event, event.from_test,
                                     event.relationship)
        event.complement.complement, event.complement = left_event, right_event
        self._events_queue.push(left_event)
        self._events_queue.push(right_event)

    @abstractmethod
    def sweep(self, stop_x: Coordinate) -> Iterable[Event]:
        """
        Sweeps plane and emits processed segments' events.
        """


class ClosedSweeper(Sweeper[ClosedEvent]):
    event_cls = ClosedEvent

    def sweep(self, stop_x: Coordinate) -> Iterable[ClosedEvent]:
        sweep_line = SweepLine()
        events_queue = self._events_queue
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
                    event.set_both_relationships(
                            max(event.relationship,
                                SegmentsRelationship.TOUCH))
            for event in same_start_events:
                if event.is_left_endpoint:
                    sweep_line.add(event)
                    above_event, below_event = (sweep_line.above(event),
                                                sweep_line.below(event))
                    self.compute_transition(below_event, event)
                    if (above_event is not None
                            and self.detect_intersection(event, above_event)):
                        self.compute_transition(below_event, event)
                        self.compute_transition(event, above_event)
                    if (below_event is not None
                            and self.detect_intersection(below_event, event)):
                        below_below_event = sweep_line.below(below_event)
                        self.compute_transition(below_below_event, below_event)
                        self.compute_transition(below_event, event)
                else:
                    event = event.complement
                    if event in sweep_line:
                        above_event, below_event = (sweep_line.above(event),
                                                    sweep_line.below(event))
                        sweep_line.remove(event)
                        if above_event is not None and below_event is not None:
                            self.detect_intersection(below_event, above_event)
                    yield event

    def detect_intersection(self, below_event: ClosedEvent,
                            event: ClosedEvent) -> bool:
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
                    self.divide_segment(end_max.complement, end_min.start)
                return True
            elif ends_equal:
                # the line segments share the right endpoint
                start_max.set_both_relationships(relationship)
                start_min.complement.relationship = relationship
                self.divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                start_max.set_both_relationships(relationship)
                start_min_original_relationship = start_min.relationship
                start_min.relationship = relationship
                self.divide_segment(start_min, end_min.start)
                start_min.relationship = start_min_original_relationship
                start_min.complement.relationship = relationship
                self.divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                start_max.relationship = relationship
                self.divide_segment(start_max, end_min.start)
                start_min.complement.relationship = relationship
                self.divide_segment(start_min, start_max.start)
        elif relationship is not SegmentsRelationship.NONE:
            point = segments_intersection(below_segment, segment)
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect at endpoints
                if point != below_event.start and point != below_event.end:
                    self.divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self.divide_segment(event, point)
            if event.from_test is not below_event.from_test:
                event.set_both_relationships(max(event.relationship,
                                                 relationship))
                below_event.set_both_relationships(
                        max(below_event.relationship, relationship))
        return False

    @staticmethod
    def compute_transition(below_event: Optional[ClosedEvent],
                           event: ClosedEvent) -> None:
        if below_event is None:
            event.in_out, event.other_in_out = False, True
        elif event.from_test is below_event.from_test:
            event.in_out, event.other_in_out = (not below_event.in_out,
                                                below_event.other_in_out)
        else:
            event.in_out, event.other_in_out = (not below_event.other_in_out,
                                                below_event.in_out)


class OpenSweeper(Sweeper):
    event_cls = OpenEvent

    def sweep(self, stop_x: Coordinate) -> Iterable[OpenEvent]:
        sweep_line = SweepLine()
        events_queue = self._events_queue
        prev_start = None
        prev_from_same_events = []  # type: List[OpenEvent]
        prev_from_other_events = []  # type: List[OpenEvent]
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
            from_same_events, from_other_events = (
                ((prev_from_same_events + [event], prev_from_other_events)
                 if event.from_test is prev_from_same_events[0].from_test
                 else ((prev_from_other_events + [event],
                        prev_from_same_events)))
                if start == prev_start
                else ([event], []))
            while events_queue and events_queue.peek().start == start:
                next_event = events_queue.pop()
                same_start_events.append(next_event)
                (from_same_events
                 if next_event.from_test is event.from_test
                 else from_other_events).append(next_event)
            if from_other_events:
                if len(from_same_events) > 1 and len(from_other_events) > 1:
                    base_event = min(from_same_events,
                                     key=partial(_to_point_event_cosine,
                                                 event.end))
                    base_end = base_event.end
                    largest_angle_event = min(
                            from_same_events,
                            key=partial(_to_point_event_cosine, base_end))
                    largest_angle_end = largest_angle_event.end
                    base_orientation = orientation(base_end, start,
                                                   largest_angle_end)
                    if all_equal(_point_in_angle(other_event.end,
                                                 base_end, start,
                                                 largest_angle_end,
                                                 base_orientation)
                                 for other_event in from_other_events):
                        relationship = SegmentsRelationship.TOUCH
                    else:
                        relationship = SegmentsRelationship.CROSS
                else:
                    relationship = SegmentsRelationship.TOUCH
                for event in same_start_events:
                    event.set_both_relationships(max(event.relationship,
                                                     relationship))
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

    def detect_intersection(self, below_event: OpenEvent,
                            event: OpenEvent) -> None:
        """
        Populates events queue with intersection events.
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
                if ends_equal:
                    event.set_both_relationships(relationship)
                    below_event.set_both_relationships(relationship)
                else:
                    end_min.set_both_relationships(relationship)
                    end_max.complement.relationship = relationship
                    self.divide_segment(end_max.complement, end_min.start)
            elif ends_equal:
                # the line segments share the right endpoint
                start_max.set_both_relationships(relationship)
                start_min.complement.relationship = relationship
                self.divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                start_max.set_both_relationships(relationship)
                start_min_original_relationship = start_min.relationship
                start_min.relationship = relationship
                self.divide_segment(start_min, end_min.start)
                start_min.relationship = start_min_original_relationship
                start_min.complement.relationship = relationship
                self.divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                start_max.relationship = relationship
                self.divide_segment(start_max, end_min.start)
                start_min.complement.relationship = relationship
                self.divide_segment(start_min, start_max.start)
        elif relationship is not SegmentsRelationship.NONE:
            point = segments_intersection(below_segment, segment)
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect at endpoints
                if point != below_event.start and point != below_event.end:
                    self.divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self.divide_segment(event, point)

            if event.from_test is not below_event.from_test:
                event.set_both_relationships(max(event.relationship,
                                                 relationship))
                below_event.set_both_relationships(
                        max(below_event.relationship, relationship))


def all_equal(values: Iterable[Any]) -> bool:
    groups = groupby(values)
    return next(groups, True) and not next(groups, False)


def _to_point_event_cosine(point: Point, event: Event) -> Coordinate:
    return (signed_length(event.start, point, event.start, event.end)
            / _points_distance(event.start, event.end))


def _point_in_angle(point: Point,
                    first_ray_point: Point,
                    vertex: Point,
                    second_ray_point: Point,
                    angle_orientation: Orientation) -> bool:
    first_half_orientation = orientation(first_ray_point, vertex, point)
    second_half_orientation = orientation(vertex, second_ray_point, point)
    return (second_half_orientation is angle_orientation
            if first_half_orientation is Orientation.COLLINEAR
            else (first_half_orientation is angle_orientation
                  if second_half_orientation is Orientation.COLLINEAR
                  else (first_half_orientation is second_half_orientation
                        is (angle_orientation
                            # if angle is degenerate
                            or Orientation.COUNTERCLOCKWISE))))


def _points_distance(start: Point, end: Point) -> Coordinate:
    (start_x, start_y), (end_x, end_y) = start, end
    delta_x, delta_y = end_x - start_x, end_y - start_y
    return math.sqrt(delta_x * delta_x + delta_y * delta_y)
