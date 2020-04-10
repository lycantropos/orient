from numbers import Real
from typing import (List,
                    Tuple)

Coordinate = Real
Point = Tuple[Coordinate, Coordinate]
Segment = Tuple[Point, Point]
Contour = Region = List[Point]
Multicontour = Multiregion = List[Region]
Polygon = Tuple[Region, Multiregion]
