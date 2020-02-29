from enum import (IntEnum,
                  unique)

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
class PointPolygonLocation(IntEnum):
    OUTSIDE = 0
    INSIDE = 1
    ON_BORDER = 2


def point_in_polygon(point: Point, border: Contour) -> PointPolygonLocation:
    """
    Finds location of point in relation to polygon given by its border.

    Based on ray casting algorithm.

    Time complexity:
        ``O(len(border))``
    Memory complexity:
        ``O(1)``
    Reference:
        https://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm

    :param point: point to locate.
    :param border:
        border of polygon to check,
        vertices should be listed in counterclockwise order.
    :returns: location of point in relation to polygon.

    >>> border = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> point_in_polygon((0, 0), border) is PointPolygonLocation.ON_BORDER
    True
    >>> point_in_polygon((1, 1), border) is PointPolygonLocation.INSIDE
    True
    >>> point_in_polygon((2, 2), border) is PointPolygonLocation.ON_BORDER
    True
    >>> point_in_polygon((3, 3), border) is PointPolygonLocation.OUTSIDE
    True
    """
    result = False
    _, point_y = point
    for index in range(len(border)):
        start, end = border[index - 1], border[index]
        if point_in_segment(point, (start, end)):
            return PointPolygonLocation.ON_BORDER
        (_, start_y), (_, end_y) = start, end
        if ((start_y > point_y) is not (end_y > point_y)
                and ((end_y > start_y) is (to_orientation(end, start, point)
                                           is Orientation.COUNTERCLOCKWISE))):
            result = not result
    return PointPolygonLocation(result)
