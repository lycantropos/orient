from typing import (List,
                    Tuple)

from hypothesis import given

from orient.hints import Contour
from orient.planar import (Relation,
                           contour_in_contour,
                           contour_in_multicontour)
from tests.utils import equivalence
from . import strategies


@given(strategies.contours_with_contours_lists)
def test_basic(contour_with_contours: Tuple[Contour, List[Contour]]) -> None:
    contour, contours = contour_with_contours

    result = contour_in_multicontour(contour, contours)

    assert isinstance(result, Relation)


@given(strategies.contours)
def test_self(contour: Contour) -> None:
    assert contour_in_multicontour(contour, [contour]) is Relation.EQUAL


@given(strategies.contours_with_empty_contours_lists)
def test_base(contour_with_contours: Tuple[Contour, List[Contour]]) -> None:
    contour, contours = contour_with_contours

    assert contour_in_multicontour(contour, contours) is Relation.DISJOINT


@given(strategies.contours_with_non_empty_contours_lists)
def test_step(contour_with_contours: Tuple[Contour, List[Contour]]) -> None:
    contour, contours = contour_with_contours
    first_contour, *rest_contours = contours

    result = contour_in_multicontour(contour, rest_contours)
    next_result = contour_in_multicontour(contour, contours)

    relation_with_first_contour = contour_in_contour(contour, first_contour)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_contour
                       is Relation.DISJOINT)
    assert equivalence(next_result is Relation.TOUCH,
                       result is Relation.DISJOINT
                       and relation_with_first_contour is Relation.TOUCH
                       or result is Relation.TOUCH
                       and relation_with_first_contour in (Relation.DISJOINT,
                                                           Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or bool(rest_contours)
                       and relation_with_first_contour is Relation.EQUAL)
    assert equivalence(next_result is Relation.OVERLAP,
                       result is Relation.OVERLAP
                       or relation_with_first_contour is Relation.OVERLAP
                       or (bool(rest_contours) and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and relation_with_first_contour in (Relation.COVER,
                                                           Relation.ENCLOSES)
                       or result in (Relation.COVER, Relation.ENCLOSES)
                       and relation_with_first_contour is Relation.DISJOINT)
    assert equivalence(next_result is Relation.COVER,
                       (not rest_contours or result is Relation.COVER)
                       and relation_with_first_contour is Relation.COVER)
    assert equivalence(next_result is Relation.ENCLOSES,
                       result is Relation.ENCLOSES
                       and relation_with_first_contour in (Relation.ENCLOSES,
                                                           Relation.COVER)
                       or (not rest_contours or result is Relation.COVER)
                       and relation_with_first_contour is Relation.ENCLOSES)
    assert equivalence(next_result is Relation.EQUAL,
                       not rest_contours
                       and relation_with_first_contour is Relation.EQUAL)
    assert equivalence(next_result is Relation.ENCLOSED,
                       result is Relation.ENCLOSED
                       or relation_with_first_contour is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       result is Relation.WITHIN
                       or relation_with_first_contour is Relation.WITHIN)


@given(strategies.contours_with_contours_lists)
def test_reversed(contour_with_contours: Tuple[Contour, List[Contour]]
                  ) -> None:
    contour, contours = contour_with_contours

    result = contour_in_multicontour(contour, contours)

    assert result is contour_in_multicontour(contour, contours[::-1])


@given(strategies.contours_with_contours_lists)
def test_reversed_contours(contour_with_contours: Tuple[Contour, List[Contour]]
                           ) -> None:
    contour, contours = contour_with_contours

    result = contour_in_multicontour(contour, contours)

    assert result is contour_in_multicontour(contour, [contour[::-1]
                                                       for contour in
                                                       contours])
    assert result is contour_in_multicontour(contour[::-1], contours)
