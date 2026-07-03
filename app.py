import streamlit as st
import numpy as np
import plotly.graph_objects as go

from pulp import (
    LpProblem,
    LpVariable,
    LpMaximize,
    LpMinimize,
    LpStatus,
    value,
    PULP_CBC_CMD,
)

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(page_title="X,Y Optimisation Tool", layout="wide")
st.title("X,Y Optimisation Model")
st.caption("Graphical linear programming decision tool")

# ------------------------------------------------------------
# SIDEBAR INPUTS
# ------------------------------------------------------------

st.sidebar.header("Objective Function")

cx = st.sidebar.number_input("Coefficient of x", value=30.0)
cy = st.sidebar.number_input("Coefficient of y", value=40.0)

maximise = st.sidebar.radio("Optimisation", ["Maximise", "Minimise"]) == "Maximise"

st.sidebar.divider()
st.sidebar.header("Constraints (2 max)")

constraints = []

for i in range(2):

    st.sidebar.subheader(f"Constraint {i+1}")

    label = st.sidebar.text_input(
        f"Label {i+1}",
        value="Labour" if i == 0 else "Material",
        key=f"label{i}"
    )

    ax = st.sidebar.number_input(f"{label} - x coefficient", value=1.0, key=f"ax{i}")
    ay = st.sidebar.number_input(f"{label} - y coefficient", value=1.0, key=f"ay{i}")

    rhs = st.sidebar.number_input(f"{label} - limit", value=100.0, key=f"rhs{i}")

    constraints.append((label, ax, ay, rhs))

# ------------------------------------------------------------
# SOLVER
# ------------------------------------------------------------

def solve_lp():

    sense = LpMaximize if maximise else LpMinimize
    model = LpProblem("XY_Model", sense)

    x = LpVariable("x", lowBound=0)
    y = LpVariable("y", lowBound=0)

    model += cx * x + cy * y

    for label, ax, ay, rhs in constraints:
        model += ax * x + ay * y <= rhs, label

    model.solve(PULP_CBC_CMD(msg=False))

    return {
        "x": value(x),
        "y": value(y),
        "z": value(model.objective),
        "status": LpStatus[model.status],
    }

# ------------------------------------------------------------
# FEASIBLE REGION (SIMPLE VISUAL APPROX)
# ------------------------------------------------------------

def feasible_region(x_max=100, y_max=100):

    grid = np.linspace(0, x_max, 60)
    points = []

    for x in grid:
        for y in grid:

            ok = True

            for _, ax, ay, rhs in constraints:

                if ax * x + ay * y > rhs:
                    ok = False

            if ok:
                points.append((x, y))

    if len(points) < 3:
        return np.array([]), (x_max, y_max)

    pts = np.array(points)

    return pts, (pts[:,0].max()*1.1, pts[:,1].max()*1.1)

# ------------------------------------------------------------
# PLOT
# ------------------------------------------------------------

def plot(solution, region, limits):

    fig = go.Figure()

    x_max, y_max = limits
    x_range = np.linspace(0, x_max, 300)

    # constraints
    for i, (label, ax, ay, rhs) in enumerate(constraints):

        if ay != 0:
            y = (rhs - ax * x_range) / ay

            fig.add_trace(go.Scatter(
                x=x_range,
                y=y,
                mode="lines",
                name=label
            ))

    # feasible region
    if len(region) > 0:
        fig.add_trace(go.Scatter(
            x=region[:,0],
            y=region[:,1],
            mode="markers",
            marker=dict(size=3),
            name="Feasible Region"
        ))

    # optimum
    fig.add_trace(go.Scatter(
        x=[solution["x"]],
        y=[solution["y"]],
        mode="markers+text",
        marker=dict(size=12, color="red"),
        text=["OPT"],
        name="Optimal Solution"
    ))

    fig.update_layout(
        title="Feasible Region & Optimal Solution",
        template="simple_white",
        height=650
    )

    fig.update_xaxes(range=[0, x_max])
    fig.update_yaxes(range=[0, y_max])

    return fig

# ------------------------------------------------------------
# RUN
# ------------------------------------------------------------

if st.button("Solve Model"):

    sol = solve_lp()
    region, limits = feasible_region()
    fig = plot(sol, region, limits)

    # LEFT: algebra
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Algebraic Model")

        st.code(f"""
Max Z = {cx}x + {cy}y

Subject to:
""" + "\n".join([
    f"{label}: {ax}x + {ay}y ≤ {rhs}"
    for label, ax, ay, rhs in constraints
]))

        st.write(sol)

    # RIGHT: graph
    with col2:
        st.subheader("Graphical Solution")
        st.plotly_chart(fig, use_container_width=True)
