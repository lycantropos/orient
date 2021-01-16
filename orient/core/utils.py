from itertools import (chain,
                       groupby)
from typing import (Iterable,
                    Tuple,
                    TypeVar)

Domain = TypeVar('Domain')


def all_equal(values: Iterable[Domain]) -> bool:
    groups = groupby(values)
    return next(groups, True) and not next(groups, False)


flatten = chain.from_iterable


def to_sorted_pair(pair: Tuple[Domain, Domain]) -> Tuple[Domain, Domain]:
    first, second = pair
    return pair if first < second else (second, first)
