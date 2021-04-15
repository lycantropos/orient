from typing import Tuple

from ground.base import Relation
from ground.hints import (Contour,
                          Multisegment)
from hypothesis import given

from orient.planar import (multisegment_in_contour,
                           segment_in_contour)
from tests.utils import (SAME_LINEAR_RELATIONS,
                         contour_rotations,
                         contour_to_multisegment,
                         equivalence,
                         implication,
                         multisegment_pop_left,
                         multisegment_rotations,
                         reverse_contour,
                         reverse_contour_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates)
from . import strategies


@given(strategies.contours_with_multisegments)
def test_basic(contour_with_multisegment: Tuple[Contour, Multisegment]
               ) -> None:
    contour, multisegment = contour_with_multisegment

    result = multisegment_in_contour(multisegment, contour)

    assert isinstance(result, Relation)
    assert result in SAME_LINEAR_RELATIONS


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert multisegment_in_contour(contour_to_multisegment(contour),
                                   contour) is Relation.EQUAL


@given(strategies.contours_with_empty_multisegments)
def test_base(contour_with_multisegment: Tuple[Contour, Multisegment]) -> None:
    contour, multisegment = contour_with_multisegment

    assert multisegment_in_contour(multisegment, contour) is Relation.DISJOINT


@given(strategies.contours_with_non_empty_multisegments)
def test_step(contour_with_multisegment: Tuple[Contour, Multisegment]) -> None:
    contour, multisegment = contour_with_multisegment
    first_segment, rest_multisegment = multisegment_pop_left(multisegment)

    result = multisegment_in_contour(rest_multisegment, contour)
    next_result = multisegment_in_contour(multisegment, contour)

    relation_with_first_segment = segment_in_contour(first_segment, contour)
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
                           and bool(rest_multisegment.segments)
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
                       or bool(rest_multisegment.segments)
                       and relation_with_first_segment is Relation.EQUAL
                       or result is Relation.EQUAL
                       or result is Relation.COMPONENT
                       and relation_with_first_segment is Relation.OVERLAP
                       or result is Relation.OVERLAP
                       and relation_with_first_segment is Relation.COMPONENT)
    assert implication(result is Relation.COMPOSITE
                       or relation_with_first_segment is Relation.COMPOSITE
                       or bool(rest_multisegment.segments)
                       and relation_with_first_segment is Relation.EQUAL
                       or result is Relation.EQUAL,
                       next_result is Relation.COMPOSITE)
    assert implication(next_result is Relation.EQUAL,
                       not rest_multisegment.segments
                       and relation_with_first_segment is Relation.EQUAL
                       or result is relation_with_first_segment
                       is Relation.COMPONENT)
    assert implication(not rest_multisegment.segments
                       and relation_with_first_segment is Relation.EQUAL,
                       next_result is Relation.EQUAL)
    assert implication(next_result is Relation.COMPONENT,
                       (not rest_multisegment.segments
                        or result is Relation.COMPONENT)
                       and relation_with_first_segment is Relation.COMPONENT)
    assert implication(not rest_multisegment.segments
                       and relation_with_first_segment is Relation.COMPONENT,
                       next_result is Relation.COMPONENT)


@given(strategies.contours_with_multisegments)
def test_reversals(contour_with_multisegment: Tuple[Contour, Multisegment]
                   ) -> None:
    contour, multisegment = contour_with_multisegment

    result = multisegment_in_contour(multisegment, contour)

    assert result is multisegment_in_contour(
            reverse_multisegment(multisegment), contour)
    assert result is multisegment_in_contour(multisegment,
                                             reverse_contour(contour))
    assert result is multisegment_in_contour(
            reverse_multisegment_coordinates(multisegment),
            reverse_contour_coordinates(contour))


@given(strategies.contours_with_multisegments)
def test_rotations(contour_with_multisegment: Tuple[Contour, Multisegment]
                   ) -> None:
    contour, multisegment = contour_with_multisegment

    result = multisegment_in_contour(multisegment, contour)

    assert all(result is multisegment_in_contour(multisegment, rotated)
               for rotated in contour_rotations(contour))
    assert all(result is multisegment_in_contour(rotated, contour)
               for rotated in multisegment_rotations(multisegment))
