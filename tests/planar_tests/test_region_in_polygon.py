from typing import Tuple

from hypothesis import given

from orient.hints import (Polygon,
                          Region)
from orient.planar import (Relation,
                           contour_in_polygon,
                           region_in_polygon)
from tests.utils import (COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_contour,
                         reverse_polygon_border,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours, rotations)
from . import strategies


@given(strategies.polygons_with_contours)
def test_basic(region_with_polygon: Tuple[Polygon, Region]) -> None:
    polygon, region = region_with_polygon

    result = region_in_polygon(region, polygon)

    assert isinstance(result, Relation)
    assert result in COMPOUND_RELATIONS


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    border, holes = polygon
    assert region_in_polygon(border, polygon) is (Relation.ENCLOSES
                                                  if holes
                                                  else Relation.EQUAL)
    assert all(region_in_polygon(hole, polygon) is Relation.TOUCH
               for hole in holes)


@given(strategies.polygons_with_contours)
def test_reversed(polygon_with_region: Tuple[Polygon, Region]) -> None:
    polygon, region = polygon_with_region

    result = region_in_polygon(region, polygon)

    assert result is region_in_polygon(reverse_contour(region), polygon)
    assert result is region_in_polygon(region, reverse_polygon_border(polygon))
    assert result is region_in_polygon(region, reverse_polygon_holes(polygon))
    assert result is region_in_polygon(region,
                                       reverse_polygon_holes_contours(polygon))


@given(strategies.polygons_with_contours)
def test_rotations(polygon_with_region: Tuple[Polygon, Region]) -> None:
    polygon, region = polygon_with_region

    result = region_in_polygon(region, polygon)

    assert all(result is region_in_polygon(rotated, polygon)
               for rotated in rotations(region))


@given(strategies.polygons_with_contours)
def test_connection_with_contour_in_polygon(polygon_with_region
                                            : Tuple[Polygon, Region]
                                            ) -> None:
    polygon, region = polygon_with_region

    result = region_in_polygon(region, polygon)

    contour_relation = contour_in_polygon(region, polygon)
    assert equivalence(result is Relation.DISJOINT
                       or result is Relation.COVER,
                       contour_relation is Relation.DISJOINT)
    assert equivalence(result is Relation.TOUCH
                       or result is Relation.ENCLOSES
                       or result is Relation.COMPOSITE,
                       contour_relation is Relation.TOUCH)
    assert implication(result is Relation.OVERLAP,
                       contour_relation is Relation.CROSS
                       or contour_relation is Relation.ENCLOSED
                       or contour_relation is Relation.WITHIN)
    assert equivalence(result is Relation.COMPONENT
                       or result is Relation.EQUAL,
                       contour_relation is Relation.COMPONENT)
    assert implication(result is Relation.ENCLOSED,
                       contour_relation is Relation.ENCLOSED)
    assert implication(result is Relation.WITHIN,
                       contour_relation is Relation.WITHIN)
