from functools import partial
from typing import (List,
                    Optional,
                    Tuple)

from hypothesis import strategies
from hypothesis_geometry import planar

from orient.hints import (Contour,
                          Coordinate,
                          Point,
                          Polygon,
                          Segment)
from tests.strategies import coordinates_strategies
from tests.utils import (Strategy,
                         to_pairs,
                         to_triplets)

segments = coordinates_strategies.flatmap(planar.segments)


def to_segments_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Segment, Point]]:
    return strategies.tuples(planar.segments(coordinates),
                             planar.points(coordinates))


segments_with_points = coordinates_strategies.flatmap(to_segments_with_points)
contours = coordinates_strategies.flatmap(planar.contours)


def to_contours_with_segments(coordinates: Strategy[Coordinate]
                              ) -> Strategy[Tuple[Contour, Segment]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.segments(coordinates))


contours_with_segments = (coordinates_strategies
                          .flatmap(to_contours_with_segments))


def to_contours_with_contours_lists(coordinates: Strategy[Coordinate],
                                    *,
                                    min_size: int = 0,
                                    max_size: Optional[int] = None
                                    ) -> Strategy[Tuple[Contour,
                                                        List[Contour]]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.multicontours(coordinates,
                                                  min_size=min_size,
                                                  max_size=max_size))


contours_with_contours_lists = (coordinates_strategies
                                .flatmap(to_contours_with_contours_lists))
contours_with_empty_contours_lists = strategies.tuples(contours,
                                                       strategies.builds(list))
contours_with_non_empty_contours_lists = coordinates_strategies.flatmap(
        partial(to_contours_with_contours_lists,
                min_size=1))


def to_contours_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Contour, Point]]:
    return strategies.tuples(planar.contours(coordinates),
                             planar.points(coordinates))


contours_with_points = coordinates_strategies.flatmap(to_contours_with_points)
contours_strategies = coordinates_strategies.map(planar.contours)
contours_pairs = contours_strategies.flatmap(to_pairs)
contours_triplets = contours_strategies.flatmap(to_triplets)


def to_polygons_with_points(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Tuple[Polygon, Point]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.points(coordinates))


polygons_with_points = coordinates_strategies.flatmap(to_polygons_with_points)
polygons = coordinates_strategies.flatmap(planar.polygons)


def to_polygons_with_segments(coordinates: Strategy[Coordinate]
                              ) -> Strategy[Tuple[Polygon, Segment]]:
    return strategies.tuples(planar.polygons(coordinates),
                             planar.segments(coordinates))


polygons_with_segments = (coordinates_strategies
                          .flatmap(to_polygons_with_segments))

polygons_strategies = coordinates_strategies.map(planar.polygons)
polygons_pairs = polygons_strategies.flatmap(to_pairs)
polygons_triplets = polygons_strategies.flatmap(to_triplets)
