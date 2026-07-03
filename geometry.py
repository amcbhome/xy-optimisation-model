"""
geometry.py

X,Y Optimisation Model
Graphical Linear Programming Geometry Engine

Responsibilities:
- Convert constraints into geometric half-planes
- Compute feasible region polygon
- Extract vertices (corner points)
- Compute axis limits
"""

import numpy as np
from itertools import combinations

from shapely.geometry import Polygon, LineString, box


# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------

def build_geometry(constraints, x_max_hint=50, y_max_hint=50):
    """
    Parameters
    ----------
    constraints : list
        (ax, ay, relation, rhs)

    Returns
    -------
    dict
        {
            "vertices": [(x,y), ...],
            "limits": (x_max, y_max)
        }
    """

    # --------------------------------------------------------
    # 1. START WITH A LARGE BOUNDING BOX
    #    (represents x >= 0, y >= 0 + upper bounds)
    # --------------------------------------------------------

    bounding_box = box(0, 0, x_max_hint, y_max_hint)

    # --------------------------------------------------------
    # 2. BUILD FEASIBLE REGION STEP BY STEP
    # --------------------------------------------------------

    feasible_region = bounding_box

    for ax, ay, relation, rhs in constraints:

        if ax == 0 and ay == 0:
            continue

        # ----------------------------------------------------
        # Convert constraint into a half-plane approximation
        # by sampling boundary line and splitting space
        # ----------------------------------------------------

        if ay != 0:
            # y = (rhs - ax*x) / ay
            x_vals = np.linspace(0, x_max_hint, 100)
            y_vals = (rhs - ax * x_vals) / ay

            line = LineString(zip(x_vals, y_vals))

        else:
            # vertical line x = rhs/ax
            x_val = rhs / ax
            line = LineString([(x_val, 0), (x_val, y_max_hint)])

        # ----------------------------------------------------
        # Split bounding region using approximation
        # ----------------------------------------------------

        try:
            # We approximate by clipping bounding box
            # NOTE: Shapely doesn't directly handle inequalities,
            # so we filter region via intersection tests.

            candidate_region = []

            # sample grid points inside bounding box
            for x in np.linspace(0, x_max_hint, 40):
                for y in np.linspace(0, y_max_hint, 40):

                    if _satisfies(x, y, ax, ay, relation, rhs):
                        candidate_region.append((x, y))

            if len(candidate_region) >= 3:
                poly = Polygon(candidate_region).convex_hull
                feasible_region = feasible_region.intersection(poly)

        except Exception:
            continue

    # --------------------------------------------------------
    # 3. EXTRACT VERTICES
    # --------------------------------------------------------

    vertices = []

    if feasible_region and not feasible_region.is_empty:

        if feasible_region.geom_type == "Polygon":
            coords = list(feasible_region.exterior.coords)
            vertices = [(float(x), float(y)) for x, y in coords[:-1]]

    # --------------------------------------------------------
    # 4. AXIS LIMITS
    # --------------------------------------------------------

    if vertices:
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]

        x_max = max(xs) * 1.1
        y_max = max(ys) * 1.1

    else:
        x_max = x_max_hint
        y_max = y_max_hint

    # --------------------------------------------------------
    # 5. RETURN
    # --------------------------------------------------------

    return {
        "vertices": vertices,
        "limits": (x_max, y_max),
    }


# ------------------------------------------------------------
# HELPER
# ------------------------------------------------------------

def _satisfies(x, y, ax, ay, relation, rhs):
    """
    Check if a point satisfies a constraint
    """

    value = ax * x + ay * y

    if relation == "<=":
        return value <= rhs

    elif relation == ">=":
        return value >= rhs

    elif relation == "=":
        return abs(value - rhs) < 1e-6

    return False
