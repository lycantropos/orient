from typing import Tuple

from hypothesis import given

from orient.hints import (Multiregion,
                          Region)
from orient.planar import (Relation,
                           contour_in_multiregion,
                           region_in_multiregion,
                           region_in_region)
from tests.utils import (COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_contour,
                         reverse_multicontour,
                         reverse_multicontour_contours,
                         rotations)
from . import strategies


@given(strategies.multiregions_with_contours)
def test_basic(multiregion_with_region: Tuple[Multiregion, Region]) -> None:
    multiregion, region = multiregion_with_region

    result = region_in_multiregion(region, multiregion)

    assert isinstance(result, Relation)
    assert result in COMPOUND_RELATIONS


@given(strategies.multiregions)
def test_self(multiregion: Multiregion) -> None:
    assert equivalence(bool(multiregion)
                       and all(region_in_multiregion(element, multiregion)
                               is Relation.EQUAL
                               for element in multiregion),
                       len(multiregion) == 1)
    assert equivalence(all(region_in_multiregion(element, multiregion)
                           is Relation.COMPONENT
                           for element in multiregion),
                       len(multiregion) != 1)


@given(strategies.empty_multiregions_with_contours)
def test_base(multiregion_with_region: Tuple[Multiregion, Region]) -> None:
    multiregion, region = multiregion_with_region

    assert region_in_multiregion(region, multiregion) is Relation.DISJOINT


@given(strategies.non_empty_multiregions_with_contours)
def test_step(multiregion_with_region: Tuple[Multiregion, Region]) -> None:
    multiregion, region = multiregion_with_region
    first_region, *rest_multiregion = multiregion

    result = region_in_multiregion(region, rest_multiregion)
    next_result = region_in_multiregion(region, multiregion)

    relation_with_first_region = region_in_region(region, first_region)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_region
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.DISJOINT
                       and relation_with_first_region is Relation.TOUCH
                       or result is Relation.TOUCH
                       and relation_with_first_region in (Relation.DISJOINT,
                                                          Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or bool(rest_multiregion)
                       and relation_with_first_region is Relation.EQUAL)
    assert equivalence(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_region is Relation.OVERLAP
                       or (bool(rest_multiregion)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_region in (Relation.COVER,
                                                          Relation.ENCLOSES)
                       or result in (Relation.COVER, Relation.ENCLOSES)
                       and relation_with_first_region is Relation.DISJOINT)
    assert equivalence(next_result is Relation.COVER,
                       (not rest_multiregion or result is Relation.COVER)
                       and relation_with_first_region is Relation.COVER)
    assert equivalence(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       and relation_with_first_region in (Relation.ENCLOSES,
                                                          Relation.COVER)
                       or (not rest_multiregion or result is Relation.COVER)
                       and relation_with_first_region is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.EQUAL,
                       not rest_multiregion
                       and relation_with_first_region is Relation.EQUAL)
    assert equivalence(next_result is Relation.ENCLOSED,
                       result is Relation.ENCLOSED
                       or relation_with_first_region is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_region is Relation.WITHIN)


@given(strategies.multiregions_with_contours)
def test_reversals(multiregion_with_region: Tuple[Multiregion, Region]
                   ) -> None:
    multiregion, region = multiregion_with_region

    result = region_in_multiregion(region, multiregion)

    assert result is region_in_multiregion(reverse_contour(region),
                                           multiregion)
    assert result is region_in_multiregion(region,
                                           reverse_multicontour(multiregion))
    assert result is region_in_multiregion(
            region, reverse_multicontour_contours(multiregion))


@given(strategies.multiregions_with_contours)
def test_rotations(multiregion_with_region: Tuple[Multiregion, Region]
                   ) -> None:
    multiregion, region = multiregion_with_region

    result = region_in_multiregion(region, multiregion)

    assert all(result is region_in_multiregion(region, rotated)
               for rotated in rotations(multiregion))


@given(strategies.multiregions_with_contours)
def test_connection_with_contour_in_multiregion(multiregion_with_region
                                                : Tuple[Multiregion, Region]
                                                ) -> None:
    multiregion, region = multiregion_with_region

    result = region_in_multiregion(region, multiregion)

    contour_relation = contour_in_multiregion(region, multiregion)
    assert implication(result is Relation.DISJOINT
                       or result is Relation.COVER,
                       contour_relation is Relation.DISJOINT)
    assert implication(contour_relation is Relation.DISJOINT,
                       result is Relation.DISJOINT
                       or result is Relation.OVERLAP
                       or result is Relation.COVER)
    assert implication(result is Relation.TOUCH
                       or result is Relation.ENCLOSES
                       or result is Relation.COMPOSITE,
                       contour_relation is Relation.TOUCH)
    assert implication(contour_relation is Relation.TOUCH,
                       result is Relation.TOUCH
                       or result is Relation.ENCLOSES
                       or result is Relation.OVERLAP
                       or result is Relation.COMPOSITE)
    assert implication(result is Relation.OVERLAP,
                       contour_relation is Relation.DISJOINT
                       or contour_relation is Relation.CROSS
                       or contour_relation is Relation.TOUCH)
    assert implication(contour_relation is Relation.CROSS,
                       result is Relation.OVERLAP)
    assert equivalence(result is Relation.COMPONENT
                       or result is Relation.EQUAL,
                       contour_relation is Relation.COMPONENT)
    assert equivalence(result is Relation.ENCLOSED,
                       contour_relation is Relation.ENCLOSED)
    assert equivalence(result is Relation.WITHIN,
                       contour_relation is Relation.WITHIN)
