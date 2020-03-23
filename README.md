orient
======

[![](https://travis-ci.com/lycantropos/orient.svg?branch=master)](https://travis-ci.com/lycantropos/orient "Travis CI")
[![](https://dev.azure.com/lycantropos/orient/_apis/build/status/lycantropos.orient?branchName=master)](https://dev.azure.com/lycantropos/orient/_build/latest?definitionId=22&branchName=master "Azure Pipelines")
[![](https://readthedocs.org/projects/orient/badge/?version=latest)](https://orient.readthedocs.io/en/latest "Documentation")
[![](https://codecov.io/gh/lycantropos/orient/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/orient "Codecov")
[![](https://img.shields.io/github/license/lycantropos/orient.svg)](https://github.com/lycantropos/orient/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/orient.svg)](https://badge.fury.io/py/orient "PyPI")

In what follows
- `python` is an alias for `python3.5` or any later
version (`python3.6` and so on),
- `pypy` is an alias for `pypy3.5` or any later
version (`pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions:
- with `CPython`
  ```bash
  python -m pip install --upgrade pip setuptools
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade pip setuptools
  ```

### User

Download and install the latest stable version from `PyPI` repository:
- with `CPython`
  ```bash
  python -m pip install --upgrade orient
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade orient
  ```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/orient.git
cd orient
```

Install dependencies:
- with `CPython`
  ```bash
  python -m pip install --force-reinstall -r requirements.txt
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --force-reinstall -r requirements.txt
  ```

Install:
- with `CPython`
  ```bash
  python setup.py install
  ```
- with `PyPy`
  ```bash
  pypy setup.py install
  ```

Usage
-----

```python
>>> left_bottom = (0, 0)
>>> right_bottom = (4, 0)
>>> left_top = (0, 4)
>>> right_top = (4, 4)
>>> bottom_segment_midpoint = (2, 0)
>>> bottom_segment = (left_bottom, right_bottom)
>>> from orient.planar import PointLocation, point_in_segment
>>> point_in_segment(left_bottom, bottom_segment) is PointLocation.BOUNDARY
True
>>> (point_in_segment(bottom_segment_midpoint, bottom_segment) 
...  is PointLocation.INTERNAL)
True
>>> point_in_segment(right_bottom, bottom_segment) is PointLocation.BOUNDARY
True
>>> point_in_segment(left_top, bottom_segment) is PointLocation.EXTERNAL
True
>>> square = [left_bottom, right_bottom, right_top, left_top]
>>> from orient.planar import point_in_contour
>>> point_in_contour(left_bottom, square) is PointLocation.BOUNDARY
True
>>> point_in_contour((1, 1), square) is PointLocation.INTERNAL
True
>>> point_in_contour(right_top, square) is PointLocation.BOUNDARY
True
>>> point_in_contour((5, 5), square) is PointLocation.EXTERNAL
True
>>> main_diagonal = (left_bottom, right_top)
>>> from orient.planar import SegmentLocation, segment_in_contour
>>> segment_in_contour(bottom_segment, square) is SegmentLocation.BOUNDARY
True
>>> segment_in_contour(((1, 0), (5, 0)), square) is SegmentLocation.TOUCH
True
>>> segment_in_contour(main_diagonal, square) is SegmentLocation.ENCLOSED
True
>>> segment_in_contour(((1, 1), (2, 2)), square) is SegmentLocation.INTERNAL
True
>>> segment_in_contour(((1, 1), (5, 5)), square) is SegmentLocation.CROSS
True
>>> inner_square = [(1, 1), (3, 1), (3, 3), (1, 3)]
>>> from orient.planar import contour_in_contour
>>> contour_in_contour(square, square)
True
>>> contour_in_contour(inner_square, square)
True
>>> contour_in_contour(square, inner_square)
False
>>> from orient.planar import point_in_polygon
>>> point_in_polygon(left_bottom, (square, [])) is PointLocation.BOUNDARY
True
>>> point_in_polygon((1, 1), (square, [])) is PointLocation.INTERNAL
True
>>> point_in_polygon((2, 2), (square, [])) is PointLocation.INTERNAL
True
>>> (point_in_polygon((1, 1), (square, [inner_square]))
...  is PointLocation.BOUNDARY)
True
>>> (point_in_polygon((2, 2), (square, [inner_square]))
...  is PointLocation.EXTERNAL)
True
>>> from orient.planar import segment_in_polygon
>>> (segment_in_polygon(bottom_segment, (square, []))
...  is SegmentLocation.BOUNDARY)
True
>>> (segment_in_polygon(((1, 0), (5, 0)), (square, []))
...  is SegmentLocation.TOUCH)
True
>>> segment_in_polygon(main_diagonal, (square, [])) is SegmentLocation.ENCLOSED
True
>>> (segment_in_polygon(main_diagonal, (square, [inner_square]))
... is SegmentLocation.CROSS)
True
>>> (segment_in_polygon(((1, 1), (2, 2)), (square, []))
...  is SegmentLocation.INTERNAL)
True
>>> (segment_in_polygon(((1, 1), (2, 2)), (square, [inner_square]))
...  is SegmentLocation.TOUCH)
True
>>> segment_in_polygon(((1, 1), (5, 5)), (square, [])) is SegmentLocation.CROSS
True
>>> (segment_in_polygon(((1, 1), (5, 5)), (square, [inner_square]))
...  is SegmentLocation.CROSS)
True
>>> from orient.planar import polygon_in_polygon
>>> polygon_in_polygon((square, []), (square, []))
True
>>> polygon_in_polygon((inner_square, []), (square, []))
True
>>> polygon_in_polygon((square, []), (inner_square, []))
False
>>> polygon_in_polygon((inner_square, []), (square, [inner_square]))
False
>>> polygon_in_polygon((square, [inner_square]), (inner_square, []))
False

```

Development
-----------

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose release
```

Bump version
```bash
bump2version --verbose release
```

This will set version to `major.minor.patch`.

### Running tests

Install dependencies:
- with `CPython`
  ```bash
  python -m pip install --force-reinstall -r requirements-tests.txt
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --force-reinstall -r requirements-tests.txt
  ```

Plain
```bash
pytest
```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```bash
  ./run-tests.sh
  ```
  or
  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`
  ```bash
  ./run-tests.sh pypy
  ```

`PowerShell` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```powershell
  .\run-tests.ps1
  ```
  or
  ```powershell
  .\run-tests.ps1 cpython
  ```
- with `PyPy`
  ```powershell
  .\run-tests.ps1 pypy
  ```
