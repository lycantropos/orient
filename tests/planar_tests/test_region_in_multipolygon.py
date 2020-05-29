from typing import Tuple

from hypothesis import given

from orient.hints import (Multipolygon,
                          Region)
from orient.planar import (Relation,
                           contour_in_multipolygon,
                           region_in_multipolygon,
                           region_in_polygon)
from tests.utils import (COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_contour,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         rotations)
from . import strategies


@given(strategies.multipolygons_with_contours)
def test_basic(multipolygon_with_region: Tuple[Multipolygon, Region]) -> None:
    multipolygon, region = multipolygon_with_region

    result = region_in_multipolygon(region, multipolygon)

    assert isinstance(result, Relation)
    assert result in COMPOUND_RELATIONS


@given(strategies.empty_multipolygons_with_contours)
def test_base(multipolygon_with_region: Tuple[Multipolygon, Region]) -> None:
    multipolygon, region = multipolygon_with_region

    assert region_in_multipolygon(region, multipolygon) is Relation.DISJOINT


@given(strategies.non_empty_multipolygons_with_contours)
def test_step(multipolygon_with_region: Tuple[Multipolygon, Region]) -> None:
    multipolygon, region = multipolygon_with_region
    first_polygon, *rest_multipolygon = multipolygon

    result = region_in_multipolygon(region, rest_multipolygon)
    next_result = region_in_multipolygon(region, multipolygon)

    relation_with_first_region = region_in_polygon(region, first_polygon)
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
                       or bool(rest_multipolygon)
                       and relation_with_first_region is Relation.EQUAL)
    assert equivalence(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_region is Relation.OVERLAP
                       or (bool(rest_multipolygon)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_region in (Relation.COVER,
                                                          Relation.ENCLOSES)
                       or result in (Relation.COVER, Relation.ENCLOSES)
                       and relation_with_first_region is Relation.DISJOINT)
    assert equivalence(next_result is Relation.COVER,
                       (not rest_multipolygon or result is Relation.COVER)
                       and relation_with_first_region is Relation.COVER)
    assert equivalence(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       and relation_with_first_region in (Relation.ENCLOSES,
                                                          Relation.COVER)
                       or (not rest_multipolygon or result is Relation.COVER)
                       and relation_with_first_region is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.EQUAL,
                       not rest_multipolygon
                       and relation_with_first_region is Relation.EQUAL)
    assert equivalence(next_result is Relation.ENCLOSED,
                       result is Relation.ENCLOSED
                       or relation_with_first_region is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_region is Relation.WITHIN)


@given(strategies.multipolygons_with_contours)
def test_reversals(multipolygon_with_region: Tuple[Multipolygon, Region]
                   ) -> None:
    multipolygon, region = multipolygon_with_region

    result = region_in_multipolygon(region, multipolygon)

    assert result is region_in_multipolygon(reverse_contour(region),
                                            multipolygon)
    assert result is region_in_multipolygon(region,
                                            reverse_multipolygon(multipolygon))
    assert result is region_in_multipolygon(
            region, reverse_multipolygon_borders(multipolygon))
    assert result is region_in_multipolygon(
            region, reverse_multipolygon_holes(multipolygon))
    assert result is region_in_multipolygon(
            region, reverse_multipolygon_holes_contours(multipolygon))


@given(strategies.multipolygons_with_contours)
def test_rotations(multipolygon_with_region: Tuple[Multipolygon, Region]
                   ) -> None:
    multipolygon, region = multipolygon_with_region

    result = region_in_multipolygon(region, multipolygon)

    assert all(result is region_in_multipolygon(region, rotated)
               for rotated in rotations(multipolygon))


@given(strategies.multipolygons_with_contours)
def test_connection_with_contour_in_multipolygon(multipolygon_with_region
                                                 : Tuple[Multipolygon, Region]
                                                 ) -> None:
    multipolygon, region = multipolygon_with_region

    result = region_in_multipolygon(region, multipolygon)

    contour_relation = contour_in_multipolygon(region, multipolygon)
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
