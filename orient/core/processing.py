from ground.base import Relation
from ground.hints import Scalar

from .enums import SegmentsRelation
from .events_queue import (CompoundEventsQueue,
                           LinearEventsQueue)


def process_open_linear_queue(events_queue: LinearEventsQueue,
                              stop_x: Scalar) -> Relation:
    test_is_subset = goal_is_subset = True
    has_no_cross = has_no_touch = has_no_overlap = True
    for event in events_queue.sweep(stop_x):
        if event.relation is SegmentsRelation.OVERLAP:
            if has_no_overlap:
                has_no_overlap = False
        else:
            if event.from_test:
                if test_is_subset:
                    test_is_subset = False
            elif goal_is_subset:
                goal_is_subset = False
            if has_no_overlap:
                if event.relation is SegmentsRelation.CROSS:
                    if has_no_cross:
                        has_no_cross = False
                elif event.relation is SegmentsRelation.TOUCH:
                    if has_no_touch:
                        has_no_touch = False
    if events_queue:
        if events_queue.peek().from_test:
            test_is_subset = False
        else:
            goal_is_subset = False
    if goal_is_subset:
        return (Relation.EQUAL
                if test_is_subset
                else Relation.COMPOSITE)
    elif test_is_subset:
        return Relation.COMPONENT
    else:
        return (((Relation.DISJOINT
                  if has_no_touch
                  else Relation.TOUCH)
                 if has_no_cross
                 else Relation.CROSS)
                if has_no_overlap
                else Relation.OVERLAP)


def process_closed_linear_queue(events_queue: CompoundEventsQueue,
                                stop_x: Scalar) -> Relation:
    test_is_subset_of_goal = goal_is_subset_of_test = True
    test_boundary_not_in_goal_interior = True
    goal_boundary_not_in_test_interior = True
    has_no_cross = has_no_touch = has_no_overlap = True
    for event in events_queue.sweep(stop_x):
        if (test_is_subset_of_goal
                and event.from_test and event.outside):
            test_is_subset_of_goal = False
        if (goal_is_subset_of_test
                and event.from_goal and event.outside):
            goal_is_subset_of_test = False
        if (test_boundary_not_in_goal_interior
                and event.from_test and event.inside):
            test_boundary_not_in_goal_interior = False
        if (goal_boundary_not_in_test_interior
                and event.from_goal and event.inside):
            goal_boundary_not_in_test_interior = False
        if has_no_cross and event.relation is SegmentsRelation.CROSS:
            has_no_cross = False
        if (has_no_overlap
                and event.relation is SegmentsRelation.OVERLAP):
            has_no_overlap = False
        if has_no_touch and event.relation is SegmentsRelation.TOUCH:
            has_no_touch = False
    if events_queue:
        if events_queue.peek().from_test:
            test_is_subset_of_goal = False
        else:
            goal_is_subset_of_test = False
    if goal_is_subset_of_test:
        return (Relation.EQUAL
                if test_is_subset_of_goal
                else (Relation.COMPOSITE
                      if goal_boundary_not_in_test_interior
                      else ((Relation.DISJOINT
                             if has_no_touch
                             else Relation.TOUCH)
                            if has_no_overlap
                            else Relation.OVERLAP)))
    elif test_is_subset_of_goal:
        return (Relation.COMPONENT
                if test_boundary_not_in_goal_interior
                else ((Relation.DISJOINT
                       if has_no_touch
                       else Relation.TOUCH)
                      if has_no_overlap
                      else Relation.OVERLAP))
    else:
        return (((Relation.DISJOINT
                  if has_no_touch
                  else Relation.TOUCH)
                 if (has_no_cross
                     and (test_boundary_not_in_goal_interior
                          is goal_boundary_not_in_test_interior))
                 else Relation.CROSS)
                if has_no_overlap
                else Relation.OVERLAP)


