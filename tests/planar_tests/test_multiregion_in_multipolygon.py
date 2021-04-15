from typing import Tuple

from ground.base import Relation
from ground.hints import Multipolygon
from hypothesis import given

from orient.hints import Multiregion
from orient.planar import (multiregion_in_multipolygon,
                           region_in_multipolygon)
from tests.utils import (MULTIPART_COMPOUND_RELATIONS,
                         equivalence,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_multiregion,
                         sequence_rotations)
from . import strategies


@given(strategies.multipolygons_with_multiregions)
def test_basic(multiregion_with_multipolygon: Tuple[Multipolygon, Multiregion]
               ) -> None:
    multipolygon, multiregion = multiregion_with_multipolygon

    result = multiregion_in_multipolygon(multiregion, multipolygon)

    assert isinstance(result, Relation)
    assert result in MULTIPART_COMPOUND_RELATIONS


@given(strategies.non_empty_multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    multipolygon_has_holes = any(polygon.holes
                                 for polygon in multipolygon.polygons)
    assert (multiregion_in_multipolygon([polygon.border
                                         for polygon in multipolygon.polygons],
                                        multipolygon)
            is (Relation.ENCLOSES
                if multipolygon_has_holes
                else Relation.EQUAL))
    assert (multiregion_in_multipolygon([hole
                                         for polygon in multipolygon.polygons
                                         for hole in polygon.holes],
                                        multipolygon)
            is (Relation.TOUCH
                if multipolygon_has_holes
                else Relation.DISJOINT))


@given(strategies.multipolygons_with_empty_multiregions)
def test_base(multiregion_with_multipolygon: Tuple[Multipolygon, Multiregion]
              ) -> None:
    multipolygon, multiregion = multiregion_with_multipolygon

    assert multiregion_in_multipolygon(multiregion,
                                       multipolygon) is Relation.DISJOINT


@given(strategies.multipolygons_with_non_empty_multiregions)
def test_step(multiregion_with_multipolygon: Tuple[Multipolygon, Multiregion]
              ) -> None:
    multipolygon, multiregion = multiregion_with_multipolygon
    first_region, *rest_multiregion = multiregion

    result = multiregion_in_multipolygon(rest_multiregion, multipolygon)
    next_result = multiregion_in_multipolygon(multiregion, multipolygon)

    relation_with_first_region = region_in_multipolygon(first_region,
                                                        multipolygon)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_region
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and (relation_with_first_region is Relation.DISJOINT
                            or relation_with_first_region is Relation.TOUCH)
                       or result is Relation.DISJOINT
                       and relation_with_first_region is Relation.TOUCH)
    assert equivalence(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_region is Relation.OVERLAP
                       or (bool(rest_multiregion)
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
    assert equivalence(next_result is Relation.COVER,
                       result is Relation.COVER
                       or relation_with_first_region is Relation.COVER)
    assert equivalence(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       or relation_with_first_region is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.COMPOSITE,
                       result is Relation.COMPOSITE or result is Relation.EQUAL
                       or (relation_with_first_region is Relation.COMPOSITE
                           or bool(rest_multiregion)
                           and relation_with_first_region is Relation.EQUAL))
    assert equivalence(next_result is Relation.EQUAL,
                       not rest_multiregion
                       and relation_with_first_region is Relation.EQUAL)
    assert equivalence(next_result is Relation.COMPONENT,
                       (not rest_multiregion or result is Relation.COMPONENT)
                       and relation_with_first_region is Relation.COMPONENT)
    assert equivalence(next_result is Relation.ENCLOSED,
                       (not rest_multiregion or result is Relation.COMPONENT
                        or result is Relation.ENCLOSED
                        or result is Relation.WITHIN)
                       and relation_with_first_region is Relation.ENCLOSED
                       or result is Relation.ENCLOSED
                       and (relation_with_first_region is Relation.COMPONENT
                            or relation_with_first_region is Relation.WITHIN))
    assert equivalence(next_result is Relation.WITHIN,
                       (not rest_multiregion or result is Relation.WITHIN)
                       and relation_with_first_region is Relation.WITHIN)


@given(strategies.multipolygons_with_multiregions)
def test_reversals(multipolygon_with_multiregion
                   : Tuple[Multipolygon, Multiregion]) -> None:
    multipolygon, multiregion = multipolygon_with_multiregion

    result = multiregion_in_multipolygon(multiregion, multipolygon)

    assert result is multiregion_in_multipolygon(
            reverse_multiregion(multiregion), multipolygon)
    assert result is multiregion_in_multipolygon(
            multiregion, reverse_multipolygon_borders(multipolygon))
    assert result is multiregion_in_multipolygon(
            multiregion, reverse_multipolygon_holes(multipolygon))
    assert result is multiregion_in_multipolygon(
            multiregion, reverse_multipolygon_holes_contours(multipolygon))


@given(strategies.multipolygons_with_multiregions)
def test_rotations(multipolygon_with_multiregion
                   : Tuple[Multipolygon, Multiregion]) -> None:
    multipolygon, multiregion = multipolygon_with_multiregion

    result = multiregion_in_multipolygon(multiregion, multipolygon)

    assert all(result is multiregion_in_multipolygon(rotated, multipolygon)
               for rotated in sequence_rotations(multiregion))
