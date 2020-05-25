from typing import Tuple

from hypothesis import given

from orient.core.multiregion import to_segments
from orient.hints import (Multiregion,
                          Multisegment)
from orient.planar import (Relation,
                           multisegment_in_multiregion,
                           segment_in_multiregion)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_multicontour,
                         reverse_multicontour_contours,
                         reverse_multisegment,
                         rotations)
from . import strategies


@given(strategies.multicontours_with_multisegments)
def test_basic(multiregion_with_multisegment: Tuple[Multiregion, Multisegment]
               ) -> None:
    multiregion, multisegment = multiregion_with_multisegment

    result = multisegment_in_multiregion(multisegment, multiregion)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.multicontours)
def test_edges(multiregion: Multiregion) -> None:
    assert multisegment_in_multiregion(list(to_segments(multiregion)),
                                       multiregion) is (Relation.COMPONENT
                                                        if multiregion
                                                        else Relation.DISJOINT)


@given(strategies.multicontours_with_empty_multisegments)
def test_base(multiregion_with_multisegment: Tuple[Multiregion, Multisegment]
              ) -> None:
    multiregion, multisegment = multiregion_with_multisegment

    result = multisegment_in_multiregion(multisegment, multiregion)

    assert result is Relation.DISJOINT


@given(strategies.multicontours_with_non_empty_multisegments)
def test_step(multiregion_with_multisegment: Tuple[Multiregion, Multisegment]
              ) -> None:
    multiregion, multisegment = multiregion_with_multisegment
    first_segment, *rest_multisegment = multisegment

    result = multisegment_in_multiregion(rest_multisegment, multiregion)
    next_result = multisegment_in_multiregion(multisegment, multiregion)

    relation_with_first_segment = segment_in_multiregion(first_segment,
                                                         multiregion)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_segment
                       is Relation.DISJOINT)
    assert implication(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and relation_with_first_segment is not Relation.CROSS
                       or result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH)
    assert implication(result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH
                       or result is Relation.TOUCH
                       and relation_with_first_segment is Relation.DISJOINT,
                       next_result is Relation.TOUCH)
    assert equivalence(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       or relation_with_first_segment is Relation.CROSS
                       or (bool(rest_multisegment)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and (relation_with_first_segment is Relation.ENCLOSED
                            or relation_with_first_segment is Relation.WITHIN)
                       or (result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       (not rest_multisegment or result is Relation.COMPONENT)
                       and relation_with_first_segment is Relation.COMPONENT)
    assert equivalence(next_result is Relation.ENCLOSED,
                       not rest_multisegment
                       and relation_with_first_segment is Relation.ENCLOSED
                       or (result is Relation.COMPONENT
                           or result is Relation.ENCLOSED)
                       and (relation_with_first_segment is Relation.ENCLOSED
                            or relation_with_first_segment is Relation.WITHIN)
                       or (result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and relation_with_first_segment is Relation.COMPONENT
                       or result is Relation.WITHIN
                       and relation_with_first_segment is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       (not rest_multisegment or result is Relation.WITHIN)
                       and relation_with_first_segment is Relation.WITHIN)


@given(strategies.multicontours_with_multisegments)
def test_reversals(multiregion_with_multisegment
                   : Tuple[Multiregion, Multisegment]) -> None:
    multiregion, multisegment = multiregion_with_multisegment

    result = multisegment_in_multiregion(multisegment, multiregion)

    assert result is multisegment_in_multiregion(
            reverse_multisegment(multisegment), multiregion)
    assert result is multisegment_in_multiregion(
            multisegment, reverse_multicontour(multiregion))
    assert result is multisegment_in_multiregion(
            multisegment, reverse_multicontour_contours(multiregion))


@given(strategies.multicontours_with_multisegments)
def test_rotations(multiregion_with_multisegment
                   : Tuple[Multiregion, Multisegment]) -> None:
    multiregion, multisegment = multiregion_with_multisegment

    result = multisegment_in_multiregion(multisegment, multiregion)

    assert all(result is multisegment_in_multiregion(multisegment, rotated)
               for rotated in rotations(multiregion))
    assert all(result is multisegment_in_multiregion(rotated, multiregion)
               for rotated in rotations(multisegment))
