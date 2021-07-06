from typing import Tuple

from ground.base import Location
from ground.hints import (Multisegment,
                          Point)
from hypothesis import given

from orient.planar import point_in_multisegment
from tests.utils import (LINEAR_LOCATIONS,
                         multisegment_rotations,
                         reverse_multisegment,
                         reverse_multisegment_coordinates,
                         reverse_point_coordinates)
from . import strategies


@given(strategies.multisegments_with_points)
def test_basic(multisegment_with_point: Tuple[Multisegment, Point]) -> None:
    multisegment, point = multisegment_with_point

    result = point_in_multisegment(point, multisegment)

    assert isinstance(result, Location)
    assert result in LINEAR_LOCATIONS


@given(strategies.multisegments_with_points)
def test_reversals(multisegment_with_point: Tuple[Multisegment, Point]
                   ) -> None:
    multisegment, point = multisegment_with_point

    result = point_in_multisegment(point, multisegment)

    assert result is point_in_multisegment(point,
                                           reverse_multisegment(multisegment))
    assert result is point_in_multisegment(
            reverse_point_coordinates(point),
            reverse_multisegment_coordinates(multisegment))


@given(strategies.multisegments_with_points)
def test_rotations(multisegment_with_point: Tuple[Multisegment, Point]
                   ) -> None:
    multisegment, point = multisegment_with_point

    result = point_in_multisegment(point, multisegment)

    assert all(result is point_in_multisegment(point, rotated)
               for rotated in multisegment_rotations(multisegment))
