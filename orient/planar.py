from .core import (contour as _contour,
                   multicontour as _multicontour,
                   polygon as _polygon,
                   segment as _segment)
from .core.relation import Relation
from .hints import (Contour,
                    Multicontour,
                    Point,
                    Polygon,
                    Segment)

Relation = Relation


def point_in_segment(point: Point, segment: Segment) -> Relation:
    """
    Finds relation between point and segment.

    Time complexity:
        ``O(1)``
    Memory complexity:
        ``O(1)``

    :param point: point to locate.
    :param segment: segment to check.
    :returns: relation between point and segment.

    >>> segment = ((0, 0), (2, 0))
    >>> point_in_segment((0, 0), segment) is Relation.COMPONENT
    True
    >>> point_in_segment((1, 0), segment) is Relation.COMPONENT
    True
    >>> point_in_segment((2, 0), segment) is Relation.COMPONENT
    True
    >>> point_in_segment((3, 0), segment) is Relation.DISJOINT
    True
    >>> point_in_segment((0, 1), segment) is Relation.DISJOINT
    True
    """
    return _segment.relate_point(segment, point)


def point_in_contour(point: Point, contour: Contour) -> Relation:
    """
    Finds relation between point and contour.

    Based on ray casting algorithm.

    Time complexity:
        ``O(len(contour))``
    Memory complexity:
        ``O(1)``
    Reference:
        https://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm

    :param point: point to locate.
    :param contour: contour to check.
    :returns: relation between point and contour.

    >>> square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> point_in_contour((0, 0), square) is Relation.COMPONENT
    True
    >>> point_in_contour((1, 1), square) is Relation.WITHIN
    True
    >>> point_in_contour((2, 2), square) is Relation.COMPONENT
    True
    >>> point_in_contour((3, 3), square) is Relation.DISJOINT
    True
    """
    return _contour.relate_point(contour, point)


def segment_in_contour(segment: Segment, contour: Contour) -> Relation:
    """
    Finds relation between segment and contour.

    Time complexity:
        ``O(len(contour))``
    Memory complexity:
        ``O(len(contour))``

    :param segment: segment to check for.
    :param contour: contour to check in.
    :returns: relation between segment and contour.

    >>> square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> (segment_in_contour(((0, 0), (1, 0)), square)
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_contour(((0, 0), (3, 0)), square)
    ...  is Relation.COMPONENT)
    True
    >>> segment_in_contour(((2, 0), (4, 0)), square) is Relation.TOUCH
    True
    >>> (segment_in_contour(((4, 0), (5, 0)), square)
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_contour(((1, 0), (1, 2)), square)
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_contour(((0, 0), (1, 1)), square)
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_contour(((1, 1), (2, 2)), square)
    ...  is Relation.WITHIN)
    True
    >>> segment_in_contour(((2, 2), (4, 4)), square) is Relation.CROSS
    True
    """
    return _contour.relate_segment(contour, segment)


def contour_in_contour(left: Contour, right: Contour) -> Relation:
    """
    Finds relation between contours.

    Time complexity:
        ``O((len(left) + len(right)) * log (len(left) + len(right)))``
    Memory complexity:
        ``O(len(left) + len(right))``

    :param left: contour to check for.
    :param right: contour to check in.
    :returns: relation between contours.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> contour_in_contour(triangle, triangle) is Relation.EQUAL
    True
    >>> contour_in_contour(triangle, square) is Relation.ENCLOSED
    True
    >>> contour_in_contour(square, triangle) is Relation.ENCLOSES
    True
    >>> contour_in_contour(square, square) is Relation.EQUAL
    True
    """
    return _contour.relate_contour(right, left)


def contour_in_multicontour(contour: Contour,
                            multicontour: Multicontour) -> Relation:
    """
    Finds relation between contour and multicontour.

    Time complexity:
        ``O(vertices_count * log (vertices_count))``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour) + sum(map(len, multicontour))``.

    :param contour: contour to check for.
    :param multicontour: multicontour to check in.
    :returns: relation between contour and multicontour.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> contour_in_multicontour(triangle, []) is Relation.DISJOINT
    True
    >>> contour_in_multicontour(square, []) is Relation.DISJOINT
    True
    >>> contour_in_multicontour(triangle, [triangle]) is Relation.EQUAL
    True
    >>> contour_in_multicontour(square, [triangle]) is Relation.ENCLOSES
    True
    >>> contour_in_multicontour(triangle, [square]) is Relation.ENCLOSED
    True
    >>> contour_in_multicontour(square, [square]) is Relation.EQUAL
    True
    """
    return _multicontour.relate_contour(multicontour, contour)


