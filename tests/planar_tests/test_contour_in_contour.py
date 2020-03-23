from typing import Tuple

from hypothesis import given

from orient.hints import Contour
from orient.planar import (PointLocation,
                           contour_in_contour,
                           point_in_contour)
from tests.utils import (are_contours_similar,
                         implication,
                         to_convex_hull)
from . import strategies


@given(strategies.contours_pairs)
def test_basic(contours_pair: Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    result = contour_in_contour(left_contour, right_contour)

    assert isinstance(result, bool)


@given(strategies.contours)
def test_reflexivity(contour: Contour) -> None:
    assert contour_in_contour(contour, contour)


@given(strategies.contours_pairs)
def test_antisymmetry(contours_pair: Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    assert implication(contour_in_contour(left_contour, right_contour)
                       and contour_in_contour(right_contour, left_contour),
                       are_contours_similar(left_contour, right_contour))


@given(strategies.contours_triplets)
def test_transitivity(contours_triplet: Tuple[Contour, Contour, Contour]
                      ) -> None:
    left_contour, mid_contour, right_contour = contours_triplet

    assert implication(contour_in_contour(left_contour, mid_contour)
                       and contour_in_contour(mid_contour, right_contour),
                       contour_in_contour(left_contour, right_contour))


@given(strategies.contours)
def test_convex_hull(contour: Contour) -> None:
    assert contour_in_contour(contour, to_convex_hull(contour))


@given(strategies.contours_pairs)
def test_vertices(contours_pair: Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    assert implication(contour_in_contour(left_contour, right_contour),
                       all(point_in_contour(vertex, right_contour)
                           is not PointLocation.EXTERNAL
                           for vertex in left_contour))
