from typing import Optional as _Optional

from ground.base import (Context as _Context,
                         Relation as _Relation,
                         get_context as _get_context)
from ground.hints import (Contour as _Contour,
                          Multipolygon as _Multipolygon,
                          Multisegment as _Multisegment,
                          Point as _Point,
                          Polygon as _Polygon,
                          Segment as _Segment)

from .core import (contour as _contour,
                   multipolygon as _multipolygon,
                   multiregion as _multiregion,
                   multisegment as _multisegment,
                   polygon as _polygon,
                   region as _region,
                   segment as _segment)
from .hints import (Multiregion as _Multiregion,
                    Region as _Region)


def point_in_segment(point: _Point, segment: _Segment,
                     *,
                     context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between point and segment.

    Time complexity:
        ``O(1)``
    Memory complexity:
        ``O(1)``

    :param point: point to check for.
    :param segment: segment to check in.
    :param context: geometric context.
    :returns: relation between point and segment.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> segment = Segment(Point(0, 0), Point(2, 0))
    >>> point_in_segment(Point(0, 0), segment) is Relation.COMPONENT
    True
    >>> point_in_segment(Point(1, 0), segment) is Relation.COMPONENT
    True
    >>> point_in_segment(Point(2, 0), segment) is Relation.COMPONENT
    True
    >>> point_in_segment(Point(3, 0), segment) is Relation.DISJOINT
    True
    >>> point_in_segment(Point(0, 1), segment) is Relation.DISJOINT
    True
    """
    return _segment.relate_point(
            segment, point, _get_context() if context is None else context)


def segment_in_segment(left: _Segment, right: _Segment,
                       *,
                       context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between segments.

    Time complexity:
        ``O(1)``
    Memory complexity:
        ``O(1)``

    :param left: point to check for.
    :param right: segment to check in.
    :param context: geometric context.
    :returns: relation between segments.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> segment = Segment(Point(0, 0), Point(2, 0))
    >>> (segment_in_segment(Segment(Point(0, 0), Point(0, 2)), segment)
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_segment(Segment(Point(0, 0), Point(1, 0)), segment)
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_segment(Segment(Point(0, 0), Point(2, 0)), segment)
    ...  is Relation.EQUAL)
    True
    >>> (segment_in_segment(Segment(Point(0, 0), Point(3, 0)), segment)
    ...  is Relation.COMPOSITE)
    True
    >>> (segment_in_segment(Segment(Point(1, 0), Point(3, 0)), segment)
    ...  is Relation.OVERLAP)
    True
    >>> (segment_in_segment(Segment(Point(2, 0), Point(3, 0)), segment)
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_segment(Segment(Point(3, 0), Point(4, 0)), segment)
    ...  is Relation.DISJOINT)
    True
    """
    return _segment.relate_segment(
            right, left, _get_context() if context is None else context)


def point_in_multisegment(point: _Point,
                          multisegment: _Multisegment,
                          *,
                          context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between point and multisegment.

    Time complexity:
        ``O(len(multisegment.segments))``
    Memory complexity:
        ``O(1)``

    :param point: point to check for.
    :param multisegment: multisegment to check in.
    :param context: geometric context.
    :returns: relation between point and multisegment.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 0)),
    ...                              Segment(Point(3, 0), Point(5, 0))])
    >>> point_in_multisegment(Point(0, 0), multisegment) is Relation.COMPONENT
    True
    >>> point_in_multisegment(Point(0, 1), multisegment) is Relation.DISJOINT
    True
    >>> point_in_multisegment(Point(1, 0), multisegment) is Relation.COMPONENT
    True
    >>> point_in_multisegment(Point(2, 0), multisegment) is Relation.DISJOINT
    True
    >>> point_in_multisegment(Point(3, 0), multisegment) is Relation.COMPONENT
    True
    >>> point_in_multisegment(Point(4, 0), multisegment) is Relation.COMPONENT
    True
    """
    return _multisegment.relate_point(
            multisegment, point,
            _get_context() if context is None else context)


def segment_in_multisegment(segment: _Segment,
                            multisegment: _Multisegment,
                            *,
                            context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between segment and multisegment.

    Time complexity:
        ``O(segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment.segments)``.

    :param segment: segment to check for.
    :param multisegment: multisegment to check in.
    :param context: geometric context.
    :returns: relation between segment and multisegment.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> multisegment = Multisegment([Segment(Point(0, 0), Point(1, 1)),
    ...                              Segment(Point(1, 1), Point(3, 3))])
    >>> segment_in_multisegment(Segment(Point(0, 0), Point(1, 0)),
    ...                         multisegment) is Relation.TOUCH
    True
    >>> segment_in_multisegment(Segment(Point(0, 0), Point(0, 1)),
    ...                         multisegment) is Relation.TOUCH
    True
    >>> segment_in_multisegment(Segment(Point(0, 1), Point(1, 0)),
    ...                         multisegment) is Relation.CROSS
    True
    >>> segment_in_multisegment(Segment(Point(0, 0), Point(1, 1)),
    ...                         multisegment) is Relation.COMPONENT
    True
    >>> segment_in_multisegment(Segment(Point(0, 0), Point(3, 3)),
    ...                         multisegment) is Relation.EQUAL
    True
    >>> segment_in_multisegment(Segment(Point(2, 2), Point(4, 4)),
    ...                         multisegment) is Relation.OVERLAP
    True
    >>> segment_in_multisegment(Segment(Point(4, 4), Point(5, 5)),
    ...                         multisegment) is Relation.DISJOINT
    True
    """
    return _multisegment.relate_segment(
            multisegment, segment,
            _get_context() if context is None else context)


def multisegment_in_multisegment(left: _Multisegment,
                                 right: _Multisegment,
                                 *,
                                 context: _Optional[_Context] = None
                                 ) -> _Relation:
    """
    Finds relation between multisegments.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(left.segments) + len(right.segments)``.

    :param left: multisegment to check for.
    :param right: multisegment to check in.
    :param context: geometric context.
    :returns: relation between multisegments.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> square_edges = [Segment(Point(0, 0), Point(4, 0)),
    ...                 Segment(Point(0, 0), Point(0, 4)),
    ...                 Segment(Point(4, 0), Point(4, 4)),
    ...                 Segment(Point(0, 4), Point(4, 4))]
    >>> inner_square_edges = [Segment(Point(1, 1), Point(3, 1)),
    ...                       Segment(Point(1, 3), Point(1, 1)),
    ...                       Segment(Point(3, 1), Point(3, 3)),
    ...                       Segment(Point(1, 3), Point(3, 3))]
    >>> square_diagonals = [Segment(Point(0, 0), Point(2, 2)),
    ...                     Segment(Point(2, 2), Point(4, 0)),
    ...                     Segment(Point(2, 2), Point(4, 4)),
    ...                     Segment(Point(0, 4), Point(2, 2))]
    >>> (multisegment_in_multisegment(Multisegment(inner_square_edges),
    ...                               Multisegment(square_edges))
    ...  is Relation.DISJOINT)
    True
    >>> (multisegment_in_multisegment(Multisegment(square_diagonals),
    ...                               Multisegment(square_edges))
    ...  is Relation.TOUCH)
    True
    >>> (multisegment_in_multisegment(Multisegment(square_diagonals),
    ...                               Multisegment(inner_square_edges))
    ...  is Relation.CROSS)
    True
    >>> (multisegment_in_multisegment(Multisegment(inner_square_edges
    ...                                            + [square_edges[0]]),
    ...                               Multisegment(square_edges))
    ...  is Relation.OVERLAP)
    True
    >>> (multisegment_in_multisegment(Multisegment(square_edges
    ...                                            + inner_square_edges),
    ...                               Multisegment(square_edges))
    ...  is Relation.COMPOSITE)
    True
    >>> (multisegment_in_multisegment(Multisegment(square_edges),
    ...                               Multisegment(square_edges))
    ...  is Relation.EQUAL)
    True
    >>> (multisegment_in_multisegment(Multisegment(square_edges),
    ...                               Multisegment(square_edges
    ...                                            + inner_square_edges))
    ...  is Relation.COMPONENT)
    True
    """
    return _multisegment.relate_multisegment(
            right, left, _get_context() if context is None else context)


