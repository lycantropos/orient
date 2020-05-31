from .core import (contour as _contour,
                   multipolygon as _multipolygon,
                   multiregion as _multiregion,
                   multisegment as _multisegment,
                   polygon as _polygon,
                   region as _region,
                   segment as _segment)
from .core.relation import Relation
from .hints import (Contour,
                    Multipolygon,
                    Multiregion,
                    Multisegment,
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


def point_in_multisegment(point: Point,
                          multisegment: Multisegment) -> Relation:
    """
    Finds relation between point and multisegment.

    Time complexity:
        ``O(len(multisegment))``
    Memory complexity:
        ``O(1)``

    :param point: point to check for.
    :param multisegment: multisegment to check in.
    :returns: relation between point and multisegment.

    >>> multisegment = [((0, 0), (1, 0)), ((3, 0), (5, 0))]
    >>> point_in_multisegment((0, 0), multisegment) is Relation.COMPONENT
    True
    >>> point_in_multisegment((0, 1), multisegment) is Relation.DISJOINT
    True
    >>> point_in_multisegment((1, 0), multisegment) is Relation.COMPONENT
    True
    >>> point_in_multisegment((2, 0), multisegment) is Relation.DISJOINT
    True
    >>> point_in_multisegment((3, 0), multisegment) is Relation.COMPONENT
    True
    >>> point_in_multisegment((4, 0), multisegment) is Relation.COMPONENT
    True
    """
    return _multisegment.relate_point(multisegment, point)


def segment_in_multisegment(segment: Segment,
                            multisegment: Multisegment) -> Relation:
    """
    Finds relation between segment and multisegment.

    Time complexity:
        ``O(segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment)``.

    :param segment: segment to check for.
    :param multisegment: multisegment to check in.
    :returns: relation between segment and multisegment.

    >>> multisegment = [((0, 0), (1, 1)), ((1, 1), (3, 3))]
    >>> segment_in_multisegment(((0, 0), (1, 0)),
    ...                         multisegment) is Relation.TOUCH
    True
    >>> segment_in_multisegment(((0, 0), (0, 1)),
    ...                         multisegment) is Relation.TOUCH
    True
    >>> segment_in_multisegment(((0, 1), (1, 0)),
    ...                         multisegment) is Relation.CROSS
    True
    >>> segment_in_multisegment(((0, 0), (1, 1)),
    ...                         multisegment) is Relation.COMPONENT
    True
    >>> segment_in_multisegment(((0, 0), (3, 3)),
    ...                         multisegment) is Relation.EQUAL
    True
    >>> segment_in_multisegment(((2, 2), (4, 4)),
    ...                         multisegment) is Relation.OVERLAP
    True
    >>> segment_in_multisegment(((4, 4), (5, 5)),
    ...                         multisegment) is Relation.DISJOINT
    True
    """
    return _multisegment.relate_segment(multisegment, segment)


def multisegment_in_multisegment(left: Multisegment,
                                 right: Multisegment) -> Relation:
    """
    Finds relation between multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(left) + len(right)``.

    :param left: multisegment to check for.
    :param right: multisegment to check in.
    :returns: relation between multisegments.

    >>> triangle_edges = [((0, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 0))]
    >>> square_edges = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)),
    ...                 ((0, 1), (0, 0))]
    >>> multisegment_in_multisegment([], triangle_edges) is Relation.DISJOINT
    True
    >>> multisegment_in_multisegment(triangle_edges,
    ...                              triangle_edges) is Relation.EQUAL
    True
    >>> multisegment_in_multisegment(triangle_edges,
    ...                              square_edges) is Relation.OVERLAP
    True
    >>> multisegment_in_multisegment(square_edges,
    ...                              triangle_edges) is Relation.OVERLAP
    True
    >>> multisegment_in_multisegment(square_edges,
    ...                              square_edges) is Relation.EQUAL
    True
    """
    return _multisegment.relate_multisegment(right, left)


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


def multisegment_in_contour(multisegment: Multisegment,
                            contour: Contour) -> Relation:
    """
    Finds relation between multisegment and contour.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(left) + len(right)``.

    :param multisegment: multisegment to check for.
    :param contour: contour to check in.
    :returns: relation between multisegment and contour.

    >>> triangle_edges = [((0, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 0))]
    >>> square_edges = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)),
    ...                 ((0, 1), (0, 0))]
    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> multisegment_in_contour([], triangle) is Relation.DISJOINT
    True
    >>> multisegment_in_contour(triangle_edges, triangle) is Relation.EQUAL
    True
    >>> multisegment_in_contour(triangle_edges, square) is Relation.OVERLAP
    True
    >>> multisegment_in_contour(square_edges, triangle) is Relation.OVERLAP
    True
    >>> multisegment_in_contour(square_edges, square) is Relation.EQUAL
    True
    """
    return _contour.relate_multisegment(contour, multisegment)


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


def multisegment_in_region(multisegment: Multisegment,
                           region: Region) -> Relation:
    """
    Finds relation between multisegment and region.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment) + len(region)``.

    :param multisegment: multisegment to check for.
    :param region: region to check in.
    :returns: relation between multisegment and region.

    >>> triangle_edges = [((0, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 0))]
    >>> square_edges = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)),
    ...                 ((0, 1), (0, 0))]
    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> multisegment_in_region([], triangle) is Relation.DISJOINT
    True
    >>> multisegment_in_region(triangle_edges, triangle) is Relation.COMPONENT
    True
    >>> multisegment_in_region(triangle_edges, square) is Relation.ENCLOSED
    True
    >>> multisegment_in_region(square_edges, triangle) is Relation.TOUCH
    True
    >>> multisegment_in_region(square_edges, square) is Relation.COMPONENT
    True
    """
    return _region.relate_multisegment(region, multisegment)


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


def multisegment_in_multiregion(multisegment: Multisegment,
                                multiregion: Multiregion) -> Relation:
    """
    Finds relation between multisegment and multiregion.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment) + sum(map(len, multiregion))``.

    :param multisegment: multisegment to check for.
    :param multiregion: multiregion to check in.
    :returns: relation between multisegment and multiregion.

    >>> triangle_edges = [((0, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 0))]
    >>> square_edges = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)),
    ...                 ((0, 1), (0, 0))]
    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> multisegment_in_multiregion([], []) is Relation.DISJOINT
    True
    >>> multisegment_in_multiregion([], [triangle]) is Relation.DISJOINT
    True
    >>> (multisegment_in_multiregion(triangle_edges, [triangle])
    ...  is Relation.COMPONENT)
    True
    >>> (multisegment_in_multiregion(triangle_edges, [square])
    ...  is Relation.ENCLOSED)
    True
    >>> multisegment_in_multiregion(square_edges, [triangle]) is Relation.TOUCH
    True
    >>> (multisegment_in_multiregion(square_edges, [square])
    ...  is Relation.COMPONENT)
    True
    """
    return _multiregion.relate_multisegment(multiregion, multisegment)


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
        ``O(vertices_count * log vertices_count)``
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
        ``O(1)``

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


def multisegment_in_polygon(multisegment: Multisegment,
                            polygon: Polygon) -> Relation:
    """
    Finds relation between multisegment and polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment)\
 + len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``.


    :param multisegment: multisegment to check for.
    :param polygon: polygon to check in.
    :returns: relation between multisegment and polygon.

    >>> triangle_edges = [((0, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 0))]
    >>> square_edges = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)),
    ...                 ((0, 1), (0, 0))]
    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> multisegment_in_polygon([], (triangle, [])) is Relation.DISJOINT
    True
    >>> (multisegment_in_polygon(triangle_edges, (triangle, []))
    ...  is Relation.COMPONENT)
    True
    >>> (multisegment_in_polygon(triangle_edges, (square, []))
    ...  is Relation.ENCLOSED)
    True
    >>> multisegment_in_polygon(square_edges, (triangle, [])) is Relation.TOUCH
    True
    >>> (multisegment_in_polygon(square_edges, (square, []))
    ...  is Relation.COMPONENT)
    True
    """
    return _polygon.relate_multisegment(polygon, multisegment)


def contour_in_polygon(contour: Contour, polygon: Polygon) -> Relation:
    """
    Finds relation between contour and polygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour)\
 + len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``.

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
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(region)\
 + len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``.

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
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = sum(map(len, multiregion))\
 + len(border) + sum(map(len, holes))``,
    ``border, holes = polygon``.

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
    Finds relation between polygons.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(left_border) + sum(map(len, left_holes)) \
+ len(right_border) + sum(map(len, right_holes))``,
    ``left_border, left_holes = left``, ``right_border, right_holes = right``.

    :param left: polygon to check for.
    :param right: polygon to check in.
    :returns: relation between polygons.

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


def point_in_multipolygon(point: Point,
                          multipolygon: Multipolygon) -> Relation:
    """
    Finds relation between point and multipolygon.

    Time complexity:
        ``O(sum(len(border) = sum(map(len, holes))\
 for border, holes in multipolygon))``
    Memory complexity:
        ``O(1)``

    :param point: point to check for.
    :param multipolygon: multipolygon to check in.
    :returns: relation between point and multipolygon.

    >>> triangle = [(0, 0), (2, 0), (0, 2)]
    >>> square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    >>> point_in_multipolygon((0, 0), [(triangle, [])]) is Relation.COMPONENT
    True
    >>> point_in_multipolygon((0, 0), [(square, [])]) is Relation.COMPONENT
    True
    >>> point_in_multipolygon((1, 1), [(triangle, [])]) is Relation.COMPONENT
    True
    >>> point_in_multipolygon((1, 1), [(square, [])]) is Relation.WITHIN
    True
    >>> point_in_multipolygon((2, 2), [(triangle, [])]) is Relation.DISJOINT
    True
    >>> point_in_multipolygon((2, 2), [(square, [])]) is Relation.COMPONENT
    True
    """
    return _multipolygon.relate_point(multipolygon, point)


def segment_in_multipolygon(segment: Segment,
                            multipolygon: Multipolygon) -> Relation:
    """
    Finds relation between segment and multipolygon.

    Time complexity:
        ``O(sum(len(border) = sum(map(len, holes))\
 for border, holes in multipolygon))``
    Memory complexity:
        ``O(1)``

    :param segment: segment to check for.
    :param multipolygon: multipolygon to check in.
    :returns: relation between segment and multipolygon.

    >>> square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> (segment_in_multipolygon(((0, 0), (1, 0)), [])
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_multipolygon(((0, 0), (1, 0)), [(square, [])])
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_multipolygon(((0, 0), (3, 0)), [(square, [])])
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_multipolygon(((2, 0), (4, 0)), [(square, [])])
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_multipolygon(((4, 0), (5, 0)), [(square, [])])
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_multipolygon(((1, 0), (1, 2)), [(square, [])])
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_multipolygon(((0, 0), (1, 1)), [(square, [])])
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_multipolygon(((1, 1), (2, 2)), [(square, [])])
    ...  is Relation.WITHIN)
    True
    >>> (segment_in_multipolygon(((2, 2), (4, 4)), [(square, [])])
    ...  is Relation.CROSS)
    True
    """
    return _multipolygon.relate_segment(multipolygon, segment)


def multisegment_in_multipolygon(multisegment: Multisegment,
                                 multipolygon: Multipolygon) -> Relation:
    """
    Finds relation between multisegment and multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment) + multipolygon_segments_count``,
    ``multipolygon_segments_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in multipolygon)``.

    :param multisegment: multisegment to check for.
    :param multipolygon: multipolygon to check in.
    :returns: relation between multisegment and multipolygon.

    >>> triangle_edges = [((0, 0), (1, 0)), ((1, 0), (0, 1)), ((0, 1), (0, 0))]
    >>> square_edges = [((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)),
    ...                 ((0, 1), (0, 0))]
    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> multisegment_in_multipolygon([], []) is Relation.DISJOINT
    True
    >>> multisegment_in_multipolygon([], [(triangle, [])]) is Relation.DISJOINT
    True
    >>> (multisegment_in_multipolygon(triangle_edges, [(triangle, [])])
    ...  is Relation.COMPONENT)
    True
    >>> (multisegment_in_multipolygon(triangle_edges, [(square, [])])
    ...  is Relation.ENCLOSED)
    True
    >>> (multisegment_in_multipolygon(square_edges, [(triangle, [])])
    ...  is Relation.TOUCH)
    True
    >>> (multisegment_in_multipolygon(square_edges, [(square, [])])
    ...  is Relation.COMPONENT)
    True
    """
    return _multipolygon.relate_multisegment(multipolygon, multisegment)


def contour_in_multipolygon(contour: Contour,
                            multipolygon: Multipolygon) -> Relation:
    """
    Finds relation between contour and multipolygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour) + multipolygon_vertices_count``,
    ``multipolygon_vertices_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in multipolygon)``.

    :param contour: contour to check for.
    :param multipolygon: multipolygon to check in.
    :returns: relation between contour and multipolygon.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> (contour_in_multipolygon(triangle, [(triangle, [])])
    ...  is Relation.COMPONENT)
    True
    >>> contour_in_multipolygon(triangle, [(square, [])]) is Relation.ENCLOSED
    True
    >>> contour_in_multipolygon(square, [(triangle, [])]) is Relation.TOUCH
    True
    >>> contour_in_multipolygon(square, [(square, [])]) is Relation.COMPONENT
    True
    """
    return _multipolygon.relate_contour(multipolygon, contour)


def region_in_multipolygon(region: Region,
                           multipolygon: Multipolygon) -> Relation:
    """
    Finds relation between region and multipolygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(region) + multipolygon_vertices_count``,
    ``multipolygon_vertices_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in multipolygon)``.

    :param region: region to check for.
    :param multipolygon: multipolygon to check in.
    :returns: relation between region and multipolygon.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> region_in_multipolygon(triangle, []) is Relation.DISJOINT
    True
    >>> region_in_multipolygon(square, []) is Relation.DISJOINT
    True
    >>> region_in_multipolygon(triangle, [(triangle, [])]) is Relation.EQUAL
    True
    >>> region_in_multipolygon(square, [(triangle, [])]) is Relation.ENCLOSES
    True
    >>> region_in_multipolygon(triangle, [(square, [])]) is Relation.ENCLOSED
    True
    >>> region_in_multipolygon(square, [(square, [])]) is Relation.EQUAL
    True
    """
    return _multipolygon.relate_region(multipolygon, region)


def multiregion_in_multipolygon(multiregion: Multiregion,
                                multipolygon: Multipolygon) -> Relation:
    """
    Finds relation between multiregion and multipolygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = sum(map(len, multiregion))\
 + multipolygon_vertices_count``,
    ``multipolygon_vertices_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in multipolygon)``.

    :param multiregion: multiregion to check for.
    :param multipolygon: multipolygon to check in.
    :returns: relation between multiregion and multipolygon.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> multiregion_in_multipolygon([], []) is Relation.DISJOINT
    True
    >>> multiregion_in_multipolygon([triangle], []) is Relation.DISJOINT
    True
    >>> multiregion_in_multipolygon([square], []) is Relation.DISJOINT
    True
    >>> (multiregion_in_multipolygon([triangle], [(triangle, [])])
    ...  is Relation.EQUAL)
    True
    >>> (multiregion_in_multipolygon([square], [(triangle, [])])
    ...  is Relation.ENCLOSES)
    True
    >>> (multiregion_in_multipolygon([triangle], [(square, [])])
    ...  is Relation.ENCLOSED)
    True
    >>> multiregion_in_multipolygon([square], [(square, [])]) is Relation.EQUAL
    True
    """
    return _multipolygon.relate_multiregion(multipolygon, multiregion)


def polygon_in_multipolygon(polygon: Polygon,
                            multipolygon: Multipolygon) -> Relation:
    """
    Finds relation between polygon and multipolygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = polygon_vertices_count\
 + multipolygon_vertices_count``,
    ``polygon_vertices_count = len(border) + sum(map(len, holes)``,
    ``border, holes = polygon``,
    ``multipolygon_vertices_count = sum(len(border) + sum(map(len, holes))\
 for border, holes in multipolygon)``.

    :param polygon: polygon to check for.
    :param multipolygon: multipolygon to check in.
    :returns: relation between polygon and multipolygon.

    >>> triangle = [(0, 0), (1, 0), (0, 1)]
    >>> square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    >>> polygon_in_multipolygon((triangle, []), []) is Relation.DISJOINT
    True
    >>> polygon_in_multipolygon((square, []), []) is Relation.DISJOINT
    True
    >>> (polygon_in_multipolygon((triangle, []), [(triangle, [])])
    ...  is Relation.EQUAL)
    True
    >>> (polygon_in_multipolygon((square, []), [(triangle, [])])
    ...  is Relation.ENCLOSES)
    True
    >>> (polygon_in_multipolygon((triangle, []), [(square, [])])
    ...  is Relation.ENCLOSED)
    True
    >>> polygon_in_multipolygon((square, []), [(square, [])]) is Relation.EQUAL
    True
    """
    return _multipolygon.relate_polygon(multipolygon, polygon)


def multipolygon_in_multipolygon(left: Multipolygon,
                                 right: Multipolygon) -> Relation:
    """
    Finds relation between multipolygons.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = left_multipolygon_vertices_count\
 + right_multipolygon_vertices_count ``,
    ``left_multipolygon_vertices_count = sum(len(border)\
 + sum(map(len, holes)) for border, holes in multipolygon)``.
    ``right_multipolygon_vertices_count = sum(len(border)\
 + sum(map(len, holes)) for border, holes in multipolygon)``.

    :param left: multipolygon to check for.
    :param right: multipolygon to check in.
    :returns: relation between multipolygons.

    >>> outer_square = [(0, 0), (3, 0), (3, 3), (0, 3)]
    >>> inner_square = [(1, 1), (2, 1), (2, 2), (1, 2)]
    >>> multipolygon_in_multipolygon([], []) is Relation.DISJOINT
    True
    >>> (multipolygon_in_multipolygon([(inner_square, [])], [])
    ...  is Relation.DISJOINT)
    True
    >>> multipolygon_in_multipolygon([(inner_square, [])],
    ...                              [(inner_square, [])]) is Relation.EQUAL
    True
    >>> multipolygon_in_multipolygon([(inner_square, [])],
    ...                              [(outer_square, [])]) is Relation.WITHIN
    True
    >>> (multipolygon_in_multipolygon([(inner_square, [])],
    ...                               [(outer_square, [inner_square])])
    ...  is Relation.TOUCH)
    True
    >>> (multipolygon_in_multipolygon([(outer_square, [inner_square])],
    ...                               [(outer_square, [])])
    ...  is Relation.ENCLOSED)
    True
    """
    return _multipolygon.relate_multipolygon(right, left)
