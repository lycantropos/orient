from typing import Tuple

from hypothesis import given

from orient.hints import Multisegment
from orient.planar import (Relation,
                           multisegment_in_multisegment)
from tests.utils import (ASYMMETRIC_LINEAR_RELATIONS,
                         SAME_LINEAR_RELATIONS,
                         SYMMETRIC_SAME_LINEAR_RELATIONS,
                         equivalence)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: Tuple[Multisegment, Multisegment]) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = multisegment_in_multisegment(left_multisegment,
                                          right_multisegment)

    assert isinstance(result, Relation)
    assert result in SAME_LINEAR_RELATIONS


@given(strategies.multisegments)
def test_self(multisegment: Multisegment) -> None:
    assert (multisegment_in_multisegment(multisegment, multisegment)
            is (Relation.EQUAL
                if multisegment
                else Relation.DISJOINT))


@given(strategies.non_empty_multisegments)
def test_elements(multisegment: Multisegment) -> None:
    assert equivalence(all(multisegment_in_multisegment([segment],
                                                        multisegment)
                           is Relation.EQUAL
                           for segment in multisegment),
                       len(multisegment) == 1)
    assert equivalence(all(multisegment_in_multisegment([segment],
                                                        multisegment)
                           is Relation.COMPONENT
                           for segment in multisegment),
                       len(multisegment) > 1)


@given(strategies.multisegments_pairs)
def test_symmetric_relations(multisegments_pair: Tuple[Multisegment,
                                                       Multisegment]) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = multisegment_in_multisegment(left_multisegment,
                                          right_multisegment)

    complement = multisegment_in_multisegment(right_multisegment,
                                              left_multisegment)
    assert equivalence(result is complement,
                       result in SYMMETRIC_SAME_LINEAR_RELATIONS)


@given(strategies.multisegments_pairs)
def test_asymmetric_relations(multisegments_pair: Tuple[Multisegment,
                                                        Multisegment]) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = multisegment_in_multisegment(left_multisegment,
                                          right_multisegment)

    complement = multisegment_in_multisegment(right_multisegment,
                                              left_multisegment)
    assert equivalence(result is not complement
                       and result.complement is complement,
                       result in ASYMMETRIC_LINEAR_RELATIONS
                       and complement in ASYMMETRIC_LINEAR_RELATIONS)