def point_in_contour(point: _Point, contour: _Contour,
                     *,
                     context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between point and contour.

    Time complexity:
        ``O(len(contour.vertices))``
    Memory complexity:
        ``O(1)``

    :param point: point to check for.
    :param contour: contour to check in.
    :param context: geometric context.
    :returns: relation between point and contour.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> square = Contour([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)])
    >>> point_in_contour(Point(0, 0), square) is Relation.COMPONENT
    True
    >>> point_in_contour(Point(1, 1), square) is Relation.DISJOINT
    True
    >>> point_in_contour(Point(2, 2), square) is Relation.COMPONENT
    True
    >>> point_in_contour(Point(3, 3), square) is Relation.DISJOINT
    True
    """
    return _contour.relate_point(
            contour, point, _get_context() if context is None else context)


def segment_in_contour(segment: _Segment, contour: _Contour,
                       *,
                       context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between segment and contour.

    Time complexity:
        ``O(len(contour.vertices))``
    Memory complexity:
        ``O(1)``

    :param segment: segment to check for.
    :param contour: contour to check in.
    :param context: geometric context.
    :returns: relation between segment and contour.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(3, 0), Point(3, 3), Point(0, 3)])
    >>> (segment_in_contour(Segment(Point(0, 0), Point(1, 0)), square)
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_contour(Segment(Point(0, 0), Point(3, 0)), square)
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_contour(Segment(Point(2, 0), Point(4, 0)), square)
    ...  is Relation.OVERLAP)
    True
    >>> (segment_in_contour(Segment(Point(4, 0), Point(5, 0)), square)
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_contour(Segment(Point(1, 0), Point(1, 2)), square)
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_contour(Segment(Point(0, 0), Point(1, 1)), square)
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_contour(Segment(Point(1, 1), Point(2, 2)), square)
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_contour(Segment(Point(2, 2), Point(4, 4)), square)
    ...  is Relation.CROSS)
    True
    """
    return _contour.relate_segment(
            contour, segment, _get_context() if context is None else context)


