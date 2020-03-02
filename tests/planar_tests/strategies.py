from functools import partial
from itertools import repeat
from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar

from orient.hints import (Contour,
                          Coordinate,
                          Point,
                          Segment)
from tests.strategies import coordinates_strategies
from tests.utils import (Strategy,
                         to_counterclockwise_contour)

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
