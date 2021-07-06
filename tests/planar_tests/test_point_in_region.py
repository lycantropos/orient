from typing import Tuple

from ground.base import Location
from ground.hints import Point
from hypothesis import given

from orient.hints import Region
from orient.planar import point_in_region
from tests.utils import (SHAPED_LOCATIONS,
                         region_rotations,
                         reverse_contour,
                         reverse_contour_coordinates,
                         reverse_point_coordinates)
from . import strategies


@given(strategies.contours_with_points)
def test_basic(region_with_point: Tuple[Region, Point]) -> None:
    region, point = region_with_point

    result = point_in_region(point, region)

    assert isinstance(result, Location)
    assert result in SHAPED_LOCATIONS


@given(strategies.contours)
def test_self(region: Region) -> None:
    assert all(point_in_region(vertex, region) is Location.BOUNDARY
               for vertex in region.vertices)


@given(strategies.contours_with_points)
def test_reversals(region_with_point: Tuple[Region, Point]) -> None:
    region, point = region_with_point

    result = point_in_region(point, region)

    assert result is point_in_region(point, reverse_contour(region))
    assert result is point_in_region(reverse_point_coordinates(point),
                                     reverse_contour_coordinates(region))


@given(strategies.contours_with_points)
def test_rotated(region_with_point: Tuple[Region, Point]) -> None:
    region, point = region_with_point

    result = point_in_region(point, region)

    assert all(result is point_in_region(point, rotated)
               for rotated in region_rotations(region))