def multisegment_in_contour(multisegment: _Multisegment,
                            contour: _Contour,
                            *,
                            context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between multisegment and contour.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(left.vertices) + len(right.vertices)``.

    :param multisegment: multisegment to check for.
    :param contour: contour to check in.
    :param context: geometric context.
    :returns: relation between multisegment and contour.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> square_edges = [Segment(Point(0, 0), Point(4, 0)),
    ...                 Segment(Point(0, 0), Point(0, 4)),
    ...                 Segment(Point(4, 0), Point(4, 4)),
    ...                 Segment(Point(0, 4), Point(4, 4))]
    >>> inner_square_edges = [Segment(Point(1, 1), Point(3, 1)),
    ...                       Segment(Point(1, 3), Point(1, 1)),
    ...                       Segment(Point(3, 1), Point(3, 3)),
    ...                       Segment(Point(1, 3), Point(3, 3))]
    >>> square_diagonals = [Segment(Point(0, 0), Point(2, 2)),
    ...                     Segment(Point(2, 2), Point(4, 0)),
    ...                     Segment(Point(2, 2), Point(4, 4)),
    ...                     Segment(Point(0, 4), Point(2, 2))]
    >>> (multisegment_in_contour(Multisegment(inner_square_edges), square)
    ...  is Relation.DISJOINT)
    True
    >>> (multisegment_in_contour(Multisegment(square_diagonals), square)
    ...  is Relation.TOUCH)
    True
    >>> (multisegment_in_contour(Multisegment(square_diagonals), inner_square)
    ...  is Relation.CROSS)
    True
    >>> (multisegment_in_contour(
    ...      Multisegment(square_diagonals + [square_edges[0]]), square)
    ...  is Relation.OVERLAP)
    True
    >>> (multisegment_in_contour(Multisegment(square_diagonals + square_edges),
    ...                          square)
    ...  is Relation.COMPOSITE)
    True
    >>> (multisegment_in_contour(Multisegment(square_edges), square)
    ...  is Relation.EQUAL)
    True
    >>> (multisegment_in_contour(Multisegment(square_edges[1:]), square)
    ...  is Relation.COMPONENT)
    True
    """
    return _contour.relate_multisegment(
            contour, multisegment,
            _get_context() if context is None else context)


def contour_in_contour(left: _Contour, right: _Contour,
                       *,
                       context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between contours.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(left.vertices) + len(right.vertices)``.

    :param left: contour to check for.
    :param right: contour to check in.
    :param context: geometric context.
    :returns: relation between contours.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> triangle = Contour([Point(0, 0), Point(1, 0), Point(0, 1)])
    >>> square = Contour([Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)])
    >>> contour_in_contour(triangle, triangle) is Relation.EQUAL
    True
    >>> contour_in_contour(triangle, square) is Relation.OVERLAP
    True
    >>> contour_in_contour(square, triangle) is Relation.OVERLAP
    True
    >>> contour_in_contour(square, square) is Relation.EQUAL
    True
    """
    return _contour.relate_contour(
            right, left, _get_context() if context is None else context)


def point_in_region(point: _Point, region: _Region,
                    *,
                    context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between point and region.

    Based on ray casting algorithm.

    Time complexity:
        ``O(len(region.vertices))``
    Memory complexity:
        ``O(1)``
    Reference:
        https://en.wikipedia.org/wiki/Point_in_polygon#Ray_casting_algorithm

    :param point: point to check for.
    :param region: region to check in.
    :param context: geometric context.
    :returns: relation between point and region.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> square = Contour([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)])
    >>> point_in_region(Point(0, 0), square) is Relation.COMPONENT
    True
    >>> point_in_region(Point(1, 1), square) is Relation.WITHIN
    True
    >>> point_in_region(Point(2, 2), square) is Relation.COMPONENT
    True
    >>> point_in_region(Point(3, 3), square) is Relation.DISJOINT
    True
    """
    return _region.relate_point(region, point,
                                _get_context() if context is None else context)


def segment_in_region(segment: _Segment, region: _Region,
                      *,
                      context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between segment and region.

    Time complexity:
        ``O(len(region.vertices))``
    Memory complexity:
        ``O(1)``

    :param segment: segment to check for.
    :param region: region to check in.
    :param context: geometric context.
    :returns: relation between segment and region.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(3, 0), Point(3, 3), Point(0, 3)])
    >>> (segment_in_region(Segment(Point(0, 0), Point(1, 0)), square)
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_region(Segment(Point(0, 0), Point(3, 0)), square)
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_region(Segment(Point(2, 0), Point(4, 0)), square)
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_region(Segment(Point(4, 0), Point(5, 0)), square)
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_region(Segment(Point(1, 0), Point(1, 2)), square)
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_region(Segment(Point(0, 0), Point(1, 1)), square)
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_region(Segment(Point(1, 1), Point(2, 2)), square)
    ...  is Relation.WITHIN)
    True
    >>> (segment_in_region(Segment(Point(2, 2), Point(4, 4)), square)
    ...  is Relation.CROSS)
    True
    """
    return _region.relate_segment(
            region, segment, _get_context() if context is None else context)


def multisegment_in_region(multisegment: _Multisegment,
                           region: _Region,
                           *,
                           context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between multisegment and region.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment.segments)\
 + len(region.vertices)``.

    :param multisegment: multisegment to check for.
    :param region: region to check in.
    :param context: geometric context.
    :returns: relation between multisegment and region.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> square_edges = [Segment(Point(0, 0), Point(4, 0)),
    ...                 Segment(Point(0, 0), Point(0, 4)),
    ...                 Segment(Point(4, 0), Point(4, 4)),
    ...                 Segment(Point(0, 4), Point(4, 4))]
    >>> inner_square_edges = [Segment(Point(1, 1), Point(3, 1)),
    ...                       Segment(Point(1, 3), Point(1, 1)),
    ...                       Segment(Point(3, 1), Point(3, 3)),
    ...                       Segment(Point(1, 3), Point(3, 3))]
    >>> square_diagonals = [Segment(Point(0, 0), Point(2, 2)),
    ...                     Segment(Point(2, 2), Point(4, 0)),
    ...                     Segment(Point(2, 2), Point(4, 4)),
    ...                     Segment(Point(0, 4), Point(2, 2))]
    >>> (multisegment_in_region(Multisegment(square_edges), inner_square)
    ...  is Relation.DISJOINT)
    True
    >>> (multisegment_in_region(
    ...      Multisegment(square_edges + inner_square_edges), inner_square)
    ...  is Relation.TOUCH)
    True
    >>> (multisegment_in_region(Multisegment(square_diagonals), inner_square)
    ...  is Relation.CROSS)
    True
    >>> (multisegment_in_region(Multisegment(square_edges), square)
    ...  is Relation.COMPONENT)
    True
    >>> (multisegment_in_region(
    ...      Multisegment(square_edges + inner_square_edges), square)
    ...  is Relation.ENCLOSED)
    True
    >>> (multisegment_in_region(Multisegment(inner_square_edges), square)
    ...  is Relation.WITHIN)
    True
    """
    return _region.relate_multisegment(
            region, multisegment,
            _get_context() if context is None else context)


def contour_in_region(contour: _Contour, region: _Region,
                      *,
                      context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between contour and region.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour.vertices) + len(region.vertices)``.

    :param contour: contour to check for.
    :param region: region to check in.
    :param context: geometric context.
    :returns: relation between contour and region.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> triangle = Contour([Point(0, 0), Point(4, 0), Point(0, 4)])
    >>> contour_in_region(square, inner_square) is Relation.DISJOINT
    True
    >>> contour_in_region(square, triangle) is Relation.TOUCH
    True
    >>> contour_in_region(inner_square, triangle) is Relation.CROSS
    True
    >>> contour_in_region(square, square) is Relation.COMPONENT
    True
    >>> contour_in_region(triangle, square) is Relation.ENCLOSED
    True
    >>> contour_in_region(inner_square, square) is Relation.WITHIN
    True
    """
    return _region.relate_contour(
            region, contour, _get_context() if context is None else context)


def region_in_region(left: _Region, right: _Region,
                     *,
                     context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between regions.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(left.vertices) + len(right.vertices)``.

    :param left: region to check for.
    :param right: region to check in.
    :param context: geometric context.
    :returns: relation between regions.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
    >>> neighbour_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                             Point(4, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> triangle = Contour([Point(0, 0), Point(4, 0), Point(0, 4)])
    >>> (region_in_region(inner_square, neighbour_square)
    ...  is Relation.DISJOINT)
    True
    >>> region_in_region(square, neighbour_square) is Relation.TOUCH
    True
    >>> region_in_region(inner_square, triangle) is Relation.OVERLAP
    True
    >>> region_in_region(square, inner_square) is Relation.COVER
    True
    >>> region_in_region(square, triangle) is Relation.ENCLOSES
    True
    >>> region_in_region(square, square) is Relation.EQUAL
    True
    >>> region_in_region(triangle, square) is Relation.ENCLOSED
    True
    >>> region_in_region(inner_square, square) is Relation.WITHIN
    True
    """
    return _region.relate_region(
            right, left, _get_context() if context is None else context)


def point_in_multiregion(point: _Point,
                         multiregion: _Multiregion,
                         *,
                         context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between point and multiregion.

    Time complexity:
        ``O(sum(len(region.vertices) for region in multiregion))``
    Memory complexity:
        ``O(1)``

    :param point: point to check for.
    :param multiregion: multiregion to check in.
    :param context: geometric context.
    :returns: relation between point and multiregion.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> triangle = Contour([Point(0, 0), Point(2, 0), Point(0, 2)])
    >>> square = Contour([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)])
    >>> point_in_multiregion(Point(0, 0), [triangle]) is Relation.COMPONENT
    True
    >>> point_in_multiregion(Point(0, 0), [square]) is Relation.COMPONENT
    True
    >>> point_in_multiregion(Point(1, 1), [triangle]) is Relation.COMPONENT
    True
    >>> point_in_multiregion(Point(1, 1), [square]) is Relation.WITHIN
    True
    >>> point_in_multiregion(Point(2, 2), [triangle]) is Relation.DISJOINT
    True
    >>> point_in_multiregion(Point(2, 2), [square]) is Relation.COMPONENT
    True
    """
    return _multiregion.relate_point(
            multiregion, point, _get_context() if context is None else context)


def segment_in_multiregion(segment: _Segment,
                           multiregion: _Multiregion,
                           *,
                           context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between segment and multiregion.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count =\
 sum(len(region.vertices) for region in multiregion)``.

    :param segment: segment to check for.
    :param multiregion: multiregion to check in.
    :param context: geometric context.
    :returns: relation between segment and multiregion.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(3, 0), Point(3, 3), Point(0, 3)])
    >>> (segment_in_multiregion(Segment(Point(0, 0), Point(1, 0)), [])
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_multiregion(Segment(Point(0, 0), Point(1, 0)), [square])
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_multiregion(Segment(Point(0, 0), Point(3, 0)), [square])
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_multiregion(Segment(Point(2, 0), Point(4, 0)), [square])
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_multiregion(Segment(Point(4, 0), Point(5, 0)), [square])
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_multiregion(Segment(Point(1, 0), Point(1, 2)), [square])
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_multiregion(Segment(Point(0, 0), Point(1, 1)), [square])
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_multiregion(Segment(Point(1, 1), Point(2, 2)), [square])
    ...  is Relation.WITHIN)
    True
    >>> (segment_in_multiregion(Segment(Point(2, 2), Point(4, 4)), [square])
    ...  is Relation.CROSS)
    True
    """
    return _multiregion.relate_segment(
            multiregion, segment,
            _get_context() if context is None else context)


def multisegment_in_multiregion(multisegment: _Multisegment,
                                multiregion: _Multiregion,
                                *,
                                context: _Optional[_Context] = None
                                ) -> _Relation:
    """
    Finds relation between multisegment and multiregion.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment.segments)\
 + sum(len(region.vertices) for region in multiregion)``.

    :param multisegment: multisegment to check for.
    :param multiregion: multiregion to check in.
    :param context: geometric context.
    :returns: relation between multisegment and multiregion.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                          Point(4, 8)])
    >>> second_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                                Point(5, 7)])
    >>> first_square_edges = [Segment(Point(0, 0), Point(4, 0)),
    ...                       Segment(Point(0, 0), Point(0, 4)),
    ...                       Segment(Point(4, 0), Point(4, 4)),
    ...                       Segment(Point(0, 4), Point(4, 4))]
    >>> first_inner_square_edges = [Segment(Point(1, 1), Point(3, 1)),
    ...                             Segment(Point(1, 3), Point(1, 1)),
    ...                             Segment(Point(3, 1), Point(3, 3)),
    ...                             Segment(Point(1, 3), Point(3, 3))]
    >>> first_square_diagonals = [Segment(Point(0, 0), Point(2, 2)),
    ...                           Segment(Point(2, 2), Point(4, 0)),
    ...                           Segment(Point(2, 2), Point(4, 4)),
    ...                           Segment(Point(0, 4), Point(2, 2))]
    >>> (multisegment_in_multiregion(Multisegment(first_square_edges),
    ...                              [first_inner_square, second_inner_square])
    ...  is Relation.DISJOINT)
    True
    >>> (multisegment_in_multiregion(Multisegment(first_square_edges
    ...                                           + first_inner_square_edges),
    ...                              [first_inner_square, second_inner_square])
    ...  is Relation.TOUCH)
    True
    >>> (multisegment_in_multiregion(Multisegment(first_square_diagonals),
    ...                              [first_inner_square, second_inner_square])
    ...  is Relation.CROSS)
    True
    >>> (multisegment_in_multiregion(Multisegment(first_square_edges),
    ...                              [first_square, second_square])
    ...  is Relation.COMPONENT)
    True
    >>> (multisegment_in_multiregion(Multisegment(first_inner_square_edges),
    ...                              [first_square, second_square])
    ...  is Relation.WITHIN)
    True
    """
    return _multiregion.relate_multisegment(
            multiregion, multisegment,
            _get_context() if context is None else context)


def contour_in_multiregion(contour: _Contour,
                           multiregion: _Multiregion,
                           *,
                           context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between contour and multiregion.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour.vertices)\
 + sum(len(region.vertices) for region in multiregion)``.

    :param contour: contour to check for.
    :param multiregion: multiregion to check in.
    :param context: geometric context.
    :returns: relation between contour and multiregion.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> triangle = Contour([Point(0, 0), Point(4, 0), Point(0, 4)])
    >>> (contour_in_multiregion(first_square,
    ...                         [first_inner_square, second_inner_square])
    ...  is Relation.DISJOINT)
    True
    >>> (contour_in_multiregion(second_square, [first_square, third_square])
    ...  is Relation.TOUCH)
    True
    >>> (contour_in_multiregion(first_inner_square, [triangle, second_square])
    ...  is Relation.CROSS)
    True
    >>> (contour_in_multiregion(first_square, [first_square, third_square])
    ...  is Relation.COMPONENT)
    True
    >>> (contour_in_multiregion(triangle, [first_square, third_square])
    ...  is Relation.ENCLOSED)
    True
    >>> (contour_in_multiregion(first_inner_square,
    ...                         [first_square, third_square])
    ...  is Relation.WITHIN)
    True
    """
    return _multiregion.relate_contour(
            multiregion, contour,
            _get_context() if context is None else context)


