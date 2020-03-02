from typing import (Iterable,
                    List,
                    Sequence)

from hypothesis.strategies import SearchStrategy

from orient.core.angular import (Orientation,
                                 to_orientation)
from orient.hints import (Contour,
                          Point)

Strategy = SearchStrategy


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def to_counterclockwise_contour(contour: Contour) -> Contour:
    if _to_first_angle_orientation(contour) is not Orientation.CLOCKWISE:
        contour = contour[:1] + contour[1:][::-1]
    return contour


def _to_first_angle_orientation(contour: Contour) -> Orientation:
    return to_orientation(contour[-1], contour[0], contour[1])


def are_contours_similar(left: Contour, right: Contour) -> bool:
    if len(left) != len(right):
        return False
    elif not left:
        return not right
    try:
        right_start = right.index(left[0])
    except ValueError:
        return False
    else:
        right = right[right_start:] + right[:right_start]
        if left[1] == right[-1]:
            right = right[:1] + right[:0:-1]
        return left == right


def to_convex_hull(points: Sequence[Point]) -> Contour:
    points = sorted(points)
    lower = _to_sub_hull(points)
    upper = _to_sub_hull(reversed(points))
    return lower[:-1] + upper[:-1]


def _to_sub_hull(points: Iterable[Point]) -> List[Point]:
    result = []
    for point in points:
        while len(result) >= 2:
            if (to_orientation(result[-1], result[-2], point)
                    is not Orientation.COUNTERCLOCKWISE):
                del result[-1]
            else:
                break
        result.append(point)
    return result
