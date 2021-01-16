from enum import (IntEnum,
                  unique)


@unique
class SegmentsRelation(IntEnum):
    DISJOINT = 0
    TOUCH = 1
    CROSS = 2
    OVERLAP = 3


@unique
class OverlapKind(IntEnum):
    NONE = 0
    SAME_ORIENTATION = 1
    DIFFERENT_ORIENTATION = 2
