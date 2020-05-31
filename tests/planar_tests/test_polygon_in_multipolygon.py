from typing import Tuple

from hypothesis import given

from orient.hints import (Multipolygon,
                          Polygon)
from orient.planar import (Relation,
                           polygon_in_multipolygon,
                           polygon_in_polygon)
from tests.utils import (COMPOUND_RELATIONS,
                         equivalence,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_polygon_border,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         rotations)
from . import strategies


@given(strategies.multipolygons_with_polygons)
def test_basic(
        multipolygon_with_polygon: Tuple[Multipolygon, Polygon]) -> None:
    multipolygon, polygon = multipolygon_with_polygon

    result = polygon_in_multipolygon(polygon, multipolygon)

    assert isinstance(result, Relation)
    assert result in COMPOUND_RELATIONS


@given(strategies.non_empty_multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    has_holes = any(holes for _, holes in multipolygon)
    assert equivalence(any(polygon_in_multipolygon(polygon, multipolygon)
                           is Relation.EQUAL
                           for polygon in multipolygon),
                       len(multipolygon) == 1)
    assert equivalence(all(polygon_in_multipolygon(polygon, multipolygon)
                           is Relation.COMPONENT
                           for polygon in multipolygon),
                       len(multipolygon) > 1)
    assert equivalence(any(polygon_in_multipolygon((border, []), multipolygon)
                           is Relation.EQUAL
                           for border, _ in multipolygon),
                       not has_holes and len(multipolygon) == 1)
    assert equivalence(all(polygon_in_multipolygon((border, []), multipolygon)
                           is Relation.COMPONENT
                           for border, _ in multipolygon),
                       not has_holes and len(multipolygon) > 1)
    assert equivalence(any(polygon_in_multipolygon((border, []), multipolygon)
                           is Relation.ENCLOSES
                           for border, _ in multipolygon),
                       has_holes and len(multipolygon) == 1)
    assert equivalence(any(polygon_in_multipolygon((border, []), multipolygon)
                           is Relation.OVERLAP
                           for border, _ in multipolygon),
                       has_holes and len(multipolygon) > 1)


@given(strategies.empty_multipolygons_with_polygons)
def test_base(multipolygon_with_polygon: Tuple[Multipolygon, Polygon]) -> None:
    multipolygon, polygon = multipolygon_with_polygon

    assert polygon_in_multipolygon(polygon, multipolygon) is Relation.DISJOINT


@given(strategies.non_empty_multipolygons_with_polygons)
def test_step(multipolygon_with_polygon: Tuple[Multipolygon, Polygon]) -> None:
    multipolygon, polygon = multipolygon_with_polygon
    first_polygon, *rest_multipolygon = multipolygon

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
                       or bool(rest_multipolygon)
                       and relation_with_first_polygon is Relation.EQUAL)
    assert equivalence(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_polygon is Relation.OVERLAP
                       or (bool(rest_multipolygon)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_polygon in (Relation.COVER,
                                                           Relation.ENCLOSES)
                       or result in (Relation.COVER, Relation.ENCLOSES)
                       and relation_with_first_polygon is Relation.DISJOINT)
    assert equivalence(next_result is Relation.COVER,
                       (not rest_multipolygon or result is Relation.COVER)
                       and relation_with_first_polygon is Relation.COVER)
    assert equivalence(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       and relation_with_first_polygon in (Relation.ENCLOSES,
                                                           Relation.COVER)
                       or (not rest_multipolygon or result is Relation.COVER)
                       and relation_with_first_polygon is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.EQUAL,
                       not rest_multipolygon
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
               for rotated in rotations(multipolygon))
