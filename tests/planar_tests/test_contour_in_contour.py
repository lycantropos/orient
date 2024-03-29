from typing import Tuple

from ground.base import (Location,
                         Relation)
from ground.hints import Contour
from hypothesis import given

from orient.planar import (contour_in_contour,
                           point_in_contour)
from tests.utils import (ASYMMETRIC_LINEAR_RELATIONS,
                         SAME_LINEAR_RELATIONS,
                         SYMMETRIC_SAME_LINEAR_RELATIONS,
                         contour_rotations,
                         equivalence,
                         implication,
                         reverse_contour,
                         reverse_contour_coordinates,
                         to_contour_convex_hull)
from . import strategies


@given(strategies.contours_pairs)
def test_basic(contours_pair: Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    result = contour_in_contour(left_contour, right_contour)

    assert isinstance(result, Relation)
    assert result in SAME_LINEAR_RELATIONS


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contour_in_contour(contour, contour) is Relation.EQUAL


@given(strategies.contours_pairs)
def test_relations(contours_pair: Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    result = contour_in_contour(left_contour, right_contour)

    complement = contour_in_contour(right_contour, left_contour)
    assert equivalence(result is complement,
                       result in SYMMETRIC_SAME_LINEAR_RELATIONS)
    assert equivalence(result is not complement,
                       result.complement is complement
                       and result in ASYMMETRIC_LINEAR_RELATIONS
                       and complement in ASYMMETRIC_LINEAR_RELATIONS)


@given(strategies.contours)
def test_convex_hull(contour: Contour) -> None:
    assert (contour_in_contour(contour, to_contour_convex_hull(contour))
            in (Relation.TOUCH, Relation.OVERLAP, Relation.EQUAL))


@given(strategies.contours_pairs)
def test_reversals(contours_pair: Tuple[Contour, Contour]) -> None:
    left, right = contours_pair

    result = contour_in_contour(left, right)

    assert result is contour_in_contour(reverse_contour(left), right)
    assert result is contour_in_contour(left, reverse_contour(right))
    assert result is contour_in_contour(reverse_contour_coordinates(left),
                                        reverse_contour_coordinates(right))


@given(strategies.contours_pairs)
def test_rotations(contours_pair: Tuple[Contour, Contour]) -> None:
    left, right = contours_pair

    result = contour_in_contour(left, right)

    assert all(result is contour_in_contour(rotated, right)
               for rotated in contour_rotations(left))
    assert all(result is contour_in_contour(left, rotated)
               for rotated in contour_rotations(right))


@given(strategies.contours_pairs)
def test_connection_with_point_in_contour(contours_pair
                                          : Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    assert implication(contour_in_contour(left_contour, right_contour)
                       in (Relation.EQUAL, Relation.COMPONENT),
                       all(point_in_contour(vertex, right_contour)
                           is Location.BOUNDARY
                           for vertex in left_contour.vertices))
