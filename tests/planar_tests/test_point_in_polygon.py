from typing import Tuple

from ground.base import Location
from ground.hints import (Point,
                          Polygon)
from hypothesis import given

from orient.planar import point_in_polygon
from tests.utils import (SHAPED_LOCATIONS,
                         implication,
                         reverse_point_coordinates,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         to_polygon_vertices,
                         to_solid_polygon)
from . import strategies


@given(strategies.polygons_with_points)
def test_basic(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    assert isinstance(result, Location)
    assert result in SHAPED_LOCATIONS


@given(strategies.polygons)
def test_self(polygon: Polygon) -> None:
    assert all(point_in_polygon(vertex, polygon) is Location.BOUNDARY
               for vertex in to_polygon_vertices(polygon))


@given(strategies.polygons_with_points)
def test_without_holes(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    polygon_without_holes = to_solid_polygon(polygon)
    assert implication(result is Location.INTERIOR,
                       point_in_polygon(point, polygon_without_holes)
                       is Location.INTERIOR)
    assert implication(point_in_polygon(point, polygon_without_holes)
                       is Location.EXTERIOR,
                       result is Location.EXTERIOR)
    assert implication(point_in_polygon(point, polygon_without_holes)
                       is Location.BOUNDARY,
                       result is Location.BOUNDARY)


@given(strategies.polygons_with_points)
def test_reversals(polygon_with_point: Tuple[Polygon, Point]) -> None:
    polygon, point = polygon_with_point

    result = point_in_polygon(point, polygon)

    assert result is point_in_polygon(point, reverse_polygon_border(polygon))
    assert result is point_in_polygon(point, reverse_polygon_holes(polygon))
    assert result is point_in_polygon(point,
                                      reverse_polygon_holes_contours(polygon))
    assert result is point_in_polygon(reverse_point_coordinates(point),
                                      reverse_polygon_coordinates(polygon))
