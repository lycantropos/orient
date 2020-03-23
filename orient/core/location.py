from enum import (IntEnum,
                  unique)


@unique
class PointLocation(IntEnum):
    EXTERNAL = 0
    BOUNDARY = 1
    INTERNAL = 2


@unique
class SegmentLocation(IntEnum):
    EXTERNAL = 0
    TOUCH = 1
    CROSS = 2
    BOUNDARY = 3
    ENCLOSED = 4
    INTERNAL = 5
