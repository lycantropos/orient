from typing import (Iterable,
                    Sequence)

from orient.hints import (Contour,
                          Segment)
from .events_queue import EventsQueue
from .sweep import sweep


def contains_contour(goal: Contour, test: Contour) -> bool:
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test_contour=False)
    register(events_queue, test,
             from_test_contour=True)
    return all(not event.from_test_contour or event.in_intersection
               for event in sweep(events_queue))


def contains_contours(goal: Contour, tests: Sequence[Contour]) -> bool:
    events_queue = EventsQueue()
    register(events_queue, goal,
             from_test_contour=False)
    for test in tests:
        register(events_queue, test,
                 from_test_contour=True)
    return all(not event.from_test_contour or event.in_intersection
               for event in sweep(events_queue))


def register(events_queue: EventsQueue, contour: Contour,
             *,
             from_test_contour: bool) -> None:
    for segment in to_segments(contour):
        events_queue.register_segment(segment,
                                      from_test_contour=from_test_contour)


def to_segments(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))
