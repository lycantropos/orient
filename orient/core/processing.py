from robust.linear import SegmentsRelationship

from orient.hints import Coordinate
from .events_queue import EventsQueue
from .relation import Relation
from .sweep import sweep


def process_linear_queue(events_queue: EventsQueue,
                         test_max_x: Coordinate) -> Relation:
    test_is_subset_of_goal = goal_is_subset_of_test = True
    boundaries_do_not_intersect = True
    test_boundary_in_goal_interior = goal_boundary_in_test_interior = False
    has_overlap = has_cross = False
    for event in sweep(events_queue, test_max_x):
        if (test_is_subset_of_goal
                and event.from_test and event.outside):
            test_is_subset_of_goal = False
        if (goal_is_subset_of_test
                and event.from_goal and event.outside):
            goal_is_subset_of_test = False
        if (boundaries_do_not_intersect
                and event.relationship is not SegmentsRelationship.NONE):
            boundaries_do_not_intersect = False
        if (not test_boundary_in_goal_interior
                and event.from_test and event.inside):
            test_boundary_in_goal_interior = True
        if (not goal_boundary_in_test_interior
                and event.from_goal and event.inside):
            goal_boundary_in_test_interior = True
        if (not has_overlap
                and event.relationship is SegmentsRelationship.OVERLAP):
            has_overlap = True
        if not has_cross and event.relationship is SegmentsRelationship.CROSS:
            has_cross = True
    if goal_is_subset_of_test:
        goal_is_subset_of_test = not events_queue
    if goal_is_subset_of_test:
        return (Relation.EQUAL
                if test_is_subset_of_goal
                else (Relation.DISJOINT
                      if boundaries_do_not_intersect
                      else (Relation.OVERLAP
                            if goal_boundary_in_test_interior
                            else Relation.COMPOSITE)))
    elif test_is_subset_of_goal:
        return (Relation.DISJOINT
                if boundaries_do_not_intersect
                else (Relation.OVERLAP
                      if test_boundary_in_goal_interior
                      else Relation.COMPONENT))
    else:
        return (Relation.DISJOINT
                if boundaries_do_not_intersect
                else (Relation.OVERLAP
                      if has_overlap
                      else (Relation.CROSS
                            if has_cross
                            else Relation.TOUCH)))


def process_linear_compound_queue(events_queue: EventsQueue,
                                  test_max_x: Coordinate) -> Relation:
    # ``goal`` is a compound object
    # ``test`` is a linear object
    test_boundary_in_goal_interior = has_touch = False
    test_is_subset_of_goal = goal_is_subset_of_test = True
    for event in sweep(events_queue, test_max_x):
        if event.relationship is SegmentsRelationship.CROSS:
            return Relation.CROSS
        if test_is_subset_of_goal and event.from_test and event.outside:
            test_is_subset_of_goal = False
        if goal_is_subset_of_test and event.from_goal and event.outside:
            goal_is_subset_of_test = False
        if (not test_boundary_in_goal_interior
                and event.from_test and event.inside):
            test_boundary_in_goal_interior = True
        if (not has_touch
                and (event.relationship is SegmentsRelationship.TOUCH
                     or event.relationship is SegmentsRelationship.OVERLAP)):
            has_touch = True
    if goal_is_subset_of_test:
        goal_is_subset_of_test = not events_queue
    if goal_is_subset_of_test:
        return (Relation.COMPONENT
                if test_is_subset_of_goal
                else (Relation.TOUCH
                      if has_touch
                      else Relation.DISJOINT))
    elif test_is_subset_of_goal:
        return (Relation.ENCLOSED
                if has_touch
                else Relation.WITHIN)
    else:
        return (Relation.CROSS
                if test_boundary_in_goal_interior
                else (Relation.TOUCH
                      if has_touch
                      else Relation.DISJOINT))


def process_compound_queue(events_queue: EventsQueue,
                           test_max_x: Coordinate) -> Relation:
    test_boundary_in_goal_interior = goal_boundary_in_test_interior = False
    boundaries_do_not_intersect, boundary_in_other_interior = True, False
    test_is_subset_of_goal = goal_is_subset_of_test = True
    for event in sweep(events_queue, test_max_x):
        if event.relationship is SegmentsRelationship.CROSS:
            return Relation.OVERLAP
        if test_is_subset_of_goal and event.from_test and event.outside:
            test_is_subset_of_goal = False
        if goal_is_subset_of_test and event.from_goal and event.outside:
            goal_is_subset_of_test = False
        if (boundaries_do_not_intersect
                and event.relationship is not SegmentsRelationship.NONE):
            boundaries_do_not_intersect = False
        if not boundary_in_other_interior and event.inside:
            boundary_in_other_interior = True
        if (not test_boundary_in_goal_interior
                and event.from_test and event.inside):
            test_boundary_in_goal_interior = True
        if (not goal_boundary_in_test_interior
                and event.from_goal and event.inside):
            goal_boundary_in_test_interior = True
    if goal_is_subset_of_test:
        goal_is_subset_of_test = not events_queue
    if boundaries_do_not_intersect:
        return (Relation.WITHIN
                if test_is_subset_of_goal
                else (Relation.COVER
                      if goal_is_subset_of_test
                      else (Relation.OVERLAP
                            if boundary_in_other_interior
                            else Relation.DISJOINT)))
    elif test_is_subset_of_goal:
        return (Relation.EQUAL
                if goal_is_subset_of_test
                else (Relation.ENCLOSED
                      if test_boundary_in_goal_interior
                      else Relation.COMPONENT))
    elif goal_is_subset_of_test:
        return (Relation.ENCLOSES
                if goal_boundary_in_test_interior
                else Relation.COMPOSITE)
    else:
        return (Relation.OVERLAP
                if boundary_in_other_interior
                else Relation.TOUCH)
