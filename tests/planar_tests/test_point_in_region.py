from typing import Tuple

from hypothesis import given

from orient.hints import (Point,
                          Region)
from orient.planar import (Relation,
                           point_in_region)
from tests.utils import (reverse_contour,
                         rotations)
from . import strategies


@given(strategies.contours_with_points)
def test_basic(region_with_point: Tuple[Region, Point]) -> None:
    region, point = region_with_point

    result = point_in_region(point, region)

    assert isinstance(result, Relation)


@given(strategies.contours)
def test_vertices(region: Region) -> None:
    assert all(point_in_region(vertex, region) is Relation.COMPONENT
               for vertex in region)


@given(strategies.contours_with_points)
def test_reversed(region_with_point: Tuple[Region, Point]) -> None:
    region, point = region_with_point

    result = point_in_region(point, region)

    assert result is point_in_region(point, reverse_contour(region))


@given(strategies.contours_with_points)
def test_rotated(region_with_point: Tuple[Region, Point]) -> None:
    region, point = region_with_point

    result = point_in_region(point, region)

    assert all(result is point_in_region(point, rotated)
               for rotated in rotations(region))
