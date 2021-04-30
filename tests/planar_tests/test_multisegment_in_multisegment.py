from typing import Tuple

from ground.base import Relation
from ground.hints import Multisegment
from hypothesis import given

from orient.planar import (multisegment_in_multisegment,
                           segment_in_multisegment)
from tests.utils import (ASYMMETRIC_LINEAR_RELATIONS,
                         SAME_LINEAR_RELATIONS,
                         SYMMETRIC_SAME_LINEAR_RELATIONS,
                         equivalence,
                         implication,
                         multisegment_pop_left,
                         multisegment_rotations,
                         reverse_multisegment,
                         reverse_multisegment_coordinates,
                         segment_to_multisegment)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: Tuple[Multisegment, Multisegment]) -> None:
    left, right = multisegments_pair

    result = multisegment_in_multisegment(left, right)

    assert isinstance(result, Relation)
    assert result in SAME_LINEAR_RELATIONS


@given(strategies.multisegments)
def test_self(multisegment: Multisegment) -> None:
    assert (multisegment_in_multisegment(multisegment, multisegment)
            is Relation.EQUAL)
    assert all(multisegment_in_multisegment(segment_to_multisegment(segment),
                                            multisegment)
               is Relation.COMPONENT
               for segment in multisegment.segments)


@given(strategies.multisegments_pairs)
def test_relations(multisegments_pair: Tuple[Multisegment, Multisegment]
                   ) -> None:
    left, right = multisegments_pair

    result = multisegment_in_multisegment(left, right)

    complement = multisegment_in_multisegment(right, left)
    assert equivalence(result is complement,
                       result in SYMMETRIC_SAME_LINEAR_RELATIONS)
    assert equivalence(result is not complement,
                       result.complement is complement
                       and result in ASYMMETRIC_LINEAR_RELATIONS
                       and complement in ASYMMETRIC_LINEAR_RELATIONS)


@given(strategies.multisegments_pairs)
def test_step(multisegments_pair: Tuple[Multisegment, Multisegment]) -> None:
    left, right = multisegments_pair
    first_segment, rest_left = multisegment_pop_left(left)

    result = multisegment_in_multisegment(rest_left, right)
    next_result = multisegment_in_multisegment(left, right)

    relation_with_first_segment = segment_in_multisegment(first_segment, right)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_segment
                       is Relation.DISJOINT)
    assert implication(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH)
                       or result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH)
    assert implication(result is Relation.TOUCH
                       and relation_with_first_segment is Relation.DISJOINT
                       or result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH,
                       next_result is Relation.TOUCH)
    assert implication(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH
                            or relation_with_first_segment is Relation.CROSS)
                       or (result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_segment is Relation.CROSS
                       or result is Relation.TOUCH
                       and relation_with_first_segment is Relation.TOUCH)
    assert implication(result is Relation.CROSS
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH
                            or relation_with_first_segment is Relation.CROSS)
                       or (result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_segment is Relation.CROSS,
                       next_result is Relation.CROSS)
    assert implication(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_segment is Relation.OVERLAP
                       or (result is Relation.DISJOINT
                           and bool(rest_left.segments)
                           or result is Relation.TOUCH
                           or result is Relation.CROSS)
                       and relation_with_first_segment is Relation.COMPONENT
                       or result is Relation.COMPONENT
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH
                            or relation_with_first_segment is Relation.CROSS))
    assert implication(next_result is Relation.COMPOSITE,
                       result is Relation.COMPOSITE
                       or relation_with_first_segment is Relation.COMPOSITE
                       or result is Relation.OVERLAP
                       and (relation_with_first_segment is Relation.COMPONENT
                            or relation_with_first_segment is Relation.OVERLAP)
                       or bool(rest_left.segments)
                       and relation_with_first_segment is Relation.EQUAL
                       or result is Relation.EQUAL
                       or result is Relation.COMPONENT
                       and relation_with_first_segment is Relation.OVERLAP)
    assert implication(result is Relation.COMPOSITE
                       or relation_with_first_segment is Relation.COMPOSITE
                       or bool(rest_left.segments)
                       and relation_with_first_segment is Relation.EQUAL
                       or result is Relation.EQUAL,
                       next_result is Relation.COMPOSITE)
    assert implication(next_result is Relation.EQUAL,
                       not rest_left.segments
                       and relation_with_first_segment is Relation.EQUAL
                       or result is relation_with_first_segment
                       is Relation.COMPONENT)
    assert implication(not rest_left.segments
                       and relation_with_first_segment is Relation.EQUAL,
                       next_result is Relation.EQUAL)
    assert implication(next_result is Relation.COMPONENT,
                       (not rest_left.segments
                        or result is Relation.COMPONENT)
                       and relation_with_first_segment is Relation.COMPONENT)
    assert implication(not rest_left.segments
                       and relation_with_first_segment is Relation.COMPONENT,
                       next_result is Relation.COMPONENT)


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: Tuple[Multisegment, Multisegment]
                   ) -> None:
    left, right = multisegments_pair

    result = multisegment_in_multisegment(left, right)

    assert result is multisegment_in_multisegment(reverse_multisegment(left),
                                                  right)
    assert result is multisegment_in_multisegment(left,
                                                  reverse_multisegment(right))
    assert result is multisegment_in_multisegment(
            reverse_multisegment_coordinates(left),
            reverse_multisegment_coordinates(right))


@given(strategies.multisegments_pairs)
def test_rotations(multisegments_pair: Tuple[Multisegment, Multisegment]
                   ) -> None:
    left, right = multisegments_pair

    result = multisegment_in_multisegment(left, right)

    assert all(result is multisegment_in_multisegment(rotated, right)
               for rotated in multisegment_rotations(left))
    assert all(result is multisegment_in_multisegment(left, rotated)
               for rotated in multisegment_rotations(right))
