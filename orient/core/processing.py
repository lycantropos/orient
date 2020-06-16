from collections import defaultdict
from typing import List

from robust.linear import SegmentsRelationship

from orient.hints import Coordinate
from .relation import Relation
from .sweep import (ComplexCompoundSweeper,
                    CompoundSweeper,
                    LinearSweeper)


def process_open_linear_queue(sweeper: LinearSweeper,
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


def process_closed_linear_queue(sweeper: CompoundSweeper,
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


def process_linear_compound_queue(sweeper: CompoundSweeper,
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


def process_compound_queue(sweeper: CompoundSweeper,
                           stop_x: Coordinate) -> Relation:
    test_boundary_not_in_goal_interior = True
    goal_boundary_not_in_test_interior = True
    boundaries_do_not_intersect = True
    all_test_segments_in_goal = all_goal_segments_in_test = True
    for event in sweeper.sweep(stop_x):
        if event.relationship is SegmentsRelationship.CROSS:
            return Relation.OVERLAP
        if (boundaries_do_not_intersect
                and event.relationship is not SegmentsRelationship.NONE):
            boundaries_do_not_intersect = False
        if event.inside:
            if test_boundary_not_in_goal_interior and event.from_test:
                test_boundary_not_in_goal_interior = False
            if goal_boundary_not_in_test_interior and event.from_goal:
                goal_boundary_not_in_test_interior = False
        elif event.outside:
            if all_test_segments_in_goal and event.from_test:
                all_test_segments_in_goal = False
            if all_goal_segments_in_test and event.from_goal:
                all_goal_segments_in_test = False
    if sweeper:
        if sweeper.peek().from_test:
            all_test_segments_in_goal = False
        else:
            all_goal_segments_in_test = False
    if boundaries_do_not_intersect:
        return ((Relation.WITHIN
                 if goal_boundary_not_in_test_interior
                 else Relation.OVERLAP)
                if all_test_segments_in_goal
                else ((Relation.COVER
                       if test_boundary_not_in_goal_interior
                       else Relation.OVERLAP)
                      if all_goal_segments_in_test
                      else (Relation.DISJOINT
                            if (test_boundary_not_in_goal_interior
                                and goal_boundary_not_in_test_interior)
                            else Relation.OVERLAP)))
    elif all_test_segments_in_goal:
        return (Relation.EQUAL
                if all_goal_segments_in_test
                else ((Relation.COMPONENT
                       if goal_boundary_not_in_test_interior
                       else Relation.OVERLAP)
                      if test_boundary_not_in_goal_interior
                      else (Relation.ENCLOSED
                            if goal_boundary_not_in_test_interior
                            else Relation.OVERLAP)))
    elif all_goal_segments_in_test:
        return ((Relation.COMPOSITE
                 if test_boundary_not_in_goal_interior
                 else Relation.OVERLAP)
                if goal_boundary_not_in_test_interior
                else (Relation.ENCLOSES
                      if test_boundary_not_in_goal_interior
                      else Relation.OVERLAP))
    else:
        return (Relation.TOUCH
                if (test_boundary_not_in_goal_interior
                    and goal_boundary_not_in_test_interior)
                else Relation.OVERLAP)


def process_complex_compound_queue(sweeper: ComplexCompoundSweeper,
                                   stop_x: Coordinate,
                                   test_components_sizes: List[int]
                                   ) -> Relation:
    test_boundary_not_in_goal_interior = True
    goal_boundary_not_in_test_interior = True
    boundaries_do_not_intersect = True
    all_test_segments_in_goal = all_goal_segments_in_test = True
    common_boundary_segments_counts = defaultdict(int)
    for event in sweeper.sweep(stop_x):
        if event.relationship is SegmentsRelationship.CROSS:
            return Relation.OVERLAP
        if (boundaries_do_not_intersect
                and event.relationship is not SegmentsRelationship.NONE):
            boundaries_do_not_intersect = False
        if event.boundary:
            if event.from_test:
                common_boundary_segments_counts[event.component_id] += 1
        elif event.inside:
            if test_boundary_not_in_goal_interior and event.from_test:
                test_boundary_not_in_goal_interior = False
            if goal_boundary_not_in_test_interior and event.from_goal:
                goal_boundary_not_in_test_interior = False
        elif event.outside:
            if all_test_segments_in_goal and event.from_test:
                all_test_segments_in_goal = False
            if all_goal_segments_in_test and event.from_goal:
                all_goal_segments_in_test = False
    if sweeper:
        if sweeper.peek().from_test:
            all_test_segments_in_goal = False
        else:
            all_goal_segments_in_test = False
    if boundaries_do_not_intersect:
        return ((Relation.WITHIN
                 if goal_boundary_not_in_test_interior
                 else Relation.OVERLAP)
                if all_test_segments_in_goal
                else ((Relation.COVER
                       if test_boundary_not_in_goal_interior
                       else Relation.OVERLAP)
                      if all_goal_segments_in_test
                      else (Relation.DISJOINT
                            if (test_boundary_not_in_goal_interior
                                and goal_boundary_not_in_test_interior)
                            else Relation.OVERLAP)))
    elif all_test_segments_in_goal:
        return (Relation.EQUAL
                if all_goal_segments_in_test
                else ((Relation.COMPONENT
                       if goal_boundary_not_in_test_interior
                       else Relation.OVERLAP)
                      if test_boundary_not_in_goal_interior
                      else (Relation.ENCLOSED
                            if goal_boundary_not_in_test_interior
                            else Relation.OVERLAP)))
    elif all_goal_segments_in_test:
        return ((Relation.COMPOSITE
                 if test_boundary_not_in_goal_interior
                 else Relation.OVERLAP)
                if goal_boundary_not_in_test_interior
                else (Relation.ENCLOSES
                      if test_boundary_not_in_goal_interior
                      else Relation.OVERLAP))
    else:
        return (Relation.TOUCH
                if (test_boundary_not_in_goal_interior
                    and goal_boundary_not_in_test_interior
                    and all(count < test_components_sizes[component_id]
                            for component_id, count
                            in common_boundary_segments_counts.items()))
                else Relation.OVERLAP)
