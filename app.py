import streamlit as st

from model import LPModel, Constraint
from solver import solve
from geometry import build_geometry
from plotter import build_plot


st.set_page_config(layout="wide")

st.title("X,Y Optimisation Model")


# ---------------------------
# INPUTS
# ---------------------------

cx = st.number_input("Objective x coefficient", value=40)
cy = st.number_input("Objective y coefficient", value=30)

maximise = st.radio("Objective", ["Maximise", "Minimise"]) == "Maximise"


constraints = []

st.subheader("Constraints")

for i in range(4):

    col1, col2, col3, col4 = st.columns(4)

    ax = col1.number_input(f"x{i}", value=1.0, key=f"ax{i}")
    ay = col2.number_input(f"y{i}", value=1.0, key=f"ay{i}")
    rel = col3.selectbox(f"rel{i}", ["<=", ">=", "="], key=f"rel{i}")
    rhs = col4.number_input(f"rhs{i}", value=40.0, key=f"rhs{i}")

    constraints.append(Constraint(ax, ay, rel, rhs))


# ---------------------------
# BUILD MODEL
# ---------------------------

model = LPModel(
    objective=(cx, cy),
    maximise=maximise,
    constraints=constraints
)


if st.button("Solve"):

    solution = solve(model)
    geometry = build_geometry(model)

    fig = build_plot(geometry, solution, model)

    # -----------------------
    # OUTPUTS
    # -----------------------

    st.subheader("Algebraic Model")

    st.code(f"""
Z = {cx}x + {cy}y

Constraints:
""" + "\n".join(
        [f"{c.ax}x + {c.ay}y {c.relation} {c.rhs}" for c in constraints]
    ))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Solution")
        st.write(solution)

    with col2:
        st.plotly_chart(fig, use_container_width=True)