def region_in_multiregion(region: _Region,
                          multiregion: _Multiregion,
                          *,
                          context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between region and multiregion.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(region.vertices)\
 + sum(len(region.vertices) for region in multiregion)``.

    :param region: region to check for.
    :param multiregion: multiregion to check in.
    :param context: geometric context.
    :returns: relation between region and multiregion.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> outer_square = Contour([Point(0, 0), Point(8, 0), Point(8, 8),
    ...                         Point(0, 8)])
    >>> triangle = Contour([Point(0, 0), Point(4, 0), Point(0, 4)])
    >>> (region_in_multiregion(third_square,
    ...                        [first_inner_square, second_inner_square])
    ...  is Relation.DISJOINT)
    True
    >>> (region_in_multiregion(second_square, [first_square, third_square])
    ...  is Relation.TOUCH)
    True
    >>> (region_in_multiregion(first_square,
    ...                        [first_inner_square, second_inner_square])
    ...  is Relation.OVERLAP)
    True
    >>> (region_in_multiregion(outer_square,
    ...                        [first_inner_square, second_inner_square])
    ...  is Relation.COVER)
    True
    >>> (region_in_multiregion(outer_square, [first_square, third_square])
    ...  is Relation.ENCLOSES)
    True
    >>> (region_in_multiregion(triangle, [first_square, third_square])
    ...  is Relation.ENCLOSED)
    True
    >>> (region_in_multiregion(first_inner_square,
    ...                        [first_square, third_square])
    ...  is Relation.WITHIN)
    True
    """
    return _multiregion.relate_region(
            multiregion, region,
            _get_context() if context is None else context)


def multiregion_in_multiregion(left: _Multiregion,
                               right: _Multiregion,
                               *,
                               context: _Optional[_Context] = None
                               ) -> _Relation:
    """
    Finds relation between multiregions.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = sum(len(region.vertices) for region in left)\
 + sum(len(region.vertices) for region in right)``.

    :param left: multiregion to check for.
    :param right: multiregion to check in.
    :param context: geometric context.
    :returns: relation between multiregions.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> (multiregion_in_multiregion([first_inner_square, third_inner_square],
    ...                             [second_square, fourth_square])
    ...  is Relation.DISJOINT)
    True
    >>> (multiregion_in_multiregion([first_square, third_square],
    ...                             [second_square, fourth_square])
    ...  is Relation.TOUCH)
    True
    >>> (multiregion_in_multiregion([first_square, third_inner_square],
    ...                             [first_inner_square, third_square])
    ...  is Relation.OVERLAP)
    True
    >>> (multiregion_in_multiregion([first_square, third_square],
    ...                             [first_inner_square, third_inner_square])
    ...  is Relation.COVER)
    True
    >>> (multiregion_in_multiregion([first_square, third_square],
    ...                             [first_square, third_inner_square])
    ...  is Relation.ENCLOSES)
    True
    >>> (multiregion_in_multiregion(
    ...      [first_inner_square, second_inner_square, third_inner_square],
    ...      [first_inner_square, second_inner_square])
    ...  is Relation.COMPOSITE)
    True
    >>> (multiregion_in_multiregion([first_square, third_square],
    ...                             [first_square, third_square])
    ...  is Relation.EQUAL)
    True
    >>> (multiregion_in_multiregion(
    ...      [first_inner_square, second_inner_square],
    ...      [first_inner_square, second_inner_square, third_inner_square])
    ...  is Relation.COMPONENT)
    True
    >>> (multiregion_in_multiregion([first_square, third_inner_square],
    ...                             [first_square, third_square])
    ...  is Relation.ENCLOSED)
    True
    >>> (multiregion_in_multiregion([first_inner_square, third_inner_square],
    ...                             [first_square, third_square])
    ...  is Relation.WITHIN)
    True
    """
    return _multiregion.relate_multiregion(
            right, left, _get_context() if context is None else context)


def point_in_polygon(point: _Point, polygon: _Polygon,
                     *,
                     context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between point and polygon.

    Time complexity:
        ``O(vertices_count)``
    Memory complexity:
        ``O(1)``

    where ``vertices_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``.

    :param point: point to check for.
    :param polygon: polygon to check in.
    :param context: geometric context.
    :returns: relation between point and polygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> outer_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> (point_in_polygon(Point(0, 0), Polygon(inner_square, []))
    ...  is Relation.DISJOINT)
    True
    >>> (point_in_polygon(Point(0, 0), Polygon(outer_square, []))
    ...  is Relation.COMPONENT)
    True
    >>> (point_in_polygon(Point(1, 1), Polygon(inner_square, []))
    ...  is Relation.COMPONENT)
    True
    >>> (point_in_polygon(Point(1, 1), Polygon(outer_square, []))
    ...  is Relation.WITHIN)
    True
    >>> (point_in_polygon(Point(2, 2), Polygon(outer_square, []))
    ...  is Relation.WITHIN)
    True
    >>> (point_in_polygon(Point(2, 2), Polygon(outer_square, [inner_square]))
    ...  is Relation.DISJOINT)
    True
    """
    return _polygon.relate_point(
            polygon, point, _get_context() if context is None else context)


def segment_in_polygon(segment: _Segment, polygon: _Polygon,
                       *,
                       context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between segment and polygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``.

    :param segment: segment to check for.
    :param polygon: polygon to check in.
    :param context: geometric context.
    :returns: relation between segment and polygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> outer_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> segment_in_polygon(Segment(Point(0, 0), Point(1, 0)),
    ...                    Polygon(outer_square, [])) is Relation.COMPONENT
    True
    >>> (segment_in_polygon(Segment(Point(0, 0), Point(1, 0)),
    ...                     Polygon(outer_square, [inner_square]))
    ...  is Relation.COMPONENT)
    True
    >>> segment_in_polygon(Segment(Point(0, 0), Point(2, 2)),
    ...                    Polygon(outer_square, [])) is Relation.ENCLOSED
    True
    >>> (segment_in_polygon(Segment(Point(0, 0), Point(2, 2)),
    ...                     Polygon(outer_square, [inner_square]))
    ...  is Relation.CROSS)
    True
    >>> segment_in_polygon(Segment(Point(1, 1), Point(3, 3)),
    ...                    Polygon(outer_square, [])) is Relation.WITHIN
    True
    >>> (segment_in_polygon(Segment(Point(1, 1), Point(3, 3)),
    ...                     Polygon(outer_square, [inner_square]))
    ...  is Relation.TOUCH)
    True
    >>> segment_in_polygon(Segment(Point(0, 0), Point(4, 4)),
    ...                    Polygon(outer_square, [])) is Relation.ENCLOSED
    True
    >>> (segment_in_polygon(Segment(Point(0, 0), Point(4, 4)),
    ...                     Polygon(outer_square, [inner_square]))
    ...  is Relation.CROSS)
    True
    """
    return _polygon.relate_segment(
            polygon, segment, _get_context() if context is None else context)


def multisegment_in_polygon(multisegment: _Multisegment,
                            polygon: _Polygon,
                            *,
                            context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between multisegment and polygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment.segments)\
 + len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``.

    :param multisegment: multisegment to check for.
    :param polygon: polygon to check in.
    :param context: geometric context.
    :returns: relation between multisegment and polygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> square_edges = [Segment(Point(0, 0), Point(4, 0)),
    ...                 Segment(Point(0, 0), Point(0, 4)),
    ...                 Segment(Point(4, 0), Point(4, 4)),
    ...                 Segment(Point(0, 4), Point(4, 4))]
    >>> inner_square_edges = [Segment(Point(1, 1), Point(3, 1)),
    ...                       Segment(Point(1, 3), Point(1, 1)),
    ...                       Segment(Point(3, 1), Point(3, 3)),
    ...                       Segment(Point(1, 3), Point(3, 3))]
    >>> square_diagonals = [Segment(Point(0, 0), Point(2, 2)),
    ...                     Segment(Point(2, 2), Point(4, 0)),
    ...                     Segment(Point(2, 2), Point(4, 4)),
    ...                     Segment(Point(0, 4), Point(2, 2))]
    >>> (multisegment_in_polygon(Multisegment(square_edges),
    ...                          Polygon(inner_square, []))
    ...  is Relation.DISJOINT)
    True
    >>> (multisegment_in_polygon(Multisegment(square_edges
    ...                                       + inner_square_edges),
    ...                          Polygon(inner_square, []))
    ...  is Relation.TOUCH)
    True
    >>> (multisegment_in_polygon(Multisegment(square_diagonals),
    ...                          Polygon(inner_square, []))
    ...  is Relation.CROSS)
    True
    >>> (multisegment_in_polygon(Multisegment(square_edges),
    ...                          Polygon(square, []))
    ...  is Relation.COMPONENT)
    True
    >>> (multisegment_in_polygon(Multisegment(square_edges
    ...                                       + inner_square_edges),
    ...                          Polygon(square, []))
    ...  is Relation.ENCLOSED)
    True
    >>> (multisegment_in_polygon(Multisegment(inner_square_edges),
    ...                          Polygon(square, []))
    ...  is Relation.WITHIN)
    True
    """
    return _polygon.relate_multisegment(
            polygon, multisegment,
            _get_context() if context is None else context)


def contour_in_polygon(contour: _Contour, polygon: _Polygon,
                       *,
                       context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between contour and polygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour.vertices)\
 + len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``.

    :param contour: contour to check for.
    :param polygon: polygon to check in.
    :param context: geometric context.
    :returns: relation between contour and polygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> triangle = Contour([Point(0, 0), Point(4, 0), Point(0, 4)])
    >>> (contour_in_polygon(square, Polygon(inner_square, []))
    ...  is Relation.DISJOINT)
    True
    >>> contour_in_polygon(square, Polygon(triangle, [])) is Relation.TOUCH
    True
    >>> (contour_in_polygon(inner_square, Polygon(triangle, []))
    ...  is Relation.CROSS)
    True
    >>> contour_in_polygon(square, Polygon(square, [])) is Relation.COMPONENT
    True
    >>> contour_in_polygon(triangle, Polygon(square, [])) is Relation.ENCLOSED
    True
    >>> (contour_in_polygon(inner_square, Polygon(square, []))
    ...  is Relation.WITHIN)
    True
    """
    return _polygon.relate_contour(
            polygon, contour, _get_context() if context is None else context)


def region_in_polygon(region: _Region, polygon: _Polygon,
                      *,
                      context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between region and polygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(region.vertices)\
 + len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``.

    :param region: region to check for.
    :param polygon: polygon to check in.
    :param context: geometric context.
    :returns: relation between region and polygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> square = Contour([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
    >>> neighbour_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                             Point(4, 4)])
    >>> inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                         Point(1, 3)])
    >>> triangle = Contour([Point(0, 0), Point(4, 0), Point(0, 4)])
    >>> (region_in_polygon(inner_square, Polygon(neighbour_square, []))
    ...  is Relation.DISJOINT)
    True
    >>> (region_in_polygon(square, Polygon(neighbour_square, []))
    ...  is Relation.TOUCH)
    True
    >>> (region_in_polygon(inner_square, Polygon(triangle, []))
    ...  is Relation.OVERLAP)
    True
    >>> region_in_polygon(square, Polygon(inner_square, [])) is Relation.COVER
    True
    >>> region_in_polygon(square, Polygon(triangle, [])) is Relation.ENCLOSES
    True
    >>> region_in_polygon(square, Polygon(square, [])) is Relation.EQUAL
    True
    >>> region_in_polygon(triangle, Polygon(square, [])) is Relation.ENCLOSED
    True
    >>> region_in_polygon(inner_square, Polygon(square, [])) is Relation.WITHIN
    True
    """
    return _polygon.relate_region(
            polygon, region, _get_context() if context is None else context)


def multiregion_in_polygon(multiregion: _Multiregion,
                           polygon: _Polygon,
                           *,
                           context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between multiregion and polygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count =\
 sum(len(region.vertices) for region in multiregion)\
 + len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``.

    :param multiregion: multiregion to check for.
    :param polygon: polygon to check in.
    :param context: geometric context.
    :returns: relation between multiregion and polygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> outer_square = Contour([Point(0, 0), Point(8, 0), Point(8, 8),
    ...                         Point(0, 8)])
    >>> (multiregion_in_polygon([first_square, third_square],
    ...                         Polygon(second_inner_square, []))
    ...  is Relation.DISJOINT)
    True
    >>> (multiregion_in_polygon([first_inner_square, second_inner_square],
    ...                         Polygon(first_square, [first_inner_square]))
    ...  is Relation.TOUCH)
    True
    >>> (multiregion_in_polygon([first_inner_square, second_inner_square],
    ...                         Polygon(first_square, []))
    ...  is Relation.OVERLAP)
    True
    >>> (multiregion_in_polygon([first_square, second_inner_square],
    ...                         Polygon(first_inner_square, []))
    ...  is Relation.COVER)
    True
    >>> (multiregion_in_polygon([first_square, second_inner_square],
    ...                         Polygon(first_square, [first_inner_square]))
    ...  is Relation.ENCLOSES)
    True
    >>> (multiregion_in_polygon([first_square, second_inner_square],
    ...                         Polygon(first_square, []))
    ...  is Relation.COMPOSITE)
    True
    >>> (multiregion_in_polygon([first_square, second_inner_square],
    ...                         Polygon(outer_square, []))
    ...  is Relation.ENCLOSED)
    True
    >>> (multiregion_in_polygon([first_inner_square, second_inner_square],
    ...                         Polygon(outer_square, []))
    ...  is Relation.WITHIN)
    True
    """
    return _polygon.relate_multiregion(
            polygon, multiregion,
            _get_context() if context is None else context)


def polygon_in_polygon(left: _Polygon, right: _Polygon,
                       *,
                       context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between polygons.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(left.border.vertices)\
 + sum(len(hole.vertices) for hole in left.holes) + len(right.border.vertices)\
 + sum(len(hole.vertices) for hole in right.holes)``.

    :param left: polygon to check for.
    :param right: polygon to check in.
    :param context: geometric context.
    :returns: relation between polygons.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> outer_square = Contour([Point(0, 0), Point(7, 0), Point(7, 7),
    ...                         Point(0, 7)])
    >>> inner_square = Contour([Point(1, 1), Point(6, 1), Point(6, 6),
    ...                         Point(1, 6)])
    >>> innermore_square = Contour([Point(2, 2), Point(5, 2), Point(5, 5),
    ...                             Point(2, 5)])
    >>> innermost_square = Contour([Point(3, 3), Point(4, 3), Point(4, 4),
    ...                             Point(3, 4)])
    >>> (polygon_in_polygon(Polygon(outer_square, [inner_square]),
    ...                     Polygon(innermore_square, []))
    ...  is polygon_in_polygon(Polygon(innermore_square, []),
    ...                        Polygon(outer_square, [inner_square]))
    ...  is polygon_in_polygon(Polygon(outer_square, [inner_square]),
    ...                        Polygon(innermore_square, [innermost_square]))
    ...  is polygon_in_polygon(Polygon(innermore_square, [innermost_square]),
    ...                        Polygon(outer_square, [inner_square]))
    ...  is Relation.DISJOINT)
    True
    >>> (polygon_in_polygon(Polygon(inner_square, []),
    ...                     Polygon(outer_square, [inner_square]))
    ...  is polygon_in_polygon(Polygon(outer_square, [inner_square]),
    ...                        Polygon(inner_square, []))
    ...  is polygon_in_polygon(Polygon(outer_square, [inner_square]),
    ...                        Polygon(inner_square, [innermore_square]))
    ...  is polygon_in_polygon(Polygon(inner_square, [innermore_square]),
    ...                        Polygon(outer_square, [inner_square]))
    ...  is Relation.TOUCH)
    True
    >>> (polygon_in_polygon(Polygon(inner_square, []),
    ...                     Polygon(outer_square, [innermore_square]))
    ...  is polygon_in_polygon(Polygon(outer_square, [innermore_square]),
    ...                        Polygon(inner_square, []))
    ...  is polygon_in_polygon(Polygon(outer_square, [innermore_square]),
    ...                        Polygon(inner_square, [innermost_square]))
    ...  is polygon_in_polygon(Polygon(inner_square, [innermost_square]),
    ...                        Polygon(outer_square, [innermore_square]))
    ...  is Relation.OVERLAP)
    True
    >>> (polygon_in_polygon(Polygon(outer_square, []),
    ...                     Polygon(inner_square, []))
    ...  is polygon_in_polygon(Polygon(outer_square, [innermost_square]),
    ...                        Polygon(inner_square, [innermore_square]))
    ...  is Relation.COVER)
    True
    >>> (polygon_in_polygon(Polygon(outer_square, []),
    ...                     Polygon(outer_square, [inner_square]))
    ...  is polygon_in_polygon(Polygon(outer_square, [innermore_square]),
    ...                        Polygon(outer_square, [inner_square]))
    ...  is polygon_in_polygon(Polygon(outer_square, [innermore_square]),
    ...                        Polygon(inner_square, [innermore_square]))
    ...  is Relation.ENCLOSES)
    True
    >>> (polygon_in_polygon(Polygon(outer_square, []),
    ...                     Polygon(outer_square, []))
    ...  is polygon_in_polygon(Polygon(outer_square, [inner_square]),
    ...                        Polygon(outer_square, [inner_square]))
    ...  is Relation.EQUAL)
    True
    >>> (polygon_in_polygon(Polygon(outer_square, [inner_square]),
    ...                     Polygon(outer_square, []))
    ...  is polygon_in_polygon(Polygon(outer_square, [inner_square]),
    ...                        Polygon(outer_square, [innermore_square]))
    ...  is polygon_in_polygon(Polygon(inner_square, [innermore_square]),
    ...                        Polygon(outer_square, [innermore_square]))
    ...  is Relation.ENCLOSED)
    True
    >>> (polygon_in_polygon(Polygon(inner_square, []),
    ...                     Polygon(outer_square, []))
    ...  is polygon_in_polygon(Polygon(inner_square, [innermore_square]),
    ...                        Polygon(outer_square, [innermost_square]))
    ...  is Relation.WITHIN)
    True
    """
    return _polygon.relate_polygon(
            right, left, _get_context() if context is None else context)


def point_in_multipolygon(point: _Point,
                          multipolygon: _Multipolygon,
                          *,
                          context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between point and multipolygon.

    Time complexity:
        ``O(sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes))\
 for polygon in multipolygon.polygons))``
    Memory complexity:
        ``O(1)``

    :param point: point to check for.
    :param multipolygon: multipolygon to check in.
    :param context: geometric context.
    :returns: relation between point and multipolygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                          Point(4, 8)])
    >>> (point_in_multipolygon(Point(6, 2),
    ...                        Multipolygon([Polygon(first_square, []),
    ...                                      Polygon(second_square, [])]))
    ...  is Relation.DISJOINT)
    True
    >>> (point_in_multipolygon(Point(4, 4),
    ...                        Multipolygon([Polygon(first_square, []),
    ...                                      Polygon(second_square, [])]))
    ...  is Relation.COMPONENT)
    True
    >>> (point_in_multipolygon(Point(2, 2),
    ...                        Multipolygon([Polygon(first_square, []),
    ...                                      Polygon(second_square, [])]))
    ...  is Relation.WITHIN)
    True
    """
    return _multipolygon.relate_point(
            multipolygon, point,
            _get_context() if context is None else context)


def segment_in_multipolygon(segment: _Segment,
                            multipolygon: _Multipolygon,
                            *,
                            context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between segment and multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``.

    :param segment: segment to check for.
    :param multipolygon: multipolygon to check in.
    :param context: geometric context.
    :returns: relation between segment and multipolygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                          Point(4, 8)])
    >>> (segment_in_multipolygon(Segment(Point(2, 5), Point(2, 9)),
    ...                          Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(second_square, [])]))
    ...  is Relation.DISJOINT)
    True
    >>> (segment_in_multipolygon(Segment(Point(2, 4), Point(2, 8)),
    ...                          Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(second_square, [])]))
    ...  is Relation.TOUCH)
    True
    >>> (segment_in_multipolygon(Segment(Point(2, 2), Point(2, 6)),
    ...                          Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(second_square, [])]))
    ...  is Relation.CROSS)
    True
    >>> (segment_in_multipolygon(Segment(Point(2, 4), Point(6, 4)),
    ...                          Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(second_square, [])]))
    ...  is Relation.COMPONENT)
    True
    >>> (segment_in_multipolygon(Segment(Point(3, 3), Point(5, 5)),
    ...                          Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(second_square, [])]))
    ...  is Relation.ENCLOSED)
    True
    >>> (segment_in_multipolygon(Segment(Point(1, 1), Point(3, 3)),
    ...                          Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(second_square, [])]))
    ...  is Relation.WITHIN)
    True
    """
    return _multipolygon.relate_segment(
            multipolygon, segment,
            _get_context() if context is None else context)


