from typing import Tuple

from ground.base import Relation
from ground.hints import (Multipolygon,
                          Polygon)
from hypothesis import given

from orient.planar import (polygon_in_multipolygon,
                           polygon_in_polygon)
from tests.utils import (MULTIPART_COMPOUND_RELATIONS,
                         equivalence,
                         multipolygon_pop_left,
                         multipolygon_rotations,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_polygon_border,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         to_solid_polygon)
from . import strategies


@given(strategies.multipolygons_with_polygons)
def test_basic(multipolygon_with_polygon: Tuple[Multipolygon, Polygon]
               ) -> None:
    multipolygon, polygon = multipolygon_with_polygon

    result = polygon_in_multipolygon(polygon, multipolygon)

    assert isinstance(result, Relation)
    assert result in MULTIPART_COMPOUND_RELATIONS


@given(strategies.non_empty_multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    has_holes = any(polygon.holes for polygon in multipolygon.polygons)
    assert equivalence(any(polygon_in_multipolygon(polygon, multipolygon)
                           is Relation.EQUAL
                           for polygon in multipolygon.polygons),
                       len(multipolygon.polygons) == 1)
    assert equivalence(all(polygon_in_multipolygon(polygon, multipolygon)
                           is Relation.COMPONENT
                           for polygon in multipolygon.polygons),
                       len(multipolygon.polygons) > 1)
    assert equivalence(any(polygon_in_multipolygon(to_solid_polygon(polygon),
                                                   multipolygon)
                           is Relation.EQUAL
                           for polygon in multipolygon.polygons),
                       not has_holes and len(multipolygon.polygons) == 1)
    assert equivalence(all(polygon_in_multipolygon(to_solid_polygon(polygon),
                                                   multipolygon)
                           is Relation.COMPONENT
                           for polygon in multipolygon.polygons),
                       not has_holes and len(multipolygon.polygons) > 1)
    assert equivalence(any(polygon_in_multipolygon(to_solid_polygon(polygon),
                                                   multipolygon)
                           is Relation.ENCLOSES
                           for polygon in multipolygon.polygons),
                       has_holes and len(multipolygon.polygons) == 1)
    assert equivalence(any(polygon_in_multipolygon(to_solid_polygon(polygon),
                                                   multipolygon)
                           is Relation.OVERLAP
                           for polygon in multipolygon.polygons),
                       has_holes and len(multipolygon.polygons) > 1)


@given(strategies.empty_multipolygons_with_polygons)
def test_base(multipolygon_with_polygon: Tuple[Multipolygon, Polygon]) -> None:
    multipolygon, polygon = multipolygon_with_polygon

    assert polygon_in_multipolygon(polygon, multipolygon) is Relation.DISJOINT


@given(strategies.non_empty_multipolygons_with_polygons)
def test_step(multipolygon_with_polygon: Tuple[Multipolygon, Polygon]) -> None:
    multipolygon, polygon = multipolygon_with_polygon
    first_polygon, rest_multipolygon = multipolygon_pop_left(multipolygon)

    result = polygon_in_multipolygon(polygon, rest_multipolygon)
    next_result = polygon_in_multipolygon(polygon, multipolygon)

    relation_with_first_polygon = polygon_in_polygon(polygon, first_polygon)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_polygon
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.DISJOINT
                       and relation_with_first_polygon is Relation.TOUCH
                       or result is Relation.TOUCH
                       and relation_with_first_polygon in (Relation.DISJOINT,
                                                           Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or bool(rest_multipolygon.polygons)
                       and relation_with_first_polygon is Relation.EQUAL)
    assert equivalence(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_polygon is Relation.OVERLAP
                       or (bool(rest_multipolygon.polygons)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_polygon in (Relation.COVER,
                                                           Relation.ENCLOSES)
                       or result in (Relation.COVER, Relation.ENCLOSES)
                       and relation_with_first_polygon is Relation.DISJOINT)
    assert equivalence(next_result is Relation.COVER,
                       (not rest_multipolygon.polygons
                        or result is Relation.COVER)
                       and relation_with_first_polygon is Relation.COVER)
    assert equivalence(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       and relation_with_first_polygon in (Relation.ENCLOSES,
                                                           Relation.COVER)
                       or (not rest_multipolygon.polygons
                           or result is Relation.COVER)
                       and relation_with_first_polygon is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.EQUAL,
                       not rest_multipolygon.polygons
                       and relation_with_first_polygon is Relation.EQUAL)
    assert equivalence(next_result is Relation.ENCLOSED,
                       result is Relation.ENCLOSED
                       or relation_with_first_polygon is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_polygon is Relation.WITHIN)


@given(strategies.multipolygons_with_polygons)
def test_reversals(multipolygon_with_polygon: Tuple[Multipolygon, Polygon]
                   ) -> None:
    multipolygon, polygon = multipolygon_with_polygon

    result = polygon_in_multipolygon(polygon, multipolygon)

    assert result is polygon_in_multipolygon(
            reverse_polygon_border(polygon), multipolygon)
    assert result is polygon_in_multipolygon(
            reverse_polygon_holes(polygon), multipolygon)
    assert result is polygon_in_multipolygon(
            reverse_polygon_holes_contours(polygon), multipolygon)
    assert result is polygon_in_multipolygon(
            polygon, reverse_multipolygon(multipolygon))
    assert result is polygon_in_multipolygon(
            polygon, reverse_multipolygon_borders(multipolygon))
    assert result is polygon_in_multipolygon(
            polygon, reverse_multipolygon_holes(multipolygon))
    assert result is polygon_in_multipolygon(
            polygon, reverse_multipolygon_holes_contours(multipolygon))


@given(strategies.multipolygons_with_polygons)
def test_rotations(multipolygon_with_polygon: Tuple[Multipolygon, Polygon]
                   ) -> None:
    multipolygon, polygon = multipolygon_with_polygon

    result = polygon_in_multipolygon(polygon, multipolygon)

    assert all(result is polygon_in_multipolygon(polygon, rotated)
               for rotated in multipolygon_rotations(multipolygon))
