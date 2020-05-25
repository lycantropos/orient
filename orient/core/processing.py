from robust.linear import SegmentsRelationship

from orient.hints import Coordinate
from .relation import Relation
from .sweep import (ClosedSweeper,
                    OpenSweeper)


def process_open_linear_queue(sweeper: OpenSweeper,
                              stop_x: Coordinate) -> Relation:
    test_is_subset = goal_is_subset = True
    has_no_cross = has_no_touch = has_no_overlap = True
    for event in sweeper.sweep(stop_x):
        if event.relationship is SegmentsRelationship.OVERLAP:
            if has_no_overlap:
                has_no_overlap = False
        else:
            if event.from_test:
                if test_is_subset:
                    test_is_subset = False
            elif goal_is_subset:
                goal_is_subset = False
            if has_no_overlap:
                if event.relationship is SegmentsRelationship.CROSS:
                    if has_no_cross:
                        has_no_cross = False
                elif event.relationship is SegmentsRelationship.TOUCH:
                    if has_no_touch:
                        has_no_touch = False
    if sweeper:
        if sweeper.peek().from_test:
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


def process_closed_linear_queue(sweeper: ClosedSweeper,
                                stop_x: Coordinate) -> Relation:
    test_is_subset_of_goal = goal_is_subset_of_test = True
    test_boundary_not_in_goal_interior = True
    goal_boundary_not_in_test_interior = True
    has_no_cross = has_no_touch = has_no_overlap = True
    for event in sweeper.sweep(stop_x):
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
        if has_no_cross and event.relationship is SegmentsRelationship.CROSS:
            has_no_cross = False
        if (has_no_overlap
                and event.relationship is SegmentsRelationship.OVERLAP):
            has_no_overlap = False
        if has_no_touch and event.relationship is SegmentsRelationship.TOUCH:
            has_no_touch = False
    if sweeper:
        if sweeper.peek().from_test:
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


def process_linear_compound_queue(sweeper: ClosedSweeper,
                                  stop_x: Coordinate) -> Relation:
    # ``goal`` is a compound object
    # ``test`` is a linear object
    test_not_in_goal_interior = has_no_touch = True
    test_is_subset_of_goal = goal_border_subset_of_test = True
    for event in sweeper.sweep(stop_x):
        if event.relationship is SegmentsRelationship.CROSS:
            return Relation.CROSS
        elif (has_no_touch
              and event.relationship is not SegmentsRelationship.NONE):
            has_no_touch = False

        if event.from_test:
            if test_is_subset_of_goal and event.outside:
                test_is_subset_of_goal = False
            if test_not_in_goal_interior and event.inside:
                test_not_in_goal_interior = False
        elif (goal_border_subset_of_test
              and event.relationship is not SegmentsRelationship.OVERLAP):
            goal_border_subset_of_test = False

    if sweeper:
        if sweeper.peek().from_test:
            test_is_subset_of_goal = False
        else:
            goal_border_subset_of_test = False
    if goal_border_subset_of_test:
        return (Relation.COMPONENT
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


def process_compound_queue(sweeper: ClosedSweeper,
                           stop_x: Coordinate) -> Relation:
    test_boundary_in_goal_interior = goal_boundary_in_test_interior = False
    boundaries_do_not_intersect, boundary_in_other_interior = True, False
    test_is_subset_of_goal = goal_is_subset_of_test = True
    for event in sweeper.sweep(stop_x):
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
    if sweeper:
        if sweeper.peek().from_test:
            test_is_subset_of_goal = False
        else:
            goal_is_subset_of_test = False
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
