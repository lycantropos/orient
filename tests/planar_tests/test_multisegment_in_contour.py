from typing import Tuple

from hypothesis import given

from orient.core.contour import to_segments
from orient.hints import (Contour,
                          Multisegment)
from orient.planar import (Relation,
                           multisegment_in_contour)
from tests.utils import (SAME_LINEAR_RELATIONS,
                         reverse_contour,
                         reverse_multisegment,
                         rotations)
from . import strategies


@given(strategies.contours_with_multisegments)
def test_basic(contour_with_multisegment: Tuple[Contour, Multisegment]
               ) -> None:
    contour, multisegment = contour_with_multisegment

    result = multisegment_in_contour(multisegment, contour)

    assert isinstance(result, Relation)
    assert result in SAME_LINEAR_RELATIONS


@given(strategies.contours)
def test_edges(contour: Contour) -> None:
    assert multisegment_in_contour(list(to_segments(contour)),
                                   contour) is Relation.EQUAL


@given(strategies.contours_with_multisegments)
def test_reversed_multisegment(
        contour_with_multisegment: Tuple[Contour, Multisegment]
) -> None:
    contour, multisegment = contour_with_multisegment

    result = multisegment_in_contour(multisegment, contour)

    assert result is multisegment_in_contour(
            reverse_multisegment(multisegment), contour)


@given(strategies.contours_with_multisegments)
def test_reversed_contour(contour_with_multisegment: Tuple[Contour,
                                                           Multisegment]
                          ) -> None:
    contour, multisegment = contour_with_multisegment

    result = multisegment_in_contour(multisegment, contour)

    assert result is multisegment_in_contour(multisegment,
                                             reverse_contour(contour))


@given(strategies.contours_with_multisegments)
def test_rotations(contour_with_multisegment: Tuple[Contour, Multisegment]
                   ) -> None:
    contour, multisegment = contour_with_multisegment

    result = multisegment_in_contour(multisegment, contour)

    assert all(result is multisegment_in_contour(multisegment, rotated)
               for rotated in rotations(contour))
    assert all(result is multisegment_in_contour(rotated, contour)
               for rotated in rotations(multisegment))