def multisegment_in_multipolygon(multisegment: _Multisegment,
                                 multipolygon: _Multipolygon,
                                 *,
                                 context: _Optional[_Context] = None
                                 ) -> _Relation:
    """
    Finds relation between multisegment and multipolygon.

    Time complexity:
        ``O(segments_count * log segments_count)``
    Memory complexity:
        ``O(segments_count)``

    where ``segments_count = len(multisegment.segments)\
 + multipolygon_segments_count``,
    ``multipolygon_segments_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``.

    :param multisegment: multisegment to check for.
    :param multipolygon: multipolygon to check in.
    :param context: geometric context.
    :returns: relation between multisegment and multipolygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Multisegment = context.multisegment_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Segment = context.segment_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                          Point(4, 8)])
    >>> second_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                                Point(5, 7)])
    >>> first_square_edges = [Segment(Point(0, 0), Point(4, 0)),
    ...                       Segment(Point(0, 0), Point(0, 4)),
    ...                       Segment(Point(4, 0), Point(4, 4)),
    ...                       Segment(Point(0, 4), Point(4, 4))]
    >>> first_inner_square_edges = [Segment(Point(1, 1), Point(3, 1)),
    ...                             Segment(Point(1, 3), Point(1, 1)),
    ...                             Segment(Point(3, 1), Point(3, 3)),
    ...                             Segment(Point(1, 3), Point(3, 3))]
    >>> first_square_diagonals = [Segment(Point(0, 0), Point(2, 2)),
    ...                           Segment(Point(2, 2), Point(4, 0)),
    ...                           Segment(Point(2, 2), Point(4, 4)),
    ...                           Segment(Point(0, 4), Point(2, 2))]
    >>> (multisegment_in_multipolygon(
    ...      Multisegment(first_square_edges),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, [])]))
    ...  is Relation.DISJOINT)
    True
    >>> (multisegment_in_multipolygon(
    ...      Multisegment(first_square_edges + first_inner_square_edges),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, [])]))
    ...  is Relation.TOUCH)
    True
    >>> (multisegment_in_multipolygon(
    ...      Multisegment(first_square_diagonals),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, [])]))
    ...  is Relation.CROSS)
    True
    >>> (multisegment_in_multipolygon(
    ...      Multisegment(first_square_edges),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(second_square, [])]))
    ...  is Relation.COMPONENT)
    True
    >>> (multisegment_in_multipolygon(
    ...      Multisegment(first_inner_square_edges),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(second_square, [])]))
    ...  is Relation.WITHIN)
    True
    """
    return _multipolygon.relate_multisegment(
            multipolygon, multisegment,
            _get_context() if context is None else context)


