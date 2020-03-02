from numbers import Real
from typing import (List,
                    Tuple)

Coordinate = Real
Point = Tuple[Coordinate, Coordinate]
BoundingBox = Tuple[Coordinate, Coordinate, Coordinate, Coordinate]
Segment = Tuple[Point, Point]
Contour = List[Point]
