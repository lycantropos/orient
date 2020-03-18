from typing import (Iterable,
                    Sequence)

from orient.hints import (Contour,
                          Segment)
from .events_queue import EventsQueue
from .sweep import sweep


def contains_contour(goal: Contour, test: Contour) -> bool:
    events_queue = EventsQueue()
    for segment in to_segments(goal):
        events_queue.register_segment(segment,
                                      from_test_contour=False)
    for segment in to_segments(test):
        events_queue.register_segment(segment,
                                      from_test_contour=True)
    return all(not event.from_test_contour or event.in_intersection
               for event in sweep(events_queue))


def contains_contours(goal: Contour, tests: Sequence[Contour]) -> bool:
    events_queue = EventsQueue()
    for segment in to_segments(goal):
        events_queue.register_segment(segment,
                                      from_test_contour=False)
    for test in tests:
        for segment in to_segments(test):
            events_queue.register_segment(segment,
                                          from_test_contour=True)
    return all(not event.from_test_contour or event.in_intersection
               for event in sweep(events_queue))


def to_segments(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))
