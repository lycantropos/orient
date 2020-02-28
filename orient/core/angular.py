from enum import (IntEnum,
                  unique)

from robust import parallelogram

from orient.hints import (Coordinate,
                          Point)


@unique
class Orientation(IntEnum):
    CLOCKWISE = -1
    COLLINEAR = 0
    COUNTERCLOCKWISE = 1


def to_orientation(first_ray_point: Point,
                   vertex: Point,
                   second_ray_point: Point) -> Orientation:
    return Orientation(_to_sign(parallelogram.signed_area(
            vertex, first_ray_point, vertex, second_ray_point)))


def _to_sign(value: Coordinate) -> int:
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0