def process_linear_compound_queue(events_queue: CompoundEventsQueue,
                                  stop_x: Scalar) -> Relation:
    # ``goal`` is a compound object
    # ``test`` is a linear object
    test_not_in_goal_interior = has_no_touch = True
    test_is_subset_of_goal = goal_border_subset_of_test = True
    for event in events_queue.sweep(stop_x):
        if event.relation is SegmentsRelation.CROSS:
            return Relation.CROSS
        elif has_no_touch and event.relation is not SegmentsRelation.DISJOINT:
            has_no_touch = False
        if event.from_test:
            if test_is_subset_of_goal and event.outside:
                test_is_subset_of_goal = False
            if test_not_in_goal_interior and event.inside:
                test_not_in_goal_interior = False
        elif (goal_border_subset_of_test
              and event.relation is not SegmentsRelation.OVERLAP):
            goal_border_subset_of_test = False
    if events_queue:
        if events_queue.peek().from_test:
            if test_is_subset_of_goal:
                test_is_subset_of_goal = False
        elif goal_border_subset_of_test:
            goal_border_subset_of_test = False
    if goal_border_subset_of_test:
        return ((Relation.COMPONENT
                 if test_not_in_goal_interior
                 else Relation.ENCLOSED)
                if test_is_subset_of_goal
                else Relation.TOUCH)
    elif test_is_subset_of_goal:
        return (Relation.COMPONENT
                if test_not_in_goal_interior
                else (Relation.WITHIN
                      if has_no_touch
                      else Relation.ENCLOSED))
    else:
        return ((Relation.DISJOINT
                 if has_no_touch
                 else Relation.TOUCH)
                if test_not_in_goal_interior
                else Relation.CROSS)


def process_compound_queue(events_queue: CompoundEventsQueue,
                           stop_x: Scalar) -> Relation:
    test_boundary_not_in_goal_interior = True
    goal_boundary_not_in_test_interior = True
    boundaries_do_not_intersect = True
    none_overlapping_components = True
    test_is_subset_of_goal = goal_is_subset_of_test = True
    for event in events_queue.sweep(stop_x):
        if event.relation is SegmentsRelation.CROSS:
            return Relation.OVERLAP
        elif (boundaries_do_not_intersect
              and event.relation is not SegmentsRelation.DISJOINT):
            boundaries_do_not_intersect = False
        if event.is_common_region_boundary:
            if none_overlapping_components:
                none_overlapping_components = False
        elif event.inside:
            if none_overlapping_components:
                none_overlapping_components = False
            if event.from_test:
                if test_boundary_not_in_goal_interior:
                    test_boundary_not_in_goal_interior = False
                if goal_is_subset_of_test:
                    goal_is_subset_of_test = False
            else:
                if goal_boundary_not_in_test_interior:
                    goal_boundary_not_in_test_interior = False
                if test_is_subset_of_goal:
                    test_is_subset_of_goal = False
        elif event.outside or event.is_common_polyline_component:
            if test_is_subset_of_goal and event.from_test:
                test_is_subset_of_goal = False
            if goal_is_subset_of_test and event.from_goal:
                goal_is_subset_of_test = False
    if events_queue:
        if events_queue.peek().from_test:
            if test_is_subset_of_goal:
                test_is_subset_of_goal = False
        elif goal_is_subset_of_test:
            goal_is_subset_of_test = False
    if boundaries_do_not_intersect:
        return (Relation.WITHIN
                if test_is_subset_of_goal
                else (Relation.COVER
                      if goal_is_subset_of_test
                      else (Relation.DISJOINT
                            if none_overlapping_components
                            else Relation.OVERLAP)))
    elif test_is_subset_of_goal:
        return (Relation.EQUAL
                if goal_is_subset_of_test
                else (Relation.COMPONENT
                      if test_boundary_not_in_goal_interior
                      else Relation.ENCLOSED))
    elif goal_is_subset_of_test:
        return (Relation.COMPOSITE
                if goal_boundary_not_in_test_interior
                else Relation.ENCLOSES)
    else:
        return (Relation.TOUCH
                if none_overlapping_components
                else Relation.OVERLAP)
