from hypothesis import given

from orient.planar import Relation
from . import strategies


@given(strategies.relations)
def test_basic(relation: Relation) -> None:
    assert isinstance(relation.complement, Relation)


@given(strategies.relations)
def test_involution(relation: Relation) -> None:
    assert relation.complement.complement is relation
