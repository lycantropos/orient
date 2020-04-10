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
    #: has the same dimension as geometries
    #: and boundaries cross or interiors intersect
    OVERLAP = 3
    #: interior of the geometry is a superset of the other
    COVER = 4
    #: boundary of the geometry contains
    #: at least one boundary point of the other, but not all,
    #: interior of the geometry contains other points of the other
    ENCLOSES = 5
    #: geometry is a strict superset of the other
    #: and interior/boundary of the geometry is a superset
    #: of interior/boundary of the other
    COMPOSITE = 6
    #: geometries are equal
    EQUAL = 7
    #: geometry is a strict subset of the other
    #: and interior/boundary of the geometry is a subset
    #: of interior/boundary of the other
    COMPONENT = 8
    #: at least one boundary point of the geometry
    #: lies on the boundary of the other, but not all,
    #: other points of the geometry lie in the interior of the other
    ENCLOSED = 9
    #: geometry is a subset of the interior of the other
    WITHIN = 10
