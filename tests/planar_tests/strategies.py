from functools import partial
from itertools import (chain,
                       repeat)
from typing import (List,
                    Tuple)

from bentley_ottmann.planar import segments_overlap
from hypothesis import strategies
from hypothesis_geometry import planar

from orient.core.contour import to_segments
from orient.hints import (Contour,
                          Coordinate,
                          Point,
                          Segment)
from tests.strategies import coordinates_strategies
from tests.utils import (Strategy,
                         to_counterclockwise_contour)

MAX_CONTOURS_SIZE = 10

segments = coordinates_strategies.flatmap(planar.segments)


def to_segments_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Segment, Point]]:
    return strategies.tuples(planar.segments(coordinates),
                             planar.points(coordinates))


segments_with_points = coordinates_strategies.flatmap(to_segments_with_points)


def to_counterclockwise_contours(coordinates: Strategy[Coordinate]
                                 ) -> Strategy[Contour]:
    return planar.contours(coordinates).map(to_counterclockwise_contour)


contours = coordinates_strategies.flatmap(to_counterclockwise_contours)


def to_non_overlapping_contours_lists(coordinates: Strategy[Coordinate],
                                      *,
                                      min_size: int = 0,
                                      max_size: int = MAX_CONTOURS_SIZE
                                      ) -> Strategy[List[Contour]]:
    return (strategies.lists(to_counterclockwise_contours(coordinates),
                             min_size=min_size,
                             max_size=max_size)
            .map(to_non_overlapping_contours))


def to_non_overlapping_contours(contours: List[Contour]) -> List[Contour]:
    return [contour for index, contour in enumerate(contours)
            if not any(segments_overlap(list(to_segments(contour))
                                        + list(to_segments(other_contour)))
                       for other_contour in chain(contours[:index],
                                                  contours[index + 1:]))]


def to_contours_with_non_overlapping_contours_lists(
        coordinates: Strategy[Coordinate],
        *,
        min_size: int = 0,
        max_size: int = MAX_CONTOURS_SIZE
) -> Strategy[Tuple[Contour, List[Contour]]]:
    return strategies.tuples(
            to_counterclockwise_contours(coordinates),
            to_non_overlapping_contours_lists(coordinates,
                                              min_size=min_size,
                                              max_size=max_size))


contours_with_contours_lists = coordinates_strategies.flatmap(
        to_contours_with_non_overlapping_contours_lists)
contours_with_empty_contours_lists = strategies.tuples(contours,
                                                       strategies.builds(list))
contours_with_non_empty_contours_lists = coordinates_strategies.flatmap(
        partial(to_contours_with_non_overlapping_contours_lists,
                min_size=1))


def to_contours_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Contour, Point]]:
    return strategies.tuples(to_counterclockwise_contours(coordinates),
                             planar.points(coordinates))


contours_with_points = coordinates_strategies.flatmap(to_contours_with_points)


def to_contours_tuples(coordinates: Strategy[Coordinate],
                       *,
                       size: int) -> Strategy[Tuple[Contour, Contour]]:
    return strategies.tuples(*repeat(to_counterclockwise_contours(coordinates),
                                     size))


contours_pairs = coordinates_strategies.flatmap(partial(to_contours_tuples,
                                                        size=2))
contours_triplets = coordinates_strategies.flatmap(partial(to_contours_tuples,
                                                           size=3))
