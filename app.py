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
st.set_page_config(
    page_title="X,Y Optimisation Calculator", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("📊 X, Y Optimisation Calculator")
st.caption("A graphical linear programming decision tool using PuLP")
st.divider()

# ------------------------------------------------------------
# CORE SOLVER & PLOT FUNCTIONS
# ------------------------------------------------------------
def solve_lp(cx, cy, maximise, constraints):
    sense = LpMaximize if maximise else LpMinimize
    model = LpProblem("XY_Model", sense)

    x = LpVariable("x", lowBound=0)
    y = LpVariable("y", lowBound=0)

    model += cx * x + cy * y

    for label, ax, ay, rhs in constraints:
        model += ax * x + ay * y <= rhs, label

    model.solve(PULP_CBC_CMD(msg=False))

    return {
        "x": value(x) if value(x) is not None else 0.0,
        "y": value(y) if value(y) is not None else 0.0,
        "z": value(model.objective) if value(model.objective) is not None else 0.0,
        "status": LpStatus[model.status],
    }

def feasible_region(constraints, x_max=100, y_max=100):
    grid = np.linspace(0, x_max, 80) # Increased density for smoother look
    points = []

    for x in grid:
        for y in grid:
            ok = True
            for _, ax, ay, rhs in constraints:
                if ax * x + ay * y > rhs:
                    ok = False
                    break
            if ok:
                points.append((x, y))

    if len(points) < 3:
        return np.array([]), (x_max, y_max)

    pts = np.array(points)
    return pts, (pts[:,0].max()*1.2, pts[:,1].max()*1.2)

def plot(solution, region, limits, constraints):
    fig = go.Figure()
    x_max, y_max = limits
    x_range = np.linspace(0, x_max, 300)

    # Plot constraints
    for i, (label, ax, ay, rhs) in enumerate(constraints):
        if ay != 0:
            y = (rhs - ax * x_range) / ay
            fig.add_trace(go.Scatter(
                x=x_range, y=y, mode="lines", name=label,
                line=dict(width=2)
            ))
        else:
            # Vertical line edge case
            fig.add_trace(go.Scatter(
                x=[rhs/ax, rhs/ax], y=[0, y_max], mode="lines", name=label,
                line=dict(width=2)
            ))

    # Plot feasible region (shaded approximation)
    if len(region) > 0:
        fig.add_trace(go.Scatter(
            x=region[:,0], y=region[:,1], mode="markers",
            marker=dict(size=5, color="rgba(0, 150, 255, 0.15)", symbol="square"),
            name="Feasible Region"
        ))

    # Plot optimum
    fig.add_trace(go.Scatter(
        x=[solution["x"]], y=[solution["y"]], mode="markers+text",
        marker=dict(size=14, color="red", line=dict(width=2, color="black")),
        text=["<b>OPT</b>"], textposition="top center",
        name="Optimal Solution"
    ))

    fig.update_layout(
        template="simple_white",
        height=550,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(range=[0, x_max], title_text="X Axis")
    fig.update_yaxes(range=[0, y_max], title_text="Y Axis")
    return fig

# ------------------------------------------------------------
# UI LAYOUT
# ------------------------------------------------------------
col_calc, col_screen = st.columns([1.2, 2], gap="large")

with col_calc:
    st.subheader("🧮 Calculator Inputs")
    
    with st.container(border=True):
        st.markdown("**1. Objective Function**")
        opt_type = st.radio("Goal:", ["Maximise", "Minimise"], horizontal=True, label_visibility="collapsed")
        maximise = opt_type == "Maximise"
        
        c1, c2 = st.columns(2)
        cx = c1.number_input("Coefficient of X", value=30.0, step=1.0)
        cy = c2.number_input("Coefficient of Y", value=40.0, step=1.0)

    with st.container(border=True):
        st.markdown("**2. Constraints**")
        constraints = []
        
        for i in range(2):
            st.caption(f"Constraint {i+1}")
            c_label = st.text_input("Label", value="Labour" if i == 0 else "Material", key=f"l_{i}", label_visibility="collapsed")
            
            c1, c2, c3 = st.columns([1, 1, 1.2])
            ax = c1.number_input("X Coeff", value=1.0, key=f"ax_{i}", step=0.5)
            ay = c2.number_input("Y Coeff", value=1.0, key=f"ay_{i}", step=0.5)
            rhs = c3.number_input("Limit (≤)", value=100.0, key=f"rhs_{i}", step=10.0)
            
            constraints.append((c_label, ax, ay, rhs))
            if i == 0: st.divider()

    solve_btn = st.button("Calculate Optimum", type="primary", use_container_width=True)

with col_screen:
    st.subheader("🖥️ Output Screen")
    
    # Real-time mathematical preview
    operator = "Max" if maximise else "Min"
    math_str = f"{operator} \\; Z = {cx}x + {cy}y \\\\"
    math_str += "\\text{Subject to: } \\\\"
    for _, ax, ay, rhs in constraints:
        math_str += f"{ax}x + {ay}y \\leq {rhs} \\\\"
    
    st.latex(math_str)
    
    if solve_btn:
        sol = solve_lp(cx, cy, maximise, constraints)
        
        if sol["status"] == "Optimal":
            # Display metrics like a digital readout
            with st.container(border=True):
                m1, m2, m3 = st.columns(3)
                m1.metric("Optimal X", f"{sol['x']:,.2f}")
                m2.metric("Optimal Y", f"{sol['y']:,.2f}")
                m3.metric(f"Objective (Z)", f"{sol['z']:,.2f}")
            
            # Generate and display plot
            region, limits = feasible_region(constraints)
            fig = plot(sol, region, limits, constraints)
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error(f"Solver Status: {sol['status']}. Please check your constraints.")
    else:
        st.info("👈 Enter your parameters and click **Calculate Optimum** to see the results.")
