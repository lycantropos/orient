from enum import (IntEnum,
                  unique)
from itertools import (chain,
                       groupby)
from typing import (Any,
                    Iterable,
                    Sequence,
                    Tuple)

from robust.angular import (Orientation,
                            orientation)
from robust.linear import segment_contains

from .core import (contour as _contour,
                   polygon as _polygon,
                   segment as _segment)
from .hints import (Contour,
                    Point,
                    Polygon,
                    Segment)


def point_in_segment(point: Point, segment: Segment) -> bool:
    """
    Checks if point lies inside of the segment or is one of its endpoints.

    Time complexity:
        ``O(1)``
    Memory complexity:
        ``O(1)``

    :param point: point to locate.
    :param segment: segment to check.
    :returns:
        true if point lies inside segment or equal to one of its endpoints,
        false otherwise.

    >>> point_in_segment((0, 0), ((0, 0), (1, 0)))
    True
    >>> point_in_segment((0, 1), ((0, 0), (1, 0)))
    False
    """
    return segment_contains(segment, point)


@unique
class PointLocation(IntEnum):
    OUTSIDE = 0
    BOUNDARY = 1
    INSIDE = 2


def point_in_contour(point: Point, contour: Contour) -> PointLocation:
    """
    Finds location of point in relation to contour.

    Based on ray casting algorithm.

    Time complexity:
        ``O(len(contour))``
    Memory complexity:
        ``O(1)``
    Reference:
        https://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm

    :param point: point to locate.
    :param contour: contour to check.
    :returns: location of point in relation to contour.

    >>> square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> point_in_contour((0, 0), square) is PointLocation.BOUNDARY
    True
    >>> point_in_contour((1, 1), square) is PointLocation.INSIDE
    True
    >>> point_in_contour((2, 2), square) is PointLocation.BOUNDARY
    True
    >>> point_in_contour((3, 3), square) is PointLocation.OUTSIDE
    True
    """
    result = False
    _, point_y = point
    for start, end in _contour.to_segments(contour):
        if point_in_segment(point, (start, end)):
            return PointLocation.BOUNDARY
        (_, start_y), (_, end_y) = start, end
        if ((start_y > point_y) is not (end_y > point_y)
                and ((end_y > start_y) is (orientation(end, start, point)
                                           is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return (PointLocation.INSIDE
            if result
            else PointLocation.OUTSIDE)


@unique
class SegmentLocation(IntEnum):
    OUTSIDE = 0
    TOUCH = 1
    CROSS = 2
    BOUNDARY = 3
    INSIDE = 4


def segment_in_contour(segment: Segment, contour: Contour) -> SegmentLocation:
    """
    Finds location of segment in relation to contour.

    Time complexity:
        ``O(len(contour))``
    Memory complexity:
        ``O(1)``

    :param segment: segment to check for.
    :param contour: contour to check in.
    :returns: location of segment in relation to contour.

    >>> square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> (segment_in_contour(((0, 0), (1, 0)), square)
    ...  is SegmentLocation.BOUNDARY)
    True
    >>> (segment_in_contour(((0, 0), (2, 0)), square)
    ...  is SegmentLocation.BOUNDARY)
    True
    >>> segment_in_contour(((2, 0), (3, 0)), square) is SegmentLocation.TOUCH
    True
    >>> segment_in_contour(((3, 0), (4, 0)), square) is SegmentLocation.OUTSIDE
    True
    >>> segment_in_contour(((1, 0), (1, 2)), square) is SegmentLocation.INSIDE
    True
    >>> segment_in_contour(((0, 0), (1, 1)), square) is SegmentLocation.INSIDE
    True
    >>> segment_in_contour(((0, 0), (2, 2)), square) is SegmentLocation.INSIDE
    True
    >>> segment_in_contour(((0, 0), (3, 3)), square) is SegmentLocation.CROSS
    True
    """
    start, end = segment
    try:
        start_index, end_index = contour.index(start), contour.index(end)
    except ValueError:
        start_location, end_location = (point_in_contour(start, contour),
                                        point_in_contour(end, contour))
        if start_location is PointLocation.OUTSIDE:
            return (SegmentLocation.OUTSIDE
                    if end_location is PointLocation.OUTSIDE
                    else (SegmentLocation.TOUCH
                          if end_location is PointLocation.BOUNDARY
                          else SegmentLocation.CROSS))
        elif end_location is PointLocation.OUTSIDE:
            return (SegmentLocation.TOUCH
                    if start_location is PointLocation.BOUNDARY
                    else SegmentLocation.CROSS)
        elif all(_segment.intersects_only_at_endpoints(segment, edge)
                 for edge in _contour.to_segments(contour)):
            return SegmentLocation.INSIDE
        else:
            return SegmentLocation.CROSS
    else:
        min_index, max_index = ((start_index, end_index)
                                if start_index <= end_index
                                else (end_index, start_index))
        return (SegmentLocation.BOUNDARY
                if ((max_index - min_index) == 1
                    or not min_index and max_index == len(contour) - 1)
                else
                (SegmentLocation.INSIDE
                 if _all_equal(chain((orientation(end, start, contour[index])
                                      for index in range(min_index + 1,
                                                         max_index)),
                                     (orientation(start, end, contour[index])
                                      for index in chain(
                                             range(min_index),
                                             range(max_index + 1,
                                                   len(contour))))))
                 else SegmentLocation.CROSS))


def _sort_pair(first: int, second: int) -> Tuple[int, int]:
    return (first, second) if first < second else (second, first)


def _all_equal(iterable: Iterable[Any]) -> bool:
    groups = groupby(iterable)
    return next(groups, True) and not next(groups, False)


def contour_in_contour(left: Contour, right: Contour) -> bool:
    """
    Checks if the contour fully lies inside the region
    bounded by the other one.

    Time complexity:
        ``O((len(left) + len(right)) * log (len(left) + len(right)))``
    Memory complexity:
        ``O(len(left) + len(right))``

    :param left: contour to check for.
    :param right: contour to check in.
    :returns:
        true if the left contour lies inside the right one, false otherwise.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> contour_in_contour(triangle, triangle)
    True
    >>> contour_in_contour(triangle, square)
    True
    >>> contour_in_contour(square, triangle)
    False
    >>> contour_in_contour(square, square)
    True
    """
    return _contour.contains_contour(right, left)


def contours_in_contour(contours: Sequence[Contour],
                        contour: Contour) -> bool:
    """
    Checks if contours fully lie inside the region bounded by other contour.

    Time complexity:
        ``O(vertices_count * log (vertices_count))``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = sum(map(len, contours)) + len(contour)``.

    :param contours: non-overlapping contours to check for.
    :param contour: contour to check in.
    :returns: true if contours lie inside the other contour, false otherwise.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> contours_in_contour([], triangle)
    True
    >>> contours_in_contour([], square)
    True
    >>> contours_in_contour([triangle], triangle)
    True
    >>> contours_in_contour([triangle], square)
    True
    >>> contours_in_contour([square], triangle)
    False
    >>> contours_in_contour([square], square)
    True
    """
    return not contours or _contour.contains_contours(contour, contours)


def point_in_polygon(point: Point, polygon: Polygon) -> PointLocation:
    """
    Finds location of point in relation to polygon.

    Time complexity:
        ``O(vertices_count)``
    Memory complexity:
        ``O(1)``

    where ``vertices_count = len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``.

    :param point: point to check for.
    :param polygon: polygon to check in.
    :returns: location of point in relation to polygon.

    >>> outer_square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    >>> inner_square = [(1, 1), (3, 1), (3, 3), (1, 3)]
    >>> point_in_polygon((0, 0), (inner_square, [])) is PointLocation.OUTSIDE
    True
    >>> point_in_polygon((0, 0), (outer_square, [])) is PointLocation.BOUNDARY
    True
    >>> point_in_polygon((1, 1), (inner_square, [])) is PointLocation.BOUNDARY
    True
    >>> point_in_polygon((1, 1), (outer_square, [])) is PointLocation.INSIDE
    True
    >>> point_in_polygon((2, 2), (outer_square, [])) is PointLocation.INSIDE
    True
    >>> (point_in_polygon((2, 2), (outer_square, [inner_square]))
    ...  is PointLocation.OUTSIDE)
    True
    """
    border, holes = polygon
    border_location = point_in_contour(point, border)
    if border_location is PointLocation.INSIDE:
        for hole in holes:
            hole_location = point_in_contour(point, hole)
            if hole_location is PointLocation.INSIDE:
                return PointLocation.OUTSIDE
            elif hole_location is PointLocation.BOUNDARY:
                return PointLocation.BOUNDARY
    return border_location


def segment_in_polygon(segment: Segment, polygon: Polygon) -> SegmentLocation:
    """
    Checks if the segment fully lies inside the polygon.

    Time complexity:
        ``O(edges_count)``
    Memory complexity:
        ``O(1)``

    where ``edges_count = len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``.

    :param segment: segment to check for.
    :param polygon: polygon to check in.
    :returns:
        true if the segment lies inside the polygon (or on its boundary),
        false otherwise.

    >>> outer_square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    >>> inner_square = [(1, 1), (3, 1), (3, 3), (1, 3)]
    >>> segment_in_polygon(((0, 0), (1, 0)), (outer_square, []))
    True
    >>> segment_in_polygon(((0, 0), (2, 2)), (outer_square, []))
    True
    >>> segment_in_polygon(((0, 0), (4, 4)), (outer_square, []))
    True
    >>> segment_in_polygon(((0, 0), (1, 0)), (outer_square, [inner_square]))
    True
    >>> segment_in_polygon(((0, 0), (2, 2)), (outer_square, [inner_square]))
    False
    >>> segment_in_polygon(((0, 0), (4, 4)), (outer_square, [inner_square]))
    False
    """
    border, holes = polygon
    border_location = segment_in_contour(segment, border)
    if border_location is SegmentLocation.INSIDE:
        for hole in holes:
            hole_location = segment_in_contour(segment, hole)
            if (hole_location is SegmentLocation.INSIDE
                    or hole_location is SegmentLocation.CROSS):
                return SegmentLocation.OUTSIDE
            elif hole_location is SegmentLocation.BOUNDARY:
                return SegmentLocation.BOUNDARY
    return border_location


def polygon_in_polygon(left: Polygon, right: Polygon) -> bool:
    """
    Checks if the contour fully lies inside the region
    bounded by the other one.

    Time complexity:
        ``O(vertices_count * log (vertices_count))``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(left_border) + sum(map(len, left_holes)) \
+ len(right_border) + sum(map(len, right_holes))``,
    ``left_border, left_holes = left``, ``right_border, right_holes = right``.

    :param left: polygon to check for.
    :param right: polygon to check in.
    :returns:
        true if the left polygon lies inside the right one, false otherwise.

    >>> outer_square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> inner_square = [(1, 1), (2, 1), (2, 2), (1, 2)]
    >>> polygon_in_polygon((outer_square, []), (outer_square, []))
    True
    >>> polygon_in_polygon((inner_square, []), (inner_square, []))
    True
    >>> polygon_in_polygon((inner_square, []), (outer_square, []))
    True
    >>> polygon_in_polygon((outer_square, []), (inner_square, []))
    False
    >>> polygon_in_polygon((inner_square, []), (outer_square, [inner_square]))
    False
    >>> polygon_in_polygon((outer_square, [inner_square]), (inner_square, []))
    False
    """
    return _polygon.contains_polygon(right, left)
