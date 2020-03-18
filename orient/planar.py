from enum import (IntEnum,
                  unique)
from typing import Sequence

from robust.angular import (Orientation,
                            orientation)
from robust.linear import (SegmentsRelationship,
                           segment_contains,
                           segments_relationship)

from .core import contour as _contour
from .hints import (Contour,
                    Point,
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
class PointContourLocation(IntEnum):
    OUTSIDE = 0
    INSIDE = 1
    BOUNDARY = 2


def point_in_contour(point: Point, contour: Contour) -> PointContourLocation:
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
    :param contour:
        contour to check, vertices should be listed in counterclockwise order.
    :returns: location of point in relation to polygon.

    >>> contour = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> point_in_contour((0, 0), contour) is PointContourLocation.BOUNDARY
    True
    >>> point_in_contour((1, 1), contour) is PointContourLocation.INSIDE
    True
    >>> point_in_contour((2, 2), contour) is PointContourLocation.BOUNDARY
    True
    >>> point_in_contour((3, 3), contour) is PointContourLocation.OUTSIDE
    True
    """
    result = False
    _, point_y = point
    for start, end in _contour.to_segments(contour):
        if point_in_segment(point, (start, end)):
            return PointContourLocation.BOUNDARY
        (_, start_y), (_, end_y) = start, end
        if ((start_y > point_y) is not (end_y > point_y)
                and ((end_y > start_y) is (orientation(end, start, point)
                                           is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return PointContourLocation(result)


def segment_in_contour(segment: Segment, contour: Contour) -> bool:
    """
    Checks if the segment fully lies inside the region bounded by the contour.

    Time complexity:
        ``O(len(contour))``
    Memory complexity:
        ``O(1)``

    :param segment: segment to check for.
    :param contour: contour to check in.
    :returns:
        true if the segment lies inside the contour (or on its boundary),
        false otherwise.

    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> segment_in_contour(((0, 0), (1, 0)), square)
    True
    >>> segment_in_contour(((0, 0), (1, 1)), square)
    True
    >>> segment_in_contour(((0, 0), (2, 2)), square)
    False
    >>> segment_in_contour(((1, 0), (2, 0)), square)
    False
    """
    start, end = segment

    def segments_do_not_cross(left: Segment, right: Segment) -> bool:
        return (segments_relationship(left, right)
                is not SegmentsRelationship.CROSS)

    return (bool(point_in_contour(start, contour))
            and bool(point_in_contour(end, contour))
            and all(segments_do_not_cross(segment, edge)
                    for edge in _contour.to_segments(contour)))


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
        ``O((sum(map(len, contours)) + len(contour)) \
* log (sum(map(len, contours)) + len(contour)))``
    Memory complexity:
        ``O(sum(map(len, contours)) + len(contour))``

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
