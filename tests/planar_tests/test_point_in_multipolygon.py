from typing import Tuple

from ground.base import Location
from ground.hints import (Multipolygon,
                          Point)
from hypothesis import given

from orient.planar import (point_in_multipolygon,
                           point_in_polygon)
from tests.utils import (SHAPED_LOCATIONS,
                         equivalence,
                         multipolygon_pop_left,
                         multipolygon_rotations,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_coordinates,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_point_coordinates,
                         to_multipolygon_vertices)
from . import strategies


@given(strategies.multipolygons_with_points)
def test_basic(multipolygon_with_point: Tuple[Multipolygon, Point]) -> None:
    multipolygon, point = multipolygon_with_point

    result = point_in_multipolygon(point, multipolygon)

    assert isinstance(result, Location)
    assert result in SHAPED_LOCATIONS


@given(strategies.multipolygons)
def test_vertices(multipolygon: Multipolygon) -> None:
    assert all(point_in_multipolygon(vertex, multipolygon) is Location.BOUNDARY
               for vertex in to_multipolygon_vertices(multipolygon))


@given(strategies.size_three_or_more_multipolygons_with_points)
def test_step(multipolygon_with_polygon: Tuple[Multipolygon, Point]) -> None:
    multipolygon, point = multipolygon_with_polygon
    first_polygon, rest_multipolygon = multipolygon_pop_left(multipolygon)

    result = point_in_multipolygon(point, rest_multipolygon)
    next_result = point_in_multipolygon(point, multipolygon)

    relation_with_first_polygon = point_in_polygon(point, first_polygon)
    assert equivalence(next_result is Location.EXTERIOR,
                       result is Location.EXTERIOR
                       and relation_with_first_polygon is Location.EXTERIOR)
    assert equivalence(next_result is Location.INTERIOR,
                       result is Location.INTERIOR
                       or relation_with_first_polygon is Location.INTERIOR)
    assert equivalence(next_result is Location.BOUNDARY,
                       result is Location.BOUNDARY
                       or relation_with_first_polygon is Location.BOUNDARY)


@given(strategies.multipolygons_with_points)
def test_reversals(multipolygon_with_point: Tuple[Multipolygon, Point]
                   ) -> None:
    multipolygon, point = multipolygon_with_point

    result = point_in_multipolygon(point, multipolygon)

    assert result is point_in_multipolygon(point,
                                           reverse_multipolygon(multipolygon))
    assert result is point_in_multipolygon(
            point, reverse_multipolygon_borders(multipolygon))
    assert result is point_in_multipolygon(
            point, reverse_multipolygon_holes(multipolygon))
    assert result is point_in_multipolygon(
            point, reverse_multipolygon_holes_contours(multipolygon))
    assert result is point_in_multipolygon(
            reverse_point_coordinates(point),
            reverse_multipolygon_coordinates(multipolygon))


@given(strategies.multipolygons_with_points)
def test_rotations(multipolygon_with_point: Tuple[Multipolygon, Point]
                   ) -> None:
    multipolygon, point = multipolygon_with_point

    result = point_in_multipolygon(point, multipolygon)

    assert all(result is point_in_multipolygon(point, rotated)
               for rotated in multipolygon_rotations(multipolygon))
