from .core import (multiregion as _multiregion,
                   polygon as _polygon,
                   region as _region,
                   segment as _segment)
from .core.relation import Relation
from .hints import (Multiregion,
                    Point,
                    Polygon,
                    Region,
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


def segment_in_segment(left: Segment, right: Segment) -> Relation:
    """
    Finds relation between segments.

    Time complexity:
        ``O(1)``
    Memory complexity:
        ``O(1)``

    :param left: point to locate.
    :param right: segment to check im.
    :returns: relation between segments.

    >>> segment = ((0, 0), (2, 0))
    >>> segment_in_segment(((0, 0), (1, 0)), segment) is Relation.COMPONENT
    True
    >>> segment_in_segment(((0, 0), (2, 0)), segment) is Relation.EQUAL
    True
    >>> segment_in_segment(((0, 0), (3, 0)), segment) is Relation.COMPOSITE
    True
    >>> segment_in_segment(((1, 0), (3, 0)), segment) is Relation.OVERLAP
    True
    >>> segment_in_segment(((2, 0), (3, 0)), segment) is Relation.TOUCH
    True
    >>> segment_in_segment(((3, 0), (4, 0)), segment) is Relation.DISJOINT
    True
    """
    return _segment.relate_segment(right, left)


def point_in_region(point: Point, region: Region) -> Relation:
    """
    Finds relation between point and region.

    Based on ray casting algorithm.

    Time complexity:
        ``O(len(region))``
    Memory complexity:
        ``O(1)``
    Reference:
        https://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm

    :param point: point to check for.
    :param region: region to check in.
    :returns: relation between point and region.

    >>> square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> point_in_region((0, 0), square) is Relation.COMPONENT
    True
    >>> point_in_region((1, 1), square) is Relation.WITHIN
    True
    >>> point_in_region((2, 2), square) is Relation.COMPONENT
    True
    >>> point_in_region((3, 3), square) is Relation.DISJOINT
    True
    """
    return _region.relate_point(region, point)


def segment_in_region(segment: Segment, region: Region) -> Relation:
    """
    Finds relation between segment and region.

    Time complexity:
        ``O(len(region))``
    Memory complexity:
        ``O(len(region))``

    :param segment: segment to check for.
    :param region: region to check in.
    :returns: relation between segment and region.

    >>> square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> segment_in_region(((0, 0), (1, 0)), square) is Relation.COMPONENT
    True
    >>> segment_in_region(((0, 0), (3, 0)), square) is Relation.COMPONENT
    True
    >>> segment_in_region(((2, 0), (4, 0)), square) is Relation.TOUCH
    True
    >>> segment_in_region(((4, 0), (5, 0)), square) is Relation.DISJOINT
    True
    >>> segment_in_region(((1, 0), (1, 2)), square) is Relation.ENCLOSED
    True
    >>> segment_in_region(((0, 0), (1, 1)), square) is Relation.ENCLOSED
    True
    >>> segment_in_region(((1, 1), (2, 2)), square) is Relation.WITHIN
    True
    >>> segment_in_region(((2, 2), (4, 4)), square) is Relation.CROSS
    True
    """
    return _region.relate_segment(region, segment)


def region_in_region(left: Region, right: Region) -> Relation:
    """
    Finds relation between regions.

    Time complexity:
        ``O((len(left) + len(right)) * log (len(left) + len(right)))``
    Memory complexity:
        ``O(len(left) + len(right))``

    :param left: region to check for.
    :param right: region to check in.
    :returns: relation between regions.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> region_in_region(triangle, triangle) is Relation.EQUAL
    True
    >>> region_in_region(triangle, square) is Relation.ENCLOSED
    True
    >>> region_in_region(square, triangle) is Relation.ENCLOSES
    True
    >>> region_in_region(square, square) is Relation.EQUAL
    True
    """
    return _region.relate_region(right, left)


def region_in_multiregion(region: Region,
                          multiregion: Multiregion) -> Relation:
    """
    Finds relation between region and multiregion.

    Time complexity:
        ``O(vertices_count * log (vertices_count))``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(region) + sum(map(len, multiregion))``.

    :param region: region to check for.
    :param multiregion: multiregion to check in.
    :returns: relation between region and multiregion.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> region_in_multiregion(triangle, []) is Relation.DISJOINT
    True
    >>> region_in_multiregion(square, []) is Relation.DISJOINT
    True
    >>> region_in_multiregion(triangle, [triangle]) is Relation.EQUAL
    True
    >>> region_in_multiregion(square, [triangle]) is Relation.ENCLOSES
    True
    >>> region_in_multiregion(triangle, [square]) is Relation.ENCLOSED
    True
    >>> region_in_multiregion(square, [square]) is Relation.EQUAL
    True
    """
    return _multiregion.relate_region(multiregion, region)


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
