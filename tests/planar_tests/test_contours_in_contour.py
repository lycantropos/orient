from typing import (List,
                    Tuple)

from hypothesis import given

from orient.hints import Contour
from orient.planar import (contour_in_contour,
                           contours_in_contour)
from . import strategies


@given(strategies.contours_with_contours_lists)
def test_basic(contour_with_contours: Tuple[Contour, List[Contour]]) -> None:
    contour, contours = contour_with_contours

    result = contours_in_contour(contours, contour)

    assert isinstance(result, bool)


@given(strategies.contours_with_empty_contours_lists)
def test_base(contour_with_contours: Tuple[Contour, List[Contour]]) -> None:
    contour, contours = contour_with_contours

    assert contours_in_contour(contours, contour)


@given(strategies.contours_with_non_empty_contours_lists)
def test_step(contour_with_contours: Tuple[Contour, List[Contour]]) -> None:
    contour, contours = contour_with_contours
    first_contour, *rest_contours = contours

    result = contours_in_contour(rest_contours, contour)
    next_result = contours_in_contour(contours, contour)

    assert (next_result
            is (result and contour_in_contour(first_contour, contour)))


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