def contour_in_multipolygon(contour: _Contour,
                            multipolygon: _Multipolygon,
                            *,
                            context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between contour and multipolygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(contour.vertices)\
 + multipolygon_vertices_count``,
    ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``.

    :param contour: contour to check for.
    :param multipolygon: multipolygon to check in.
    :param context: geometric context.
    :returns: relation between contour and multipolygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> triangle = Contour([Point(0, 0), Point(4, 0), Point(0, 4)])
    >>> (contour_in_multipolygon(
    ...      first_square, Multipolygon([Polygon(first_inner_square, []),
    ...                                  Polygon(second_inner_square, [])]))
    ...  is Relation.DISJOINT)
    True
    >>> (contour_in_multipolygon(
    ...      second_square, Multipolygon([Polygon(first_square, []),
    ...                                   Polygon(third_square, [])]))
    ...  is Relation.TOUCH)
    True
    >>> (contour_in_multipolygon(
    ...      first_inner_square, Multipolygon([Polygon(triangle, []),
    ...                                        Polygon(second_square, [])]))
    ...  is Relation.CROSS)
    True
    >>> (contour_in_multipolygon(
    ...      first_square, Multipolygon([Polygon(first_square, []),
    ...                                  Polygon(third_square, [])]))
    ...  is Relation.COMPONENT)
    True
    >>> (contour_in_multipolygon(
    ...      triangle, Multipolygon([Polygon(first_square, []),
    ...                              Polygon(third_square, [])]))
    ...  is Relation.ENCLOSED)
    True
    >>> (contour_in_multipolygon(
    ...      first_inner_square, Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(third_square, [])]))
    ...  is Relation.WITHIN)
    True
    """
    return _multipolygon.relate_contour(
            multipolygon, contour,
            _get_context() if context is None else context)


def region_in_multipolygon(region: _Region,
                           multipolygon: _Multipolygon,
                           *,
                           context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between region and multipolygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = len(region.vertices)\
 + multipolygon_vertices_count``,
    ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``.

    :param region: region to check for.
    :param multipolygon: multipolygon to check in.
    :param context: geometric context.
    :returns: relation between region and multipolygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> outer_square = Contour([Point(0, 0), Point(8, 0), Point(8, 8),
    ...                         Point(0, 8)])
    >>> triangle = Contour([Point(0, 0), Point(4, 0), Point(0, 4)])
    >>> (region_in_multipolygon(
    ...      third_square, Multipolygon([Polygon(first_inner_square, []),
    ...                                  Polygon(second_inner_square, [])]))
    ...  is Relation.DISJOINT)
    True
    >>> (region_in_multipolygon(
    ...      second_square, Multipolygon([Polygon(first_square, []),
    ...                                   Polygon(third_square, [])]))
    ...  is Relation.TOUCH)
    True
    >>> (region_in_multipolygon(
    ...      first_square, Multipolygon([Polygon(first_inner_square, []),
    ...                                  Polygon(second_inner_square, [])]))
    ...  is Relation.OVERLAP)
    True
    >>> (region_in_multipolygon(
    ...      outer_square, Multipolygon([Polygon(first_inner_square, []),
    ...                                  Polygon(second_inner_square, [])]))
    ...  is Relation.COVER)
    True
    >>> (region_in_multipolygon(
    ...      outer_square, Multipolygon([Polygon(first_square, []),
    ...                                  Polygon(third_square, [])]))
    ...  is Relation.ENCLOSES)
    True
    >>> (region_in_multipolygon(
    ...      triangle, Multipolygon([Polygon(first_square, []),
    ...                              Polygon(third_square, [])]))
    ...  is Relation.ENCLOSED)
    True
    >>> (region_in_multipolygon(
    ...      first_inner_square, Multipolygon([Polygon(first_square, []),
    ...                                        Polygon(third_square, [])]))
    ...  is Relation.WITHIN)
    True
    """
    return _multipolygon.relate_region(
            multipolygon, region,
            _get_context() if context is None else context)


