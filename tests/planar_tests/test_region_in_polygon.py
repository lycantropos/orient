from typing import Tuple

from ground.base import Relation
from ground.hints import Polygon
from hypothesis import given

from orient.hints import Region
from orient.planar import (contour_in_polygon,
                           region_in_polygon)
from tests.utils import (UNIFORM_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         region_rotations,
                         reverse_contour,
                         reverse_contour_coordinates,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours)
from . import strategies


@given(strategies.polygons_with_contours)
def test_basic(region_with_polygon: Tuple[Polygon, Region]) -> None:
    polygon, region = region_with_polygon

    result = region_in_polygon(region, polygon)

    assert isinstance(result, Relation)
    assert result in UNIFORM_COMPOUND_RELATIONS


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    assert region_in_polygon(polygon.border, polygon) is (Relation.ENCLOSES
                                                          if polygon.holes
                                                          else Relation.EQUAL)
    assert all(region_in_polygon(hole, polygon) is Relation.TOUCH
               for hole in polygon.holes)


@given(strategies.polygons_with_contours)
def test_reversals(polygon_with_region: Tuple[Polygon, Region]) -> None:
    polygon, region = polygon_with_region

    result = region_in_polygon(region, polygon)

    assert result is region_in_polygon(reverse_contour(region), polygon)
    assert result is region_in_polygon(region, reverse_polygon_border(polygon))
    assert result is region_in_polygon(region, reverse_polygon_holes(polygon))
    assert result is region_in_polygon(region,
                                       reverse_polygon_holes_contours(polygon))
    assert result is region_in_polygon(reverse_contour_coordinates(region),
                                       reverse_polygon_coordinates(polygon))


@given(strategies.polygons_with_contours)
def test_rotations(polygon_with_region: Tuple[Polygon, Region]) -> None:
    polygon, region = polygon_with_region

    result = region_in_polygon(region, polygon)

    assert all(result is region_in_polygon(rotated, polygon)
               for rotated in region_rotations(region))


@given(strategies.polygons_with_contours)
def test_connection_with_contour_in_polygon(polygon_with_region
                                            : Tuple[Polygon, Region]) -> None:
    polygon, region = polygon_with_region

    result = region_in_polygon(region, polygon)

    contour_relation = contour_in_polygon(region, polygon)
    assert equivalence(result is Relation.DISJOINT
                       or result is Relation.COVER,
                       contour_relation is Relation.DISJOINT)
    assert implication(result is Relation.TOUCH,
                       contour_relation is Relation.TOUCH)
    assert implication(result is Relation.OVERLAP,
                       contour_relation is Relation.CROSS
                       or contour_relation is Relation.ENCLOSED
                       or contour_relation is Relation.WITHIN)
    assert implication(result is Relation.ENCLOSES,
                       contour_relation is Relation.TOUCH
                       or contour_relation is Relation.COMPONENT)
    assert implication(result is Relation.EQUAL,
                       contour_relation is Relation.COMPONENT)
    assert implication(result is Relation.ENCLOSED,
                       contour_relation is Relation.ENCLOSED)
    assert implication(result is Relation.WITHIN,
                       contour_relation is Relation.WITHIN)
