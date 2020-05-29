from typing import Tuple

from hypothesis import given

from orient.hints import Multiregion
from orient.planar import (Relation,
                           multiregion_in_multiregion,
                           region_in_multiregion)
from tests.utils import (ASYMMETRIC_COMPOUND_RELATIONS,
                         COMPOUND_RELATIONS,
                         SYMMETRIC_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_multicontour,
                         reverse_multicontour_contours,
                         rotations)
from . import strategies


@given(strategies.multicontours_pairs)
def test_basic(multiregions_pair: Tuple[Multiregion, Multiregion]) -> None:
    multiregion, multiregion = multiregions_pair

    result = multiregion_in_multiregion(multiregion, multiregion)

    assert isinstance(result, Relation)
    assert result in COMPOUND_RELATIONS


@given(strategies.multicontours)
def test_self(multiregion: Multiregion) -> None:
    assert (multiregion_in_multiregion(multiregion, multiregion)
            is (Relation.EQUAL
                if multiregion
                else Relation.DISJOINT))


@given(strategies.non_empty_multicontours)
def test_elements(multiregion: Multiregion) -> None:
    assert equivalence(all(multiregion_in_multiregion([region], multiregion)
                           is Relation.EQUAL
                           for region in multiregion),
                       len(multiregion) == 1)
    assert equivalence(all(multiregion_in_multiregion([region], multiregion)
                           is Relation.COMPONENT
                           for region in multiregion),
                       len(multiregion) > 1)


@given(strategies.multicontours_pairs)
def test_relations(multiregions_pair: Tuple[Multiregion, Multiregion]) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = multiregion_in_multiregion(left_multiregion, right_multiregion)

    complement = multiregion_in_multiregion(right_multiregion,
                                            left_multiregion)
    assert equivalence(result is complement,
                       result in SYMMETRIC_COMPOUND_RELATIONS)
    assert equivalence(result is not complement
                       and result.complement is complement,
                       result in ASYMMETRIC_COMPOUND_RELATIONS
                       and complement in ASYMMETRIC_COMPOUND_RELATIONS)


@given(strategies.empty_multicontours_with_multicontours)
def test_base(multiregions_pair: Tuple[Multiregion, Multiregion]) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    assert multiregion_in_multiregion(left_multiregion,
                                      right_multiregion) is Relation.DISJOINT


@given(strategies.non_empty_multicontours_with_multicontours)
def test_step(multiregions_pair: Tuple[Multiregion, Multiregion]) -> None:
    left_multiregion, right_multiregion = multiregions_pair
    first_region, *rest_left_multiregion = left_multiregion

    result = multiregion_in_multiregion(rest_left_multiregion,
                                        right_multiregion)
    next_result = multiregion_in_multiregion(left_multiregion,
                                             right_multiregion)

    relation_with_first_region = region_in_multiregion(first_region,
                                                       right_multiregion)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_region
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and (relation_with_first_region is Relation.DISJOINT
                            or relation_with_first_region is Relation.TOUCH)
                       or result is Relation.DISJOINT
                       and relation_with_first_region is Relation.TOUCH)
    assert implication(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_region is Relation.OVERLAP
                       or (bool(rest_left_multiregion)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and (relation_with_first_region is Relation.COMPONENT
                            or relation_with_first_region is Relation.ENCLOSED
                            or relation_with_first_region is Relation.WITHIN)
                       or (result is Relation.COMPONENT
                           or result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and (relation_with_first_region is Relation.DISJOINT
                            or relation_with_first_region is Relation.TOUCH))
    assert implication(result is Relation.OVERLAP
                       and (relation_with_first_region is Relation.DISJOINT
                            or relation_with_first_region is Relation.TOUCH
                            or relation_with_first_region is Relation.ENCLOSED
                            or relation_with_first_region is Relation.WITHIN)
                       or (result is Relation.DISJOINT
                           or result is Relation.TOUCH
                           or result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and relation_with_first_region is Relation.OVERLAP
                       or (bool(rest_left_multiregion)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and (relation_with_first_region is Relation.COMPONENT
                            or relation_with_first_region is Relation.ENCLOSED
                            or relation_with_first_region is Relation.WITHIN)
                       or (result is Relation.COMPONENT
                           or result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and (relation_with_first_region is Relation.DISJOINT
                            or relation_with_first_region is Relation.TOUCH),
                       next_result is Relation.OVERLAP)
    assert equivalence(next_result is Relation.COVER,
                       result is Relation.COVER
                       or relation_with_first_region is Relation.COVER)
    assert implication(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       or relation_with_first_region is Relation.ENCLOSES
                       or result is Relation.OVERLAP
                       and (relation_with_first_region is Relation.COMPONENT
                            or relation_with_first_region is Relation.OVERLAP)
                       or result is Relation.COMPONENT
                       and relation_with_first_region is Relation.OVERLAP)
    assert implication(result is Relation.ENCLOSES
                       and (relation_with_first_region is Relation.DISJOINT
                            or relation_with_first_region is Relation.TOUCH)
                       or (result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_region is Relation.ENCLOSES,
                       next_result is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.COMPOSITE,
                       result is Relation.COMPOSITE or result is Relation.EQUAL
                       or (relation_with_first_region is Relation.COMPOSITE
                           or bool(rest_left_multiregion)
                           and relation_with_first_region is Relation.EQUAL))
    assert implication(result is relation_with_first_region
                       is Relation.COMPONENT,
                       next_result is Relation.EQUAL
                       or next_result is Relation.COMPONENT)
    assert implication(not rest_left_multiregion
                       and relation_with_first_region is Relation.EQUAL,
                       next_result is Relation.EQUAL)
    assert implication(not rest_left_multiregion
                       and relation_with_first_region is Relation.COMPONENT,
                       next_result is Relation.COMPONENT)
    assert equivalence(next_result is Relation.ENCLOSED,
                       (not rest_left_multiregion
                        or result is Relation.COMPONENT
                        or result is Relation.ENCLOSED
                        or result is Relation.WITHIN)
                       and relation_with_first_region is Relation.ENCLOSED
                       or result is Relation.ENCLOSED
                       and (relation_with_first_region is Relation.COMPONENT
                            or relation_with_first_region is Relation.WITHIN))
    assert equivalence(next_result is Relation.WITHIN,
                       (not rest_left_multiregion or result is Relation.WITHIN)
                       and relation_with_first_region is Relation.WITHIN)


@given(strategies.multicontours_pairs)
def test_reversals(multiregions_pair: Tuple[Multiregion, Multiregion]) -> None:
    left, right = multiregions_pair

    result = multiregion_in_multiregion(left, right)

    assert result is multiregion_in_multiregion(reverse_multicontour(left),
                                                right)
    assert result is multiregion_in_multiregion(left,
                                                reverse_multicontour(right))
    assert result is multiregion_in_multiregion(
            reverse_multicontour_contours(left), right)
    assert result is multiregion_in_multiregion(
            left, reverse_multicontour_contours(right))


@given(strategies.multicontours_pairs)
def test_rotations(multiregions_pair: Tuple[Multiregion, Multiregion]) -> None:
    left, right = multiregions_pair

    result = multiregion_in_multiregion(left, right)

    assert all(result is multiregion_in_multiregion(rotated, right)
               for rotated in rotations(left))
    assert all(result is multiregion_in_multiregion(left, rotated)
               for rotated in rotations(right))
