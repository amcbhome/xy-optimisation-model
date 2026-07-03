"""
plotter.py

X,Y Optimisation Model
Graphical Linear Programming Visualiser

Responsibilities:
- Plot constraint lines
- Shade feasible region
- Plot corner points
- Highlight optimal solution
- Draw objective function line
"""

import numpy as np
import plotly.graph_objects as go


# ------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------

def build_plot(geometry, solution, constraints):
    """
    Parameters
    ----------
    geometry : dict
        {
            "vertices": [(x,y), ...],
            "limits": (x_max, y_max)
        }

    solution : dict
        {
            "x": float,
            "y": float,
            "objective_value": float,
            "objective": {"cx": a, "cy": b}
        }

    constraints : list
        [(ax, ay, relation, rhs), ...]
    """

    fig = go.Figure()

    # --------------------------------------------------------
    # 1. AXES LIMITS
    # --------------------------------------------------------

    x_max, y_max = geometry["limits"]

    x_range = np.linspace(0, x_max, 200)

    # --------------------------------------------------------
    # 2. PLOT CONSTRAINT LINES
    # --------------------------------------------------------

    for i, (ax, ay, rel, rhs) in enumerate(constraints):

        if ay == 0:
            # vertical line x = rhs/ax
            if ax != 0:
                x_val = rhs / ax
                fig.add_trace(go.Scatter(
                    x=[x_val, x_val],
                    y=[0, y_max],
                    mode="lines",
                    name=f"C{i+1}"
                ))
            continue

        # y = (rhs - ax*x) / ay
        y_vals = (rhs - ax * x_range) / ay

        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_vals,
            mode="lines",
            name=f"C{i+1}",
            line=dict(width=2)
        ))

    # --------------------------------------------------------
    # 3. FEASIBLE REGION (POLYGON)
    # --------------------------------------------------------

    if geometry.get("vertices"):

        vx = [v[0] for v in geometry["vertices"]]
        vy = [v[1] for v in geometry["vertices"]]

        # close polygon
        vx.append(vx[0])
        vy.append(vy[0])

        fig.add_trace(go.Scatter(
            x=vx,
            y=vy,
            fill="toself",
            fillcolor="rgba(0, 150, 255, 0.2)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Feasible Region"
        ))

        # vertex points
        fig.add_trace(go.Scatter(
            x=geometry["vertices"][:,0] if hasattr(geometry["vertices"], "__array__") else [v[0] for v in geometry["vertices"]],
            y=geometry["vertices"][:,1] if hasattr(geometry["vertices"], "__array__") else [v[1] for v in geometry["vertices"]],
            mode="markers",
            marker=dict(size=6, color="black"),
            name="Corner Points"
        ))

    # --------------------------------------------------------
    # 4. OPTIMAL SOLUTION
    # --------------------------------------------------------

    x_opt = solution["x"]
    y_opt = solution["y"]

    fig.add_trace(go.Scatter(
        x=[x_opt],
        y=[y_opt],
        mode="markers+text",
        marker=dict(size=12, color="red"),
        text=["Optimal"],
        textposition="top center",
        name="Optimal Solution"
    ))

    # --------------------------------------------------------
    # 5. OBJECTIVE FUNCTION LINE
    # --------------------------------------------------------

    cx = solution["objective"]["cx"]
    cy = solution["objective"]["cy"]

    if cy != 0:
        y_obj = (solution["objective_value"] - cx * x_range) / cy

        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_obj,
            mode="lines",
            line=dict(dash="dash", color="green"),
            name="Objective Function"
        ))

    # --------------------------------------------------------
    # 6. LAYOUT
    # --------------------------------------------------------

    fig.update_layout(
        title="X,Y Optimisation Model – Feasible Region",
        xaxis_title="x",
        yaxis_title="y",
        showlegend=True,
        template="simple_white",
        width=850,
        height=650,
    )

    fig.update_xaxes(range=[0, x_max])
    fig.update_yaxes(range=[0, y_max])

    return fig
