from enum import (IntEnum,
                  unique)


@unique
class Relation(IntEnum):
    """
    Represents kinds of relations in which geometries can be.

    Order of members assumes that conditions for previous ones do not hold.
    """
    #: intersection is empty
    DISJOINT = 0
    #: intersection is a strict subset of the geometry
    #: and only boundaries intersect, but do not cross
    TOUCH = 1
    #: intersection is a strict subset of the geometry,
    #: has dimension less than at least of one of the geometries
    #: and boundaries cross
    CROSS = 2
    #: intersection is a strict subset of the geometry,
    #: and has the same dimension as geometries
    #: and boundaries cross
    OVERLAP = 3
    #: interior/boundary of the geometry is a subset
    #: of interior/boundary of the other
    COMPONENT = 4
    #: at least one boundary point of the geometry
    #: lies on the boundary of the other, but not all,
    #: other points of the geometry lie in the interior of the other
    ENCLOSED = 5
    #: geometry is a subset of the interior of the other
    WITHIN = 6