def multiregion_in_multipolygon(multiregion: _Multiregion,
                                multipolygon: _Multipolygon,
                                *,
                                context: _Optional[_Context] = None
                                ) -> _Relation:
    """
    Finds relation between multiregion and multipolygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = multiregion_vertices_count\
 + multipolygon_vertices_count``,
    ``multiregion_vertices_count =\
 sum(len(region.vertices) for region in multiregion)``,
    ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``.

    :param multiregion: multiregion to check for.
    :param multipolygon: multipolygon to check in.
    :param context: geometric context.
    :returns: relation between multiregion and multipolygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> fourth_inner_square = Contour([Point(1, 5), Point(3, 5), Point(3, 7),
    ...                                Point(1, 7)])
    >>> (multiregion_in_multipolygon(
    ...      [first_square, third_square],
    ...      Multipolygon([Polygon(second_inner_square, []),
    ...                    Polygon(fourth_inner_square, [])]))
    ...  is multiregion_in_multipolygon(
    ...          [first_inner_square, third_inner_square],
    ...          Multipolygon([Polygon(second_square, [second_inner_square]),
    ...                        Polygon(fourth_square, [fourth_inner_square])]))
    ...  is Relation.DISJOINT)
    True
    >>> (multiregion_in_multipolygon(
    ...      [first_square, third_square],
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  is multiregion_in_multipolygon(
    ...          [first_inner_square, third_inner_square],
    ...          Multipolygon([Polygon(first_square, [first_inner_square]),
    ...                        Polygon(third_square, [third_inner_square])]))
    ...  is Relation.TOUCH)
    True
    >>> (multiregion_in_multipolygon(
    ...      [first_square, third_inner_square],
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is Relation.OVERLAP)
    True
    >>> (multiregion_in_multipolygon(
    ...      [first_square, third_square],
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is Relation.COVER)
    True
    >>> (multiregion_in_multipolygon(
    ...      [first_square, third_inner_square],
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is multiregion_in_multipolygon(
    ...          [first_square, third_square],
    ...          Multipolygon([Polygon(first_square, [first_inner_square]),
    ...                        Polygon(third_square, [third_inner_square])]))
    ...  is Relation.ENCLOSES)
    True
    >>> (multiregion_in_multipolygon(
    ...      [first_inner_square, second_inner_square, third_inner_square],
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is Relation.COMPOSITE)
    True
    >>> (multiregion_in_multipolygon(
    ...      [first_square, third_square],
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is Relation.EQUAL)
    True
    >>> (multiregion_in_multipolygon(
    ...      [first_inner_square, second_inner_square],
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is Relation.COMPONENT)
    True
    >>> (multiregion_in_multipolygon(
    ...      [first_inner_square, third_inner_square],
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is Relation.ENCLOSED)
    True
    >>> (multiregion_in_multipolygon(
    ...      [first_inner_square, third_inner_square],
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is Relation.WITHIN)
    True
    """
    return _multipolygon.relate_multiregion(
            multipolygon, multiregion,
            _get_context() if context is None else context)


