"""
plotter.py

X,Y Optimisation Model
Graphical Linear Programming Visual Engine

Responsibilities:
- Plot constraint lines
- Shade feasible region
- Show corner points
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
        output from solver.py

    constraints : list
        (ax, ay, relation, rhs)
    """

    fig = go.Figure()

    # --------------------------------------------------------
    # 1. AXES
    # --------------------------------------------------------

    x_max, y_max = geometry["limits"]

    fig.update_xaxes(range=[0, x_max], title="x")
    fig.update_yaxes(range=[0, y_max], title="y")

    x_range = np.linspace(0, x_max, 300)

    # --------------------------------------------------------
    # 2. CONSTRAINT LINES
    # --------------------------------------------------------

    for i, (ax, ay, rel, rhs) in enumerate(constraints):

        if ay != 0:
            y_vals = (rhs - ax * x_range) / ay

            fig.add_trace(go.Scatter(
                x=x_range,
                y=y_vals,
                mode="lines",
                name=f"C{i+1}",
                line=dict(width=2)
            ))

        else:
            # vertical line x = rhs/ax
            if ax != 0:
                x_val = rhs / ax
                fig.add_trace(go.Scatter(
                    x=[x_val, x_val],
                    y=[0, y_max],
                    mode="lines",
                    name=f"C{i+1}",
                    line=dict(width=2)
                ))

    # --------------------------------------------------------
    # 3. FEASIBLE REGION
    # --------------------------------------------------------

    vertices = geometry.get("vertices", [])

    if vertices:

        vx = [v[0] for v in vertices]
        vy = [v[1] for v in vertices]

        # close polygon
        vx.append(vx[0])
        vy.append(vy[0])

        fig.add_trace(go.Scatter(
            x=vx,
            y=vy,
            fill="toself",
            fillcolor="rgba(0, 150, 255, 0.25)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Feasible Region"
        ))

        # ----------------------------------------------------
        # 4. CORNER POINTS
        # ----------------------------------------------------

        fig.add_trace(go.Scatter(
            x=[v[0] for v in vertices],
            y=[v[1] for v in vertices],
            mode="markers+text",
            marker=dict(size=6, color="black"),
            text=[f"({v[0]:.1f},{v[1]:.1f})" for v in vertices],
            textposition="top center",
            name="Corner Points"
        ))

    # --------------------------------------------------------
    # 5. OPTIMAL SOLUTION
    # --------------------------------------------------------

    x_opt = solution.get("x", 0)
    y_opt = solution.get("y", 0)

    fig.add_trace(go.Scatter(
        x=[x_opt],
        y=[y_opt],
        mode="markers+text",
        marker=dict(size=14, color="red"),
        text=["OPTIMUM"],
        textposition="bottom center",
        name="Optimal Solution"
    ))

    # --------------------------------------------------------
    # 6. OBJECTIVE FUNCTION LINE
    # --------------------------------------------------------

    cx = solution["objective"]["cx"]
    cy = solution["objective"]["cy"]
    z = solution["objective_value"]

    if cy != 0:
        y_obj = (z - cx * x_range) / cy

        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_obj,
            mode="lines",
            line=dict(dash="dash", color="green", width=2),
            name="Objective Function"
        ))

    # --------------------------------------------------------
    # 7. LAYOUT STYLING
    # --------------------------------------------------------

    fig.update_layout(
        title="Feasible Region and Optimal Solution",
        template="simple_white",
        width=900,
        height=650,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )

    return fig
