import streamlit as st
from pulp import (
    LpProblem,
    LpVariable,
    LpMaximize,
    LpMinimize,
    LpStatus,
    value,
    PULP_CBC_CMD,
)
from pylatex import Document, Math, Alignat, NoEscape

# ------------------------------------------------------------
# PAGE CONFIG & CALCULATOR CSS
# ------------------------------------------------------------
st.set_page_config(page_title="X,Y Optimisation Calculator", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    html, body, [data-testid="stAppViewContainer"] { background-color: #22242c !important; }
    h1, h3 { color: #f0f0f0 !important; margin-bottom: 0 !important; margin-top: 0.5rem !important;}
    p.stCaption { color: #8a8d9e !important; font-size: 1.1rem !important; margin-bottom: 1rem !important; }
    label[data-testid="stWidgetLabel"] p { color: #b0b3c5 !important; font-size: 1rem !important; font-weight: 600 !important; }
    div[data-testid="stCaptionContainer"] p { color: #8a8d9e !important; font-size: 0.9rem !important; font-weight: 700 !important; }
    div[data-testid="stRadio"] label p { color: #f0f0f0 !important; font-size: 1.1rem !important; font-weight: 600 !important;}
    
    div[data-baseweb="input"] input, div[data-baseweb="number-input"] input {
        background-color: #0a0a0c !important; 
        color: #10b981 !important; 
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        padding: 0.5rem 0.5rem !important; 
        border-radius: 12px !important;
        border: 1px solid #2e313e !important;
    }

    div.stButton > button:first-child {
        background-color: #f49020 !important;
        color: #ffffff !important;
        height: 3.5em !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.2s ease-in-out !important;
        margin-top: 0.5rem !important;
    }
    div.stButton > button:first-child p {
        font-size: 1.4rem !important; 
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1px !important;
        margin: 0 !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #e38217 !important; 
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# LOGO, TITLE & SIDEBAR PLACEHOLDER
# ------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/plasticine/200/calculator.png", width=120)
    st.divider()
    # Create an empty container in the sidebar to inject the download button later
    sidebar_report_container = st.container()

st.title("🧮 X, Y Optimisation Calculator")
st.caption("A streamlined linear programming solver using PuLP")

# ------------------------------------------------------------
# PYLATEX GENERATOR FUNCTION
# ------------------------------------------------------------
def generate_latex_source(cx, cy, maximise, constraints, obj_label, x_label, y_label, sol):
    doc = Document()
    doc.preamble.append(NoEscape(r'\usepackage{amsmath}'))
    
    doc.append(NoEscape(r'\section*{Optimisation Report}'))
    
    # 1. Algebraic Formulation
    doc.append(NoEscape(r'\subsection*{1. Algebraic Formulation}'))
    opt_word = "Maximize" if maximise else "Minimize"
    doc.append(f"{opt_word} {obj_label}:")
    
    with doc.create(Math(display=True)):
        doc.append(NoEscape(f"Z = {cx}x + {cy}y"))
        
    doc.append("Subject to:")
    with doc.create(Alignat(numbering=False, escape=False)) as agn:
        for label, ax, ay, rhs in constraints:
            agn.append(f"{ax}x + {ay}y &\\leq {rhs} \\quad \\text{{({label})}} \\\\")
        agn.append(r"x, y &\geq 0 \\") # Standard non-negativity constraint
        
    # 2. Optimal Solution
    doc.append(NoEscape(r'\subsection*{2. Optimal Solution}'))
    if sol["status"] == "Optimal":
        doc.append("The solver successfully found the following optimal decision variables:")
        with doc.create(Alignat(numbering=False, escape=False)) as agn:
            agn.append(f"x \\text{{ ({x_label})}} &= {sol['x']:,.2f} \\\\")
            agn.append(f"y \\text{{ ({y_label})}} &= {sol['y']:,.2f} \\\\")
            agn.append(f"Z \\text{{ ({obj_label})}} &= {sol['z']:,.2f} \\\\")
    else:
        doc.append(f"No optimal solution found. Solver status: {sol['status']}")

    # Return the raw string of the LaTeX document
    return doc.dumps()

# ------------------------------------------------------------
# COMPACT UI LAYOUT
# ------------------------------------------------------------
col_obj, col_cons = st.columns(2, gap="large")

with col_obj:
    st.subheader("1. Objective Function")
    
    c1, c2 = st.columns([1, 2])
    opt_type = c1.radio("Goal", ["Maximise", "Minimise"], label_visibility="collapsed")
    maximise = opt_type == "Maximise"
    
    obj_label = c2.text_input("Objective Label", value="Profit", placeholder="Enter objective label...", label_visibility="collapsed")
    
    c3, c4 = st.columns(2)
    x_label = c3.text_input("Variable 1", value="Product A", placeholder="Enter Var 1 label...", label_visibility="collapsed")
    cx = c3.number_input(f"{x_label if x_label else 'Var 1'} Coefficient", value=30.0, step=1.0)
    
    y_label = c4.text_input("Variable 2", value="Product B", placeholder="Enter Var 2 label...", label_visibility="collapsed")
    cy = c4.number_input(f"{y_label if y_label else 'Var 2'} Coefficient", value=40.0, step=1.0)

with col_cons:
    st.subheader("2. Constraints")
    
    h1, h2, h3, h4 = st.columns([1.5, 1, 1, 1])
    h1.caption("Constraint Name")
    h2.caption(f"{x_label if x_label else 'Var 1'} Coeff")
    h3.caption(f"{y_label if y_label else 'Var 2'} Coeff")
    h4.caption("Limit (≤)")
    
    constraints = []
    
    for i in range(2):
        r1, r2, r3, r4 = st.columns([1.5, 1, 1, 1])
        c_label = r1.text_input("Name", value="Labour" if i == 0 else "Material", placeholder="Constraint name...", key=f"l_{i}", label_visibility="collapsed")
        
        default_ax = 4.0 if i == 0 else 3.0
        default_ay = 4.0 if i == 0 else 5.0
        default_rhs = 16000 if i == 0 else 15000 
        
        ax = r2.number_input("X Coeff", value=default_ax, key=f"ax_{i}", step=0.5, label_visibility="collapsed")
        ay = r3.number_input("Y Coeff", value=default_ay, key=f"ay_{i}", step=0.5, label_visibility="collapsed")
        rhs = r4.number_input("Limit", value=default_rhs, key=f"rhs_{i}", step=100, label_visibility="collapsed")
        
        constraints.append((c_label, ax, ay, rhs))

solve_btn = st.button("Calculate Decision Variables", type="primary", use_container_width=True)

# ------------------------------------------------------------
# SOLVER & DIGITAL LCD OUTPUT
# ------------------------------------------------------------
if solve_btn:
    sense = LpMaximize if maximise else LpMinimize
    model = LpProblem("XY_Model", sense)

    x = LpVariable("x", lowBound=0)
    y = LpVariable("y", lowBound=0)

    model += cx * x + cy * y

    for label, ax, ay, rhs in constraints:
        model += ax * x + ay * y <= rhs, label

    model.solve(PULP_CBC_CMD(msg=False))
    status = LpStatus[model.status]

    if status == "Optimal":
        sol_dict = {
            "status": status,
            "x": value(x) if value(x) is not None else 0.0,
            "y": value(y) if value(y) is not None else 0.0,
            "z": value(model.objective) if value(model.objective) is not None else 0.0
        }
        
        # 1. Render Digital Screen
        lcd_html = f"""
<div style="background-color: #3a4372; border-radius: 15px; padding: 20px; text-align: center; box-shadow: inset 0px 4px 10px rgba(0,0,0,0.3); margin-top: 10px;">
    <p style="font-size: 1.2rem; color: #a4adcf; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 3px; font-weight: 600;">Calculated {obj_label}</p>
    <div style="font-size: 5.5rem; color: #ffffff; margin: 0; font-family: 'Courier New', Courier, monospace; font-weight: 900; line-height: 1.1;">
        £{sol_dict['z']:,.0f}
    </div>
    <hr style="border-color: #555f94; margin: 20px 0;">
    <p style="font-size: 1.8rem; color: #e0e4f5; margin: 0; font-weight: 400;">
        <span style="font-weight: bold;">{sol_dict['x']:,.2f}</span> {x_label} 
        <span style="color: #8a94c4; margin: 0 20px;">|</span> 
        <span style="font-weight: bold;">{sol_dict['y']:,.2f}</span> {y_label}
    </p>
</div>
"""
        st.markdown(lcd_html, unsafe_allow_html=True)

        # 2. Generate LaTeX source string
        tex_source = generate_latex_source(cx, cy, maximise, constraints, obj_label, x_label, y_label, sol_dict)

        # 3. Inject Download Button into Sidebar
        with sidebar_report_container:
            st.success("✅ Optimum Found!")
            st.download_button(
                label="📄 Download LaTeX Report (.tex)",
                data=tex_source,
                file_name="optimisation_report.tex",
                mime="text/plain",
                use_container_width=True
            )
            
    else:
        st.error(f"Solver Status: {status}. Please check your constraints to ensure a feasible region exists.")
