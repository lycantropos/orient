from typing import Tuple

from hypothesis import strategies
from hypothesis_geometry import planar

from orient.hints import (Coordinate,
                          Point,
                          Segment)
from tests.strategies import coordinates_strategies
from tests.utils import Strategy

segments = coordinates_strategies.flatmap(planar.segments)


def to_segments_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Segment, Point]]:
    return strategies.tuples(planar.segments(coordinates),
                             planar.points(coordinates))


segments_with_points = coordinates_strategies.flatmap(to_segments_with_points)