def point_in_polygon(point: Point, polygon: Polygon) -> Relation:
    """
    Finds relation between point and polygon.

    Time complexity:
        ``O(vertices_count)``
    Memory complexity:
        ``O(1)``

    where ``vertices_count = len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``.

    :param point: point to check for.
    :param polygon: polygon to check in.
    :returns: relation between point and polygon.

    >>> outer_square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    >>> inner_square = [(1, 1), (3, 1), (3, 3), (1, 3)]
    >>> point_in_polygon((0, 0), (inner_square, [])) is Relation.DISJOINT
    True
    >>> point_in_polygon((0, 0), (outer_square, [])) is Relation.COMPONENT
    True
    >>> point_in_polygon((1, 1), (inner_square, [])) is Relation.COMPONENT
    True
    >>> point_in_polygon((1, 1), (outer_square, [])) is Relation.WITHIN
    True
    >>> point_in_polygon((2, 2), (outer_square, [])) is Relation.WITHIN
    True
    >>> (point_in_polygon((2, 2), (outer_square, [inner_square]))
    ...  is Relation.DISJOINT)
    True
    """
    return _polygon.relate_point(polygon, point)


def segment_in_polygon(segment: Segment, polygon: Polygon) -> Relation:
    """
    Finds relation between segment and polygon.

    Time complexity:
        ``O(edges_count)``
    Memory complexity:
        ``O(edges_count)``

    where ``edges_count = len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``.

    :param segment: segment to check for.
    :param polygon: polygon to check in.
    :returns: relation between segment and polygon.

    >>> outer_square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    >>> inner_square = [(1, 1), (3, 1), (3, 3), (1, 3)]
    >>> (segment_in_polygon(((0, 0), (1, 0)), (outer_square, []))
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_polygon(((0, 0), (1, 0)), (outer_square, [inner_square]))
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_polygon(((0, 0), (2, 2)), (outer_square, []))
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_polygon(((0, 0), (2, 2)), (outer_square, [inner_square]))
    ...  is Relation.CROSS)
    True
    >>> (segment_in_polygon(((1, 1), (3, 3)), (outer_square, []))
    ...  is Relation.WITHIN)
    True
    >>> (segment_in_polygon(((1, 1), (3, 3)), (outer_square, [inner_square]))
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_polygon(((0, 0), (4, 4)), (outer_square, []))
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_polygon(((0, 0), (4, 4)), (outer_square, [inner_square]))
    ...  is Relation.CROSS)
    True
    """
    return _polygon.relate_segment(polygon, segment)


def polygon_in_polygon(left: Polygon, right: Polygon) -> Relation:
    """
    Checks if the polygon fully lies inside the other one.

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
    >>> (polygon_in_polygon((outer_square, []), (outer_square, []))
    ...  is Relation.EQUAL)
    True
    >>> (polygon_in_polygon((inner_square, []), (inner_square, []))
    ...  is Relation.EQUAL)
    True
    >>> (polygon_in_polygon((inner_square, []), (outer_square, []))
    ...  is Relation.WITHIN)
    True
    >>> (polygon_in_polygon((outer_square, []), (inner_square, []))
    ...  is Relation.COVER)
    True
    >>> (polygon_in_polygon((inner_square, []), (outer_square, [inner_square]))
    ...  is Relation.TOUCH)
    True
    >>> (polygon_in_polygon((outer_square, []), (outer_square, [inner_square]))
    ...  is Relation.ENCLOSES)
    True
    >>> (polygon_in_polygon((outer_square, [inner_square]), (inner_square, []))
    ...  is Relation.TOUCH)
    True
    >>> (polygon_in_polygon((outer_square, [inner_square]), (outer_square, []))
    ...  is Relation.ENCLOSED)
    True
    """
    return _polygon.relate_polygon(right, left)
