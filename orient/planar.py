from enum import (IntEnum,
                  unique)

from .core import intra_contour as _intra_contour
from .core.angular import (Orientation,
                           to_orientation)
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
    start, end = segment
    if point == start:
        return True
    elif point == end:
        return True
    else:
        point_x, point_y = point
        (start_x, start_y), (end_x, end_y) = start, end
        left_x, right_x = ((start_x, end_x)
                           if start_x < end_x
                           else (end_x, start_x))
        bottom_y, top_y = ((start_y, end_y)
                           if start_y < end_y
                           else (end_y, start_y))
        return (left_x <= point_x <= right_x and bottom_y <= point_y <= top_y
                and to_orientation(end, start, point) is Orientation.COLLINEAR)


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
    for index in range(len(contour)):
        start, end = contour[index - 1], contour[index]
        if point_in_segment(point, (start, end)):
            return PointContourLocation.BOUNDARY
        (_, start_y), (_, end_y) = start, end
        if ((start_y > point_y) is not (end_y > point_y)
                and ((end_y > start_y) is (to_orientation(end, start, point)
                                           is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return PointContourLocation(result)


def contour_in_contour(left: Contour, right: Contour) -> bool:
    """
    Checks if the contour fully lies inside the region
    bounded by the other one.

    Time complexity:
        ``O((len(left) + len(right)) * log (len(left) + len(right)))``
    Memory complexity:
        ``O((len(left) + len(right)) * log (len(left) + len(right)))``

    :param left:
        contour to check for,
        vertices should be listed in counterclockwise order.
    :param right:
        contour to check in,
        vertices should be listed in counterclockwise order.
    :returns:
        true if the left contour lies inside the other one, false otherwise.

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
    return (_intra_contour.bounding_box_in_bounding_box(left, right)
            and _intra_contour.sweep(left, right))
