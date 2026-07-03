"""
geometry.py

Computes feasible region polygon for LPModel
"""

import numpy as np
from shapely.geometry import Polygon, box


def build_geometry(model, x_hint=50, y_hint=50):

    region = box(0, 0, x_hint, y_hint)

    points = []

    grid = np.linspace(0, x_hint, 40)

    for x in grid:
        for y in grid:
            if _feasible(x, y, model):
                points.append((x, y))

    if len(points) < 3:
        return {"vertices": [], "limits": (x_hint, y_hint)}

    poly = Polygon(points).convex_hull
    region = region.intersection(poly)

    vertices = []

    if not region.is_empty and region.geom_type == "Polygon":
        coords = list(region.exterior.coords)
        vertices = [(float(x), float(y)) for x, y in coords[:-1]]

    if vertices:
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        limits = (max(xs) * 1.1, max(ys) * 1.1)
    else:
        limits = (x_hint, y_hint)

    return {
        "vertices": vertices,
        "limits": limits,
    }


def _feasible(x, y, model):

    for c in model.constraints:

        val = c.ax * x + c.ay * y

        if c.relation == "<=" and val > c.rhs + 1e-6:
            return False
        if c.relation == ">=" and val < c.rhs - 1e-6:
            return False
        if c.relation == "=" and abs(val - c.rhs) > 1e-6:
            return False

    return True
