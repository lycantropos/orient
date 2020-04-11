from typing import Tuple

from hypothesis import given

from orient.hints import (Multiregion,
                          Region)
from orient.planar import (Relation,
                           region_in_multiregion,
                           region_in_region)
from tests.utils import equivalence
from . import strategies


@given(strategies.contours_with_multicontours)
def test_basic(region_with_multiregion: Tuple[Region, Multiregion]) -> None:
    region, multiregion = region_with_multiregion

    result = region_in_multiregion(region, multiregion)

    assert isinstance(result, Relation)


@given(strategies.contours)
def test_self(region: Region) -> None:
    assert region_in_multiregion(region, [region]) is Relation.EQUAL


@given(strategies.contours_with_empty_multicontours)
def test_base(region_with_multiregion: Tuple[Region, Multiregion]) -> None:
    region, multiregion = region_with_multiregion

    assert region_in_multiregion(region, multiregion) is Relation.DISJOINT


@given(strategies.contours_with_non_empty_multicontours)
def test_step(region_with_multiregion: Tuple[Region, Multiregion]) -> None:
    region, multiregion = region_with_multiregion
    first_contour, *rest_multiregion = multiregion

    result = region_in_multiregion(region, rest_multiregion)
    next_result = region_in_multiregion(region, multiregion)

    relation_with_first_contour = region_in_region(region, first_contour)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_contour
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.DISJOINT
                       and relation_with_first_contour is Relation.TOUCH
                       or result is Relation.TOUCH
                       and relation_with_first_contour in (Relation.DISJOINT,
                                                           Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or bool(rest_multiregion)
                       and relation_with_first_contour is Relation.EQUAL)
    assert equivalence(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_contour is Relation.OVERLAP
                       or (bool(rest_multiregion)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_contour in (Relation.COVER,
                                                           Relation.ENCLOSES)
                       or result in (Relation.COVER, Relation.ENCLOSES)
                       and relation_with_first_contour is Relation.DISJOINT)
    assert equivalence(next_result is Relation.COVER,
                       (not rest_multiregion or result is Relation.COVER)
                       and relation_with_first_contour is Relation.COVER)
    assert equivalence(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       and relation_with_first_contour in (Relation.ENCLOSES,
                                                           Relation.COVER)
                       or (not rest_multiregion or result is Relation.COVER)
                       and relation_with_first_contour is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.EQUAL,
                       not rest_multiregion
                       and relation_with_first_contour is Relation.EQUAL)
    assert equivalence(next_result is Relation.ENCLOSED,
                       result is Relation.ENCLOSED
                       or relation_with_first_contour is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_contour is Relation.WITHIN)


@given(strategies.contours_with_multicontours)
def test_reversed(region_with_multiregion: Tuple[Region, Multiregion]) -> None:
    region, multiregion = region_with_multiregion

    result = region_in_multiregion(region, multiregion)

    assert result is region_in_multiregion(region, multiregion[::-1])


@given(strategies.contours_with_multicontours)
def test_reversed_multiregion(region_with_multiregion: Tuple[Region,
                                                             Multiregion]
                              ) -> None:
    region, multiregion = region_with_multiregion

    result = region_in_multiregion(region, multiregion)

    assert result is region_in_multiregion(region, [region[::-1]
                                                    for region in
                                                    multiregion])
    assert result is region_in_multiregion(region[::-1], multiregion)