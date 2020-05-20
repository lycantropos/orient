from typing import Tuple

from hypothesis import given

from orient.hints import (Multisegment,
                          Segment)
from orient.planar import (Relation,
                           point_in_multisegment,
                           segment_in_multisegment)
from tests.utils import (SAME_LINEAR_RELATIONS,
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


@given(strategies.multisegments_with_segments)
def test_outside(multisegment_with_segment: Tuple[Multisegment, Segment]
                 ) -> None:
    multisegment, segment = multisegment_with_segment

    result = segment_in_multisegment(segment, multisegment)

    start, end = segment
    assert implication(result is Relation.DISJOINT,
                       point_in_multisegment(start, multisegment)
                       is point_in_multisegment(end, multisegment)
                       is Relation.DISJOINT)


@given(strategies.multisegments_with_segments)
def test_reversed_segment(multisegment_with_segment: Tuple[Multisegment,
                                                           Segment]) -> None:
    multisegment, segment = multisegment_with_segment

    result = segment_in_multisegment(segment, multisegment)

    assert result is segment_in_multisegment(reverse_segment(segment),
                                             multisegment)


@given(strategies.multisegments_with_segments)
def test_reversed_multisegment(multisegment_with_segment: Tuple[Multisegment,
                                                                Segment]
                               ) -> None:
    multisegment, segment = multisegment_with_segment

    result = segment_in_multisegment(segment, multisegment)

    assert result is segment_in_multisegment(
            segment, reverse_multisegment(multisegment))


@given(strategies.multisegments_with_segments)
def test_rotations(multisegment_with_segment: Tuple[Multisegment, Segment]
                   ) -> None:
    multisegment, segment = multisegment_with_segment

    result = segment_in_multisegment(segment, multisegment)

    assert all(result is segment_in_multisegment(segment, rotated)
               for rotated in rotations(multisegment))
