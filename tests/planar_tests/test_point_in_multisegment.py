from typing import Tuple

from hypothesis import given

from orient.hints import (Multisegment,
                          Point)
from orient.planar import (Relation,
                           point_in_multisegment)
from tests.utils import (PRIMITIVE_LINEAR_RELATIONS,
                         reverse_multisegment,
                         rotations)
from . import strategies


@given(strategies.multisegments_with_points)
def test_basic(multisegment_with_point: Tuple[Multisegment, Point]) -> None:
    multisegment, point = multisegment_with_point

    result = point_in_multisegment(point, multisegment)

    assert isinstance(result, Relation)
    assert result in PRIMITIVE_LINEAR_RELATIONS


@given(strategies.multisegments_with_points)
def test_reversed(multisegment_with_point: Tuple[Multisegment, Point]) -> None:
    multisegment, point = multisegment_with_point

    result = point_in_multisegment(point, multisegment)

    assert result is point_in_multisegment(point,
                                           reverse_multisegment(multisegment))


@given(strategies.multisegments_with_points)
def test_rotations(multisegment_with_point: Tuple[Multisegment, Point]
                   ) -> None:
    multisegment, point = multisegment_with_point

    result = point_in_multisegment(point, multisegment)

    assert all(result is point_in_multisegment(point, rotated)
               for rotated in rotations(multisegment))
