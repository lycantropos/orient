from itertools import chain
from typing import Tuple

from hypothesis import given

from orient.core.multiregion import to_segments as multiregion_to_segments
from orient.core.region import to_segments as region_to_segments
from orient.core.utils import flatten
from orient.hints import (Multipolygon,
                          Multisegment)
from orient.planar import (Relation,
                           multisegment_in_multipolygon,
                           segment_in_multipolygon)
from tests.utils import (LINEAR_COMPOUND_RELATIONS,
                         equivalence,
                         implication,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_multisegment,
                         rotations)
from . import strategies


@given(strategies.multipolygons_with_multisegments)
def test_basic(multipolygon_with_multisegment
               : Tuple[Multipolygon, Multisegment]) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = multisegment_in_multipolygon(multisegment, multipolygon)

    assert isinstance(result, Relation)
    assert result in LINEAR_COMPOUND_RELATIONS


@given(strategies.multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    assert multisegment_in_multipolygon(
            list(flatten(chain(region_to_segments(border),
                               multiregion_to_segments(holes))
                         for border, holes in multipolygon)),
            multipolygon) is (Relation.COMPONENT
                              if multipolygon
                              else Relation.DISJOINT)


@given(strategies.multipolygons_with_empty_multisegments)
def test_base(multipolygon_with_multisegment: Tuple[Multipolygon, Multisegment]
              ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = multisegment_in_multipolygon(multisegment, multipolygon)

    assert result is Relation.DISJOINT


@given(strategies.multipolygons_with_non_empty_multisegments)
def test_step(multipolygon_with_multisegment: Tuple[Multipolygon, Multisegment]
              ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment
    first_segment, *rest_multisegment = multisegment

    result = multisegment_in_multipolygon(rest_multisegment, multipolygon)
    next_result = multisegment_in_multipolygon(multisegment, multipolygon)

    relation_with_first_segment = segment_in_multipolygon(first_segment,
                                                          multipolygon)
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


@given(strategies.multipolygons_with_multisegments)
def test_reversals(multipolygon_with_multisegment
                   : Tuple[Multipolygon, Multisegment]) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = multisegment_in_multipolygon(multisegment, multipolygon)

    assert result is multisegment_in_multipolygon(
            reverse_multisegment(multisegment), multipolygon)
    assert result is multisegment_in_multipolygon(
            multisegment, reverse_multipolygon(multipolygon))
    assert result is multisegment_in_multipolygon(
            multisegment, reverse_multipolygon_borders(multipolygon))
    assert result is multisegment_in_multipolygon(
            multisegment, reverse_multipolygon_holes(multipolygon))
    assert result is multisegment_in_multipolygon(
            multisegment, reverse_multipolygon_holes_contours(multipolygon))


@given(strategies.multipolygons_with_multisegments)
def test_rotations(multipolygon_with_multisegment
                   : Tuple[Multipolygon, Multisegment]) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = multisegment_in_multipolygon(multisegment, multipolygon)

    assert all(result is multisegment_in_multipolygon(multisegment, rotated)
               for rotated in rotations(multipolygon))
    assert all(result is multisegment_in_multipolygon(rotated, multipolygon)
               for rotated in rotations(multisegment))
