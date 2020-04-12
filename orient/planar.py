from .core import (contour as _contour,
                   multiregion as _multiregion,
                   polygon as _polygon,
                   region as _region,
                   segment as _segment)
from .core.relation import Relation
from .hints import (Contour,
                    Multiregion,
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
    >>> segment_in_segment(((0, 0), (0, 2)), segment) is Relation.TOUCH
    True
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


def point_in_contour(point: Point, contour: Contour) -> Relation:
    """
    Finds relation between point and contour.

    Time complexity:
        ``O(len(contour))``
    Memory complexity:
        ``O(1)``

    :param point: point to check for.
    :param contour: contour to check in.
    :returns: relation between point and contour.

    >>> square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> point_in_contour((0, 0), square) is Relation.COMPONENT
    True
    >>> point_in_contour((1, 1), square) is Relation.DISJOINT
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
        ``O(1)``

    :param segment: segment to check for.
    :param contour: contour to check in.
    :returns: relation between segment and contour.

    >>> square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> segment_in_contour(((0, 0), (1, 0)), square) is Relation.COMPONENT
    True
    >>> segment_in_contour(((0, 0), (3, 0)), square) is Relation.COMPONENT
    True
    >>> segment_in_contour(((2, 0), (4, 0)), square) is Relation.OVERLAP
    True
    >>> segment_in_contour(((4, 0), (5, 0)), square) is Relation.DISJOINT
    True
    >>> segment_in_contour(((1, 0), (1, 2)), square) is Relation.TOUCH
    True
    >>> segment_in_contour(((0, 0), (1, 1)), square) is Relation.TOUCH
    True
    >>> segment_in_contour(((1, 1), (2, 2)), square) is Relation.DISJOINT
    True
    >>> segment_in_contour(((2, 2), (4, 4)), square) is Relation.CROSS
    True
    """
    return _contour.relate_segment(contour, segment)


def contour_in_contour(left: Contour, right: Contour) -> Relation:
    """
    Finds relation between contours.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(left) + len(right)``.

    :param left: contour to check for.
    :param right: contour to check in.
    :returns: relation between contours.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> contour_in_contour(triangle, triangle) is Relation.EQUAL
    True
    >>> contour_in_contour(triangle, square) is Relation.OVERLAP
    True
    >>> contour_in_contour(square, triangle) is Relation.OVERLAP
    True
    >>> contour_in_contour(square, square) is Relation.EQUAL
    True
    """
    return _contour.relate_contour(right, left)


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
        ``O(1)``

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


def contour_in_region(contour: Contour, region: Region) -> Relation:
    """
    Finds relation between contour and region.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour) + len(region)``.

    :param contour: contour to check for.
    :param region: region to check in.
    :returns: relation between contour and region.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> contour_in_region(triangle, triangle) is Relation.COMPONENT
    True
    >>> contour_in_region(triangle, square) is Relation.ENCLOSED
    True
    >>> contour_in_region(square, triangle) is Relation.TOUCH
    True
    >>> contour_in_region(square, square) is Relation.COMPONENT
    True
    """
    return _region.relate_contour(region, contour)


def region_in_region(left: Region, right: Region) -> Relation:
    """
    Finds relation between regions.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(left) + len(right)``.

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


def point_in_multiregion(point: Point, multiregion: Multiregion) -> Relation:
    """
    Finds relation between point and multiregion.

    Time complexity:
        ``O(sum(map(len, multiregion)))``
    Memory complexity:
        ``O(1)``

    :param point: point to check for.
    :param multiregion: multiregion to check in.
    :returns: relation between point and multiregion.

    >>> triangle = [(0, 0), (2, 0), (0, 2)]
    >>> square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> point_in_multiregion((0, 0), [triangle]) is Relation.COMPONENT
    True
    >>> point_in_multiregion((0, 0), [square]) is Relation.COMPONENT
    True
    >>> point_in_multiregion((1, 1), [triangle]) is Relation.COMPONENT
    True
    >>> point_in_multiregion((1, 1), [square]) is Relation.WITHIN
    True
    >>> point_in_multiregion((2, 2), [triangle]) is Relation.DISJOINT
    True
    >>> point_in_multiregion((2, 2), [square]) is Relation.COMPONENT
    True
    """
    return _multiregion.relate_point(multiregion, point)


def segment_in_multiregion(segment: Segment,
                           multiregion: Multiregion) -> Relation:
    """
    Finds relation between segment and multiregion.

    Time complexity:
        ``O(sum(map(len, multiregion)))``
    Memory complexity:
        ``O(1)``

    :param segment: segment to check for.
    :param multiregion: multiregion to check in.
    :returns: relation between segment and multiregion.

    >>> square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> (segment_in_multiregion(((0, 0), (1, 0)), [])
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_multiregion(((0, 0), (1, 0)), [square])
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_multiregion(((0, 0), (3, 0)), [square])
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_multiregion(((2, 0), (4, 0)), [square])
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_multiregion(((4, 0), (5, 0)), [square])
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_multiregion(((1, 0), (1, 2)), [square])
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_multiregion(((0, 0), (1, 1)), [square])
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_multiregion(((1, 1), (2, 2)), [square])
    ...  is Relation.WITHIN)
    True
    >>> segment_in_multiregion(((2, 2), (4, 4)), [square]) is Relation.CROSS
    True
    """
    return _multiregion.relate_segment(multiregion, segment)


def contour_in_multiregion(contour: Contour,
                           multiregion: Multiregion) -> Relation:
    """
    Finds relation between contour and multiregion.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour) + sum(map(len, multiregion))``.

    :param contour: contour to check for.
    :param multiregion: multiregion to check in.
    :returns: relation between contour and multiregion.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> contour_in_multiregion(triangle, [triangle]) is Relation.COMPONENT
    True
    >>> contour_in_multiregion(triangle, [square]) is Relation.ENCLOSED
    True
    >>> contour_in_multiregion(square, [triangle]) is Relation.TOUCH
    True
    >>> contour_in_multiregion(square, [square]) is Relation.COMPONENT
    True
    """
    return _multiregion.relate_contour(multiregion, contour)


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


def multiregion_in_multiregion(left: Multiregion,
                               right: Multiregion) -> Relation:
    """
    Finds relation between multiregions.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = sum(map(len, left)) + sum(map(len, right))``.

    :param left: multiregion to check for.
    :param right: multiregion to check in.
    :returns: relation between multiregions.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> multiregion_in_multiregion([triangle], [triangle]) is Relation.EQUAL
    True
    >>> multiregion_in_multiregion([triangle], [square]) is Relation.ENCLOSED
    True
    >>> multiregion_in_multiregion([square], [triangle]) is Relation.ENCLOSES
    True
    >>> multiregion_in_multiregion([square], [square]) is Relation.EQUAL
    True
    """
    return _multiregion.relate_multiregion(right, left)


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
        ``O(vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(border) + sum(map(len, holes))``,
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


def contour_in_polygon(contour: Contour, polygon: Polygon) -> Relation:
    """
    Finds relation between contour and polygon.

    Time complexity:
        ``O(vertices_count * log (vertices_count))``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour)\
 + len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``

    :param contour: contour to check for.
    :param polygon: polygon to check in.
    :returns: relation between contour and polygon.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> contour_in_polygon(triangle, (triangle, [])) is Relation.COMPONENT
    True
    >>> contour_in_polygon(triangle, (square, [])) is Relation.ENCLOSED
    True
    >>> contour_in_polygon(square, (triangle, [])) is Relation.TOUCH
    True
    >>> contour_in_polygon(square, (square, [])) is Relation.COMPONENT
    True
    """
    return _polygon.relate_contour(polygon, contour)


def region_in_polygon(region: Region, polygon: Polygon) -> Relation:
    """
    Finds relation between region and polygon.

    Time complexity:
        ``O(vertices_count * log (vertices_count))``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(region)\
 + len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``

    :param region: region to check for.
    :param polygon: polygon to check in.
    :returns: relation between region and polygon.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> region_in_polygon(triangle, (triangle, [])) is Relation.EQUAL
    True
    >>> region_in_polygon(square, (triangle, [])) is Relation.ENCLOSES
    True
    >>> region_in_polygon(triangle, (square, [])) is Relation.ENCLOSED
    True
    >>> region_in_polygon(square, (square, [])) is Relation.EQUAL
    True
    """
    return _polygon.relate_region(polygon, region)


def multiregion_in_polygon(multiregion: Multiregion,
                           polygon: Polygon) -> Relation:
    """
    Finds relation between multiregion and polygon.

    Time complexity:
        ``O(vertices_count * log (vertices_count))``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = sum(map(len, multiregion))\
 + len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``

    :param multiregion: multiregion to check for.
    :param polygon: polygon to check in.
    :returns: relation between multiregion and polygon.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> multiregion_in_polygon([triangle], (triangle, [])) is Relation.EQUAL
    True
    >>> multiregion_in_polygon([square], (triangle, [])) is Relation.ENCLOSES
    True
    >>> multiregion_in_polygon([triangle], (square, [])) is Relation.ENCLOSED
    True
    >>> multiregion_in_polygon([square], (square, [])) is Relation.EQUAL
    True
    """
    return _polygon.relate_multiregion(polygon, multiregion)


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
