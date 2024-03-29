from typing import Tuple

from ground.base import Relation
from ground.hints import Polygon
from hypothesis import given

from orient.hints import Multiregion
from orient.planar import (multiregion_in_polygon,
                           region_in_polygon)
from tests.utils import (MULTIPART_COMPOUND_RELATIONS,
                         equivalence,
                         reverse_multiregion,
                         reverse_multiregion_coordinates,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         sequence_rotations)
from . import strategies


@given(strategies.polygons_with_multiregions)
def test_basic(multiregion_with_polygon: Tuple[Polygon, Multiregion]) -> None:
    polygon, multiregion = multiregion_with_polygon

    result = multiregion_in_polygon(multiregion, polygon)

    assert isinstance(result, Relation)
    assert result in MULTIPART_COMPOUND_RELATIONS


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    assert (multiregion_in_polygon([polygon.border], polygon)
            is (Relation.ENCLOSES if polygon.holes else Relation.EQUAL))
    assert (multiregion_in_polygon(polygon.holes, polygon)
            is (Relation.TOUCH if polygon.holes else Relation.DISJOINT))


@given(strategies.polygons_with_size_three_or_more_multiregions)
def test_step(multiregion_with_polygon: Tuple[Polygon, Multiregion]) -> None:
    polygon, multiregion = multiregion_with_polygon
    first_region, *rest_multiregion = multiregion

    result = multiregion_in_polygon(rest_multiregion, polygon)
    next_result = multiregion_in_polygon(multiregion, polygon)

    relation_with_first_region = region_in_polygon(first_region, polygon)
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


@given(strategies.polygons_with_multiregions)
def test_reversals(polygon_with_multiregion: Tuple[Polygon, Multiregion]
                   ) -> None:
    polygon, multiregion = polygon_with_multiregion

    result = multiregion_in_polygon(multiregion, polygon)

    assert result is multiregion_in_polygon(reverse_multiregion(multiregion),
                                            polygon)
    assert result is multiregion_in_polygon(multiregion,
                                            reverse_polygon_border(polygon))
    assert result is multiregion_in_polygon(multiregion,
                                            reverse_polygon_holes(polygon))
    assert result is multiregion_in_polygon(
            multiregion, reverse_polygon_holes_contours(polygon))
    assert result is multiregion_in_polygon(
            reverse_multiregion_coordinates(multiregion),
            reverse_polygon_coordinates(polygon))


@given(strategies.polygons_with_multiregions)
def test_rotations(polygon_with_multiregion: Tuple[Polygon, Multiregion]
                   ) -> None:
    polygon, multiregion = polygon_with_multiregion

    result = multiregion_in_polygon(multiregion, polygon)

    assert all(result is multiregion_in_polygon(rotated, polygon)
               for rotated in sequence_rotations(multiregion))
