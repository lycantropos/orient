from typing import Tuple

from hypothesis import given

from orient.hints import (Multisegment,
                          Segment)
from orient.planar import (Relation,
                           point_in_multisegment,
                           segment_in_multisegment,
                           segment_in_segment)
from tests.utils import (SAME_LINEAR_RELATIONS,
                         equivalence,
                         implication,
                         reverse_multisegment,
                         reverse_segment,
                         rotations)
from . import strategies


@given(strategies.multisegments_with_segments)
def test_basic(multisegment_with_segment: Tuple[Multisegment, Segment]
               ) -> None:
    multisegment, segment = multisegment_with_segment

    result = segment_in_multisegment(segment, multisegment)

    assert isinstance(result, Relation)
    assert result in SAME_LINEAR_RELATIONS


@given(strategies.multisegments)
def test_self(multisegment: Multisegment) -> None:
    assert all(segment_in_multisegment(segment, multisegment)
               is (Relation.COMPONENT
                   if len(multisegment) > 1
                   else Relation.EQUAL)
               for segment in multisegment)


@given(strategies.empty_multisegments_with_segments)
def test_base(multisegment_with_segment: Tuple[Multisegment, Segment]
              ) -> None:
    multisegment, segment = multisegment_with_segment

    result = segment_in_multisegment(segment, multisegment)

    assert result is Relation.DISJOINT


@given(strategies.non_empty_multisegments_with_segments)
def test_step(multisegment_with_segment: Tuple[Multisegment, Segment]
              ) -> None:
    multisegment, segment = multisegment_with_segment
    first_segment, *rest_multisegment = multisegment

    result = segment_in_multisegment(segment, rest_multisegment)
    next_result = segment_in_multisegment(segment, multisegment)

    relation_with_first_segment = segment_in_segment(segment, first_segment)
    assert equivalence(next_result is Relation.DISJOINT,
                       result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.DISJOINT)
    assert implication(next_result is Relation.TOUCH,
                       result is Relation.TOUCH
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH)
                       or result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH)
    assert implication(result is Relation.TOUCH
                       and relation_with_first_segment is Relation.DISJOINT
                       or result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.TOUCH,
                       next_result is Relation.TOUCH)
    assert implication(next_result is Relation.CROSS,
                       result is Relation.DISJOINT
                       and relation_with_first_segment is Relation.CROSS
                       or result is Relation.TOUCH
                       and (relation_with_first_segment is Relation.TOUCH
                            or relation_with_first_segment is Relation.CROSS)
                       or result is Relation.CROSS
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH
                            or relation_with_first_segment is Relation.CROSS))
    assert implication((result is Relation.DISJOINT
                        or result is Relation.TOUCH
                        or result is Relation.CROSS)
                       and relation_with_first_segment is Relation.CROSS
                       or result is Relation.CROSS
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH),
                       next_result is Relation.CROSS)
    assert implication(next_result is Relation.OVERLAP,
                       (result is Relation.DISJOINT and rest_multisegment
                        or result is Relation.TOUCH
                        or result is Relation.CROSS)
                       and relation_with_first_segment is Relation.COMPOSITE
                       or result is Relation.OVERLAP
                       or result is Relation.COMPOSITE
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH
                            or relation_with_first_segment is Relation.OVERLAP)
                       or relation_with_first_segment is Relation.OVERLAP)
    assert implication((result is Relation.DISJOINT and rest_multisegment
                        or result is Relation.TOUCH
                        or result is Relation.CROSS)
                       and relation_with_first_segment is Relation.COMPONENT
                       or result is Relation.OVERLAP
                       and (relation_with_first_segment is Relation.DISJOINT
                            or relation_with_first_segment is Relation.TOUCH
                            or relation_with_first_segment is Relation.CROSS)
                       or (result is Relation.DISJOINT
                           or result is Relation.TOUCH
                           or result is Relation.CROSS)
                       and relation_with_first_segment is Relation.OVERLAP,
                       next_result is Relation.OVERLAP)
    assert implication(next_result is Relation.COMPOSITE,
                       (not rest_multisegment
                        or result is Relation.COMPOSITE)
                       and relation_with_first_segment is Relation.COMPOSITE)
    assert implication(not rest_multisegment
                       and relation_with_first_segment is Relation.COMPOSITE,
                       next_result is Relation.COMPOSITE)
    assert implication(next_result is Relation.EQUAL,
                       not rest_multisegment
                       and relation_with_first_segment is Relation.EQUAL
                       or result is Relation.COMPOSITE
                       and relation_with_first_segment is Relation.COMPOSITE)
    assert implication(not rest_multisegment
                       and relation_with_first_segment is Relation.EQUAL,
                       next_result is Relation.EQUAL)
    assert implication(next_result is Relation.COMPONENT,
                       result is Relation.COMPONENT
                       or relation_with_first_segment is Relation.COMPONENT
                       or result is Relation.OVERLAP
                       and (relation_with_first_segment is Relation.COMPOSITE
                            or relation_with_first_segment is Relation.OVERLAP)
                       or relation_with_first_segment is Relation.COMPONENT)


@given(strategies.multisegments_with_segments)
def test_reversed(multisegment_with_segment: Tuple[Multisegment, Segment]
                  ) -> None:
    multisegment, segment = multisegment_with_segment

    result = segment_in_multisegment(segment, multisegment)

    assert result is segment_in_multisegment(reverse_segment(segment),
                                             multisegment)
    assert result is segment_in_multisegment(
            segment, reverse_multisegment(multisegment))


@given(strategies.multisegments_with_segments)
def test_rotations(multisegment_with_segment: Tuple[Multisegment, Segment]
                   ) -> None:
    multisegment, segment = multisegment_with_segment

    result = segment_in_multisegment(segment, multisegment)

    assert all(result is segment_in_multisegment(segment, rotated)
               for rotated in rotations(multisegment))


@given(strategies.multisegments_with_segments)
def test_connection_with_point_in_multisegment(multisegment_with_segment
                                               : Tuple[Multisegment, Segment]
                                               ) -> None:
    multisegment, segment = multisegment_with_segment

    result = segment_in_multisegment(segment, multisegment)

    start, end = segment
    assert implication(result is Relation.DISJOINT,
                       point_in_multisegment(start, multisegment)
                       is point_in_multisegment(end, multisegment)
                       is Relation.DISJOINT)
