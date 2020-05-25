from typing import Tuple

from hypothesis import given

from orient.core.multiregion import to_segments as multiregion_to_segments
from orient.core.region import to_segments as region_to_segments
from orient.hints import (Multisegment,
                          Polygon)
from orient.planar import (Relation,
                           multisegment_in_polygon,
                           segment_in_polygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_multisegment,
                         reverse_polygon_border,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         rotations)
from . import strategies


@given(strategies.polygons_with_multisegments)
def test_basic(polygon_with_multisegment: Tuple[Polygon, Multisegment]
               ) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = multisegment_in_polygon(multisegment, polygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.polygons)
def test_edges(polygon: Polygon) -> None:
    border, holes = polygon
    assert multisegment_in_polygon(list(region_to_segments(border))
                                   + list(multiregion_to_segments(holes)),
                                   polygon) is Relation.COMPONENT


@given(strategies.polygons_with_empty_multisegments)
def test_base(polygon_with_multisegment: Tuple[Polygon, Multisegment]) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = multisegment_in_polygon(multisegment, polygon)

    assert result is Relation.DISJOINT


@given(strategies.polygons_with_non_empty_multisegments)
def test_step(polygon_with_multisegment: Tuple[Polygon, Multisegment]) -> None:
    polygon, multisegment = polygon_with_multisegment
    first_segment, *rest_multisegment = multisegment

    result = multisegment_in_polygon(rest_multisegment, polygon)
    next_result = multisegment_in_polygon(multisegment, polygon)

    relation_with_first_segment = segment_in_polygon(first_segment, polygon)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is relation_with_first_segment
                       is Relation.DISJOINT)
    assert implication(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and relation_with_first_segment is not Relation.CROSS
                       or result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH)
    assert implication(result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH
                       or result is Relation.TOUCH
                       and relation_with_first_segment is Relation.DISJOINT,
                       next_result is Relation.TOUCH)
    assert equivalence(next_result is Relation.CROSS,
                       result is Relation.CROSS
                       or relation_with_first_segment is Relation.CROSS
                       or (bool(rest_multisegment)
                           and result is Relation.DISJOINT
                           or result is Relation.TOUCH)
                       and (relation_with_first_segment is Relation.ENCLOSED
                            or relation_with_first_segment is Relation.WITHIN)
                       or (result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH))
    assert equivalence(next_result is Relation.COMPONENT,
                       (not rest_multisegment or result is Relation.COMPONENT)
                       and relation_with_first_segment is Relation.COMPONENT)
    assert equivalence(next_result is Relation.ENCLOSED,
                       not rest_multisegment
                       and relation_with_first_segment is Relation.ENCLOSED
                       or (result is Relation.COMPONENT
                           or result is Relation.ENCLOSED)
                       and (relation_with_first_segment is Relation.ENCLOSED
                            or relation_with_first_segment is Relation.WITHIN)
                       or (result is Relation.ENCLOSED
                           or result is Relation.WITHIN)
                       and relation_with_first_segment is Relation.COMPONENT
                       or result is Relation.WITHIN
                       and relation_with_first_segment is Relation.ENCLOSED)
    assert equivalence(next_result is Relation.WITHIN,
                       (not rest_multisegment or result is Relation.WITHIN)
                       and relation_with_first_segment is Relation.WITHIN)


@given(strategies.polygons_with_multisegments)
def test_reversals(polygon_with_multisegment: Tuple[Polygon, Multisegment]
                   ) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = multisegment_in_polygon(multisegment, polygon)

    assert result is multisegment_in_polygon(
            reverse_multisegment(multisegment), polygon)
    assert result is multisegment_in_polygon(
            multisegment, reverse_polygon_border(polygon))
    assert result is multisegment_in_polygon(
            multisegment, reverse_polygon_holes(polygon))
    assert result is multisegment_in_polygon(
            multisegment, reverse_polygon_holes_contours(polygon))


@given(strategies.polygons_with_multisegments)
def test_rotations(polygon_with_multisegment: Tuple[Polygon, Multisegment]
                   ) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = multisegment_in_polygon(multisegment, polygon)

    assert all(result is multisegment_in_polygon(rotated, polygon)
               for rotated in rotations(multisegment))
