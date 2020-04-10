from itertools import chain
from operator import itemgetter
from typing import (Any,
                    Callable,
                    Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple,
                    TypeVar)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy
from robust.angular import (Orientation,
                            orientation)

from orient.hints import (Contour,
                          Point,
                          Polygon,
                          Segment)

Domain = TypeVar('Domain')
Key = Callable[[Domain], Any]
Strategy = SearchStrategy


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def equivalence(left: bool, right: bool) -> bool:
    return left is right


_sentinel = object()


def to_index_min(values: Iterable[Domain],
                 *,
                 key: Optional[Key] = None,
                 default: Any = _sentinel) -> int:
    kwargs = {}
    if key is not None:
        kwargs['key'] = lambda value_with_index: key(value_with_index[0])
    if default is not _sentinel:
        kwargs['default'] = default
    return min(((value, index)
                for index, value in enumerate(values)),
               **kwargs)[1]


def are_polygons_similar(left: Polygon, right: Polygon) -> bool:
    return normalize_polygon(left) == normalize_polygon(right)


def normalize_polygon(polygon: Polygon) -> Polygon:
    boundary, holes = polygon
    return normalize_contour(boundary), sorted([normalize_contour(hole)
                                                for hole in holes],
                                               key=itemgetter(0))


def normalize_contour(contour: Contour) -> Contour:
    return to_counterclockwise_contour(rotate_sequence(contour,
                                                       to_index_min(contour)))


def rotate_sequence(sequence: Domain, index: int) -> Domain:
    return sequence[index:] + sequence[:index]


def to_counterclockwise_contour(contour: Contour) -> Contour:
    if _to_first_angle_orientation(contour) is not Orientation.CLOCKWISE:
        contour = contour[:1] + contour[1:][::-1]
    return contour


def _to_first_angle_orientation(contour: Contour) -> Orientation:
    return orientation(contour[-1], contour[0], contour[1])


def to_pairs(strategy: Strategy[Domain]) -> Strategy[Tuple[Domain, Domain]]:
    return strategies.tuples(strategy, strategy)


def to_triplets(strategy: Strategy[Domain]
                ) -> Strategy[Tuple[Domain, Domain, Domain]]:
    return strategies.tuples(strategy, strategy, strategy)


def to_convex_hull(points: Sequence[Point]) -> Contour:
    points = sorted(points)
    lower = _to_sub_hull(points)
    upper = _to_sub_hull(reversed(points))
    return lower[:-1] + upper[:-1]


def _to_sub_hull(points: Iterable[Point]) -> List[Point]:
    result = []
    for point in points:
        while len(result) >= 2:
            if (orientation(result[-1], result[-2], point)
                    is not Orientation.COUNTERCLOCKWISE):
                del result[-1]
            else:
                break
        result.append(point)
    return result


def to_contour_separators(contour: Contour) -> Iterable[Segment]:
    return ((contour[index], contour[next_index])
            for index in range(len(contour))
            for next_index in chain(range(int(index == len(contour) - 1),
                                          index - 1),
                                    range(index + 2,
                                          min(len(contour) + index - 1,
                                              len(contour)))))


def reverse_segment(segment: Segment) -> Segment:
    return segment[::-1]


def reverse_segment_coordinates(segment: Segment) -> Segment:
    start, end = segment
    return reverse_point_coordinates(start), reverse_point_coordinates(end)


def reverse_point_coordinates(point: Point) -> Point:
    return point[::-1]
