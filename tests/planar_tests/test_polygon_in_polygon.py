from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.hints import Polygon
from orient.planar import (PointLocation,
                           point_in_polygon,
                           polygon_in_polygon)
from tests.utils import (are_polygons_similar,
                         implication,
                         to_convex_hull)
from . import strategies


@given(strategies.polygons_pairs)
def test_basic(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left_polygon, right_polygon = polygons_pair

    result = polygon_in_polygon(left_polygon, right_polygon)

    assert isinstance(result, bool)


@given(strategies.polygons)
def test_reflexivity(polygon: Polygon) -> None:
    assert polygon_in_polygon(polygon, polygon)


@given(strategies.polygons_pairs)
def test_antisymmetry(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left_polygon, right_polygon = polygons_pair

    assert implication(polygon_in_polygon(left_polygon, right_polygon)
                       and polygon_in_polygon(right_polygon, left_polygon),
                       are_polygons_similar(left_polygon, right_polygon))


@given(strategies.polygons_triplets)
def test_transitivity(polygons_triplet: Tuple[Polygon, Polygon, Polygon]
                      ) -> None:
    left_polygon, mid_polygon, right_polygon = polygons_triplet

    assert implication(polygon_in_polygon(left_polygon, mid_polygon)
                       and polygon_in_polygon(mid_polygon, right_polygon),
                       polygon_in_polygon(left_polygon, right_polygon))


@given(strategies.polygons)
def test_border_convex_hull(polygon: Polygon) -> None:
    border, holes = polygon
    assert polygon_in_polygon(polygon, (to_convex_hull(border), holes))


@given(strategies.polygons)
def test_without_holes(polygon: Polygon) -> None:
    border, holes = polygon
    polygon_without_holes = (border, [])
    assert polygon_in_polygon(polygon, polygon_without_holes)
    assert (not holes) is polygon_in_polygon(polygon_without_holes, polygon)


@given(strategies.polygons_pairs)
def test_vertices(polygons_pair: Tuple[Polygon, Polygon]) -> None:
    left_polygon, right_polygon = polygons_pair

    left_border, left_holes = left_polygon
    assert implication(polygon_in_polygon(left_polygon, right_polygon),
                       all(point_in_polygon(vertex, right_polygon)
                           is not PointLocation.EXTERNAL
                           for vertex in chain(left_border, *left_holes)))
