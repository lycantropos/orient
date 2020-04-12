from typing import Tuple

from hypothesis import given

from orient.hints import (Contour,
                          Multiregion)
from orient.planar import (Relation,
                           contour_in_multiregion,
                           contour_in_region)
from tests.utils import (LINEAR_RELATIONS,
                         equivalence,
                         reverse_contour,
                         reverse_multicontour,
                         reverse_multicontour_contours,
                         rotations)
from . import strategies


@given(strategies.multicontours_with_contours)
def test_basic(multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert isinstance(result, Relation)
    assert result in LINEAR_RELATIONS


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contour_in_multiregion(contour, [contour]) is Relation.COMPONENT


@given(strategies.empty_multicontours_with_contours)
def test_base(multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    assert contour_in_multiregion(contour, multiregion) is Relation.DISJOINT


@given(strategies.non_empty_multicontours_with_contours)
def test_step(multiregion_with_contour: Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour
    first_contour, *rest_multiregion = multiregion

    result = contour_in_multiregion(contour, rest_multiregion)
    next_result = contour_in_multiregion(contour, multiregion)

    relation_with_first_contour = contour_in_region(contour, first_contour)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_contour
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.DISJOINT
                       and relation_with_first_contour is Relation.TOUCH
                       or result is Relation.TOUCH
                       and (relation_with_first_contour is Relation.DISJOINT
                            or relation_with_first_contour is Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or relation_with_first_contour is Relation.COMPONENT)
    assert equivalence(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       or relation_with_first_contour is Relation.CROSS)
    assert equivalence(next_result is Relation.ENCLOSED,
                       result is Relation.ENCLOSED
                       or relation_with_first_contour is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_contour is Relation.WITHIN)


@given(strategies.multicontours_with_contours)
def test_reversed(multiregion_with_contour: Tuple[Multiregion, Contour]
                  ) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert result is contour_in_multiregion(contour,
                                            reverse_multicontour(multiregion))


@given(strategies.multicontours_with_contours)
def test_reversed_contours(multiregion_with_contour
                           : Tuple[Multiregion, Contour]) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert result is contour_in_multiregion(
            contour, reverse_multicontour_contours(multiregion))
    assert result is contour_in_multiregion(reverse_contour(contour),
                                            multiregion)


@given(strategies.multicontours_with_contours)
def test_rotations(multiregion_with_contour: Tuple[Multiregion, Contour]
                   ) -> None:
    multiregion, contour = multiregion_with_contour

    result = contour_in_multiregion(contour, multiregion)

    assert all(result is contour_in_multiregion(contour, rotated)
               for rotated in rotations(multiregion))
