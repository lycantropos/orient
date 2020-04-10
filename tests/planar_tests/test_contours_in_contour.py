from typing import (List,
                    Tuple)

from hypothesis import given

from orient.hints import Contour
from orient.planar import (Relation,
                           contour_in_contour,
                           contours_in_contour)
from tests.utils import equivalence
from . import strategies


@given(strategies.contours_with_contours_lists)
def test_basic(contour_with_contours: Tuple[Contour, List[Contour]]) -> None:
    contour, contours = contour_with_contours

    result = contours_in_contour(contours, contour)

    assert isinstance(result, Relation)


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contours_in_contour([contour], contour) is Relation.EQUAL


@given(strategies.contours_with_empty_contours_lists)
def test_base(contour_with_contours: Tuple[Contour, List[Contour]]) -> None:
    contour, contours = contour_with_contours

    assert contours_in_contour(contours, contour) is Relation.DISJOINT


@given(strategies.contours_with_non_empty_contours_lists)
def test_step(contour_with_contours: Tuple[Contour, List[Contour]]) -> None:
    contour, contours = contour_with_contours
    first_contour, *rest_contours = contours

    result = contours_in_contour(rest_contours, contour)
    next_result = contours_in_contour(contours, contour)

    first_contour_relation = contour_in_contour(first_contour, contour)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is first_contour_relation is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.DISJOINT
                       and first_contour_relation is Relation.TOUCH
                       or result is Relation.TOUCH
                       and first_contour_relation in (Relation.DISJOINT,
                                                      Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPOSITE,
                       result is Relation.COMPOSITE
                       or bool(rest_contours)
                       and first_contour_relation is Relation.EQUAL)
    assert equivalence(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or first_contour_relation is Relation.OVERLAP
                       or (bool(rest_contours) and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and first_contour_relation in (Relation.WITHIN,
                                                      Relation.ENCLOSED)
                       or result in (Relation.WITHIN, Relation.ENCLOSED)
                       and first_contour_relation is Relation.DISJOINT)
    assert equivalence(next_result is Relation.COVER,
                       result is Relation.COVER
                       or first_contour_relation is Relation.COVER)
    assert equivalence(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       or first_contour_relation is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.EQUAL,
                       not rest_contours
                       and first_contour_relation is Relation.EQUAL)
    assert equivalence(next_result is Relation.ENCLOSED,
                       result is Relation.ENCLOSED
                       and first_contour_relation in (Relation.ENCLOSED,
                                                      Relation.WITHIN)
                       or (not rest_contours or result is Relation.WITHIN)
                       and first_contour_relation is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       (not rest_contours or result is Relation.WITHIN)
                       and first_contour_relation is Relation.WITHIN)


@given(strategies.contours_with_contours_lists)
def test_reversed(contour_with_contours: Tuple[Contour, List[Contour]]
                  ) -> None:
    contour, contours = contour_with_contours

    result = contours_in_contour(contours, contour)

    assert result is contours_in_contour(contours[::-1], contour)


@given(strategies.contours_with_contours_lists)
def test_reversed_contours(contour_with_contours: Tuple[Contour, List[Contour]]
                           ) -> None:
    contour, contours = contour_with_contours

    result = contours_in_contour(contours, contour)

    assert result is contours_in_contour([contour[::-1]
                                          for contour in contours],
                                         contour)
    assert result is contours_in_contour(contours, contour[::-1])
