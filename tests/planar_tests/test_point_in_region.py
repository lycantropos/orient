from typing import Tuple

from ground.base import Relation
from ground.hints import Point
from hypothesis import given

from orient.hints import Region
from orient.planar import point_in_region
from tests.utils import (PRIMITIVE_COMPOUND_RELATIONS,
                         region_rotations,
                         reverse_contour)
from . import strategies


@given(strategies.contours_with_points)
def test_basic(region_with_point: Tuple[Region, Point]) -> None:
    region, point = region_with_point

    result = point_in_region(point, region)

    assert isinstance(result, Relation)
    assert result in PRIMITIVE_COMPOUND_RELATIONS


@given(strategies.contours)
def test_self(region: Region) -> None:
    assert all(point_in_region(vertex, region) is Relation.COMPONENT
               for vertex in region.vertices)


@given(strategies.contours_with_points)
def test_reversals(region_with_point: Tuple[Region, Point]) -> None:
    region, point = region_with_point

    result = point_in_region(point, region)

    assert result is point_in_region(point, reverse_contour(region))


@given(strategies.contours_with_points)
def test_rotated(region_with_point: Tuple[Region, Point]) -> None:
    region, point = region_with_point

    result = point_in_region(point, region)

    assert all(result is point_in_region(point, rotated)
               for rotated in region_rotations(region))