def polygon_in_multipolygon(polygon: _Polygon,
                            multipolygon: _Multipolygon,
                            *,
                            context: _Optional[_Context] = None) -> _Relation:
    """
    Finds relation between polygon and multipolygon.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = polygon_vertices_count\
 + multipolygon_vertices_count``,
    ``polygon_vertices_count = len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)``,
    ``multipolygon_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in multipolygon.polygons)``.

    :param polygon: polygon to check for.
    :param multipolygon: multipolygon to check in.
    :param context: geometric context.
    :returns: relation between polygon and multipolygon.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> outer_square = Contour([Point(0, 0), Point(7, 0), Point(7, 7),
    ...                         Point(0, 7)])
    >>> inner_square = Contour([Point(1, 1), Point(6, 1), Point(6, 6),
    ...                         Point(1, 6)])
    >>> innermore_square = Contour([Point(2, 2), Point(5, 2), Point(5, 5),
    ...                             Point(2, 5)])
    >>> innermost_square = Contour([Point(3, 3), Point(4, 3), Point(4, 4),
    ...                             Point(3, 4)])
    >>> (polygon_in_multipolygon(Polygon(outer_square, [inner_square]),
    ...                          Multipolygon([Polygon(innermore_square, [])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(innermore_square, []),
    ...                 Multipolygon([Polygon(outer_square, [inner_square])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(outer_square, [inner_square]),
    ...                 Multipolygon([Polygon(innermore_square,
    ...                                       [innermost_square])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(innermore_square, [innermost_square]),
    ...                 Multipolygon([Polygon(outer_square, [inner_square])]))
    ...  is Relation.DISJOINT)
    True
    >>> (polygon_in_multipolygon(
    ...         Polygon(inner_square, []),
    ...         Multipolygon([Polygon(outer_square, [inner_square])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(outer_square, [inner_square]),
    ...                 Multipolygon([Polygon(inner_square, [])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(outer_square, [inner_square]),
    ...                 Multipolygon([Polygon(inner_square,
    ...                                       [innermore_square])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(inner_square, [innermore_square]),
    ...                 Multipolygon([Polygon(outer_square, [inner_square])]))
    ...  is Relation.TOUCH)
    True
    >>> (polygon_in_multipolygon(
    ...         Polygon(inner_square, []),
    ...         Multipolygon([Polygon(outer_square, [innermore_square])]))
    ...  is polygon_in_multipolygon(Polygon(outer_square, [innermore_square]),
    ...                             Multipolygon([Polygon(inner_square, [])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(outer_square, [innermore_square]),
    ...                 Multipolygon([Polygon(inner_square,
    ...                                       [innermost_square])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(inner_square, [innermost_square]),
    ...                 Multipolygon([Polygon(outer_square,
    ...                                       [innermore_square])]))
    ...  is Relation.OVERLAP)
    True
    >>> (polygon_in_multipolygon(Polygon(outer_square, []),
    ...                          Multipolygon([Polygon(inner_square, [])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(outer_square, [innermost_square]),
    ...                 Multipolygon([Polygon(inner_square,
    ...                                       [innermore_square])]))
    ...  is Relation.COVER)
    True
    >>> (polygon_in_multipolygon(
    ...         Polygon(outer_square, []),
    ...         Multipolygon([Polygon(outer_square, [inner_square])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(outer_square, [innermore_square]),
    ...                 Multipolygon([Polygon(outer_square, [inner_square])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(outer_square, [innermore_square]),
    ...                 Multipolygon([Polygon(inner_square,
    ...                                       [innermore_square])]))
    ...  is Relation.ENCLOSES)
    True
    >>> (polygon_in_multipolygon(Polygon(outer_square, []),
    ...                          Multipolygon([Polygon(outer_square, [])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(outer_square, [inner_square]),
    ...                 Multipolygon([Polygon(outer_square, [inner_square])]))
    ...  is Relation.EQUAL)
    True
    >>> (polygon_in_multipolygon(Polygon(innermore_square, []),
    ...                          Multipolygon([Polygon(outer_square,
    ...                                                [inner_square]),
    ...                                        Polygon(innermore_square, [])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(innermore_square, [innermost_square]),
    ...                 Multipolygon([Polygon(outer_square, [inner_square]),
    ...                               Polygon(innermore_square,
    ...                                       [innermost_square])]))
    ...  is Relation.COMPONENT)
    True
    >>> (polygon_in_multipolygon(Polygon(outer_square, [inner_square]),
    ...                          Multipolygon([Polygon(outer_square, [])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(outer_square, [inner_square]),
    ...                 Multipolygon([Polygon(outer_square,
    ...                                       [innermore_square])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(inner_square, [innermore_square]),
    ...                 Multipolygon([Polygon(outer_square,
    ...                                       [innermore_square])]))
    ...  is Relation.ENCLOSED)
    True
    >>> (polygon_in_multipolygon(Polygon(inner_square, []),
    ...                          Multipolygon([Polygon(outer_square, [])]))
    ...  is polygon_in_multipolygon(
    ...                 Polygon(inner_square, [innermore_square]),
    ...                 Multipolygon([Polygon(outer_square,
    ...                                       [innermost_square])]))
    ...  is Relation.WITHIN)
    True
    """
    return _multipolygon.relate_polygon(
            multipolygon, polygon,
            _get_context() if context is None else context)


def multipolygon_in_multipolygon(left: _Multipolygon,
                                 right: _Multipolygon,
                                 *,
                                 context: _Optional[_Context] = None
                                 ) -> _Relation:
    """
    Finds relation between multipolygons.

    Time complexity:
        ``O(vertices_count * log vertices_count)``
    Memory complexity:
        ``O(vertices_count)``

    where ``vertices_count = left_vertices_count + right_vertices_count``,
    ``left_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in left.polygons)``,
    ``right_vertices_count = sum(len(polygon.border.vertices)\
 + sum(len(hole.vertices) for hole in polygon.holes)\
 for polygon in right.polygons)``.

    :param left: multipolygon to check for.
    :param right: multipolygon to check in.
    :param context: geometric context.
    :returns: relation between multipolygons.

    >>> from ground.base import Relation, get_context
    >>> context = get_context()
    >>> Contour = context.contour_cls
    >>> Multipolygon = context.multipolygon_cls
    >>> Point = context.point_cls
    >>> Polygon = context.polygon_cls
    >>> first_square = Contour([Point(0, 0), Point(4, 0), Point(4, 4),
    ...                         Point(0, 4)])
    >>> second_square = Contour([Point(4, 0), Point(8, 0), Point(8, 4),
    ...                          Point(4, 4)])
    >>> third_square = Contour([Point(4, 4), Point(8, 4), Point(8, 8),
    ...                         Point(4, 8)])
    >>> fourth_square = Contour([Point(0, 4), Point(4, 4), Point(4, 8),
    ...                          Point(0, 8)])
    >>> first_inner_square = Contour([Point(1, 1), Point(3, 1), Point(3, 3),
    ...                               Point(1, 3)])
    >>> second_inner_square = Contour([Point(5, 1), Point(7, 1), Point(7, 3),
    ...                                Point(5, 3)])
    >>> third_inner_square = Contour([Point(5, 5), Point(7, 5), Point(7, 7),
    ...                               Point(5, 7)])
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  is Relation.DISJOINT)
    True
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(second_square, []),
    ...                    Polygon(fourth_square, [])]))
    ...  is multipolygon_in_multipolygon(
    ...          Multipolygon([Polygon(first_inner_square, []),
    ...                        Polygon(third_inner_square, [])]),
    ...          Multipolygon([Polygon(first_square, [first_inner_square]),
    ...                        Polygon(third_square, [third_inner_square])]))
    ...  is Relation.TOUCH)
    True
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is Relation.OVERLAP)
    True
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is Relation.COVER)
    True
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is multipolygon_in_multipolygon(
    ...          Multipolygon([Polygon(first_square, []),
    ...                        Polygon(third_square, [])]),
    ...          Multipolygon([Polygon(first_square, [first_inner_square]),
    ...                        Polygon(third_square, [third_inner_square])]))
    ...  is Relation.ENCLOSES)
    True
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is Relation.COMPOSITE)
    True
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is Relation.EQUAL)
    True
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, [])]),
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(second_inner_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is Relation.COMPONENT)
    True
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_inner_square, [])]))
    ...  is Relation.ENCLOSED)
    True
    >>> (multipolygon_in_multipolygon(
    ...      Multipolygon([Polygon(first_inner_square, []),
    ...                    Polygon(third_inner_square, [])]),
    ...      Multipolygon([Polygon(first_square, []),
    ...                    Polygon(third_square, [])]))
    ...  is Relation.WITHIN)
    True
    """
    return _multipolygon.relate_multipolygon(
            right, left, _get_context() if context is None else context)
