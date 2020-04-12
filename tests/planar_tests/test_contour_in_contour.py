from typing import Tuple

from hypothesis import given

from orient.hints import Contour
from orient.planar import (Relation,
                           contour_in_contour,
                           point_in_contour)
from tests.utils import (SAME_LINEAR_RELATIONS,
                         equivalence,
                         implication,
                         to_convex_hull)
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
def test_symmetric_relations(contours_pair: Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    result = contour_in_contour(left_contour, right_contour)

    complement = contour_in_contour(right_contour, left_contour)
    assert equivalence(result is complement,
                       result in (Relation.DISJOINT, Relation.TOUCH,
                                  Relation.OVERLAP, Relation.CROSS,
                                  Relation.EQUAL))


@given(strategies.contours_pairs)
def test_asymmetric_relations(contours_pair: Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    result = contour_in_contour(left_contour, right_contour)

    complement = contour_in_contour(right_contour, left_contour)
    assert equivalence(result is Relation.COMPOSITE,
                       complement is Relation.COMPONENT)


@given(strategies.contours)
def test_convex_hull(contour: Contour) -> None:
    assert (contour_in_contour(contour, to_convex_hull(contour))
            in (Relation.EQUAL, Relation.OVERLAP))


@given(strategies.contours_pairs)
def test_vertices(contours_pair: Tuple[Contour, Contour]) -> None:
    left_contour, right_contour = contours_pair

    assert implication(contour_in_contour(left_contour, right_contour)
                       in (Relation.EQUAL, Relation.COMPONENT),
                       all(point_in_contour(vertex, right_contour)
                           is Relation.COMPONENT
                           for vertex in left_contour))
