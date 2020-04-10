from numbers import Real
from typing import (List,
                    Tuple)

Coordinate = Real
Point = Tuple[Coordinate, Coordinate]
Segment = Tuple[Point, Point]
Contour = List[Point]
Multicontour = List[Contour]
Polygon = Tuple[Contour, Multicontour]
