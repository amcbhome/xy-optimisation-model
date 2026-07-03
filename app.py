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

# ------------------------------------------------------------
# PAGE CONFIG & ENHANCED CALCULATOR CSS
# ------------------------------------------------------------
st.set_page_config(page_title="X,Y Optimisation Calculator", layout="wide")

# CSS to fix contrast, force readable colors, enlarge text safely
st.markdown("""
    <style>
    /* GLOBAL OVERRIDES */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f4f6f9 !important;
    }
    
    /* ENLARGE AND COLOR HEADERS */
    h1 { font-size: 3.5rem !important; font-weight: 800 !important; color: #111827 !important; margin-bottom: 0.2rem !important;}
    p.stCaption { font-size: 1.2rem !important; font-weight: 500 !important; color: #64748b !important; }
    h3 { font-size: 2rem !important; font-weight: 700 !important; color: #1f2937 !important; margin-top: 1.5rem !important;}

    /* FIX STANDARD LABELS & CAPTIONS FOR READABILITY */
    label[data-testid="stWidgetLabel"] p {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }
    div[data-testid="stCaptionContainer"] p {
        color: #475569 !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
    }

    /* ENLARGE RADIO BUTTONS */
    div[data-testid="stRadio"] label p {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #111827 !important;
    }

    /* STYLE AND ENLARGE ALL INPUT FIELDS SAFELY */
    div[data-baseweb="input"] input, div[data-baseweb="number-input"] input {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        padding: 0.75rem 0.5rem !important; /* Safe padding */
        border-radius: 8px !important;
    }

    /* MASSIVE CALCULATE BUTTON & TEXT */
    div.stButton > button:first-child {
        height: 4.5em !important;
        border-radius: 12px !important;
        background-color: #ff4b4b !important;
        border: none !important;
        box-shadow: 0px 8px 15px rgba(0,0,0,0.15) !important;
        transition: all 0.3s ease 0s !important;
    }
    div.stButton > button:first-child p {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 0 !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #ff3333 !important;
        transform: translateY(-2px) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# LOGO AND TITLE 
# ------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/plasticine/200/calculator.png", width=150)
    st.divider()

st.title("🧮 X, Y Optimisation Calculator")
st.caption("A streamlined linear programming solver using PuLP")

# ------------------------------------------------------------
# COMPACT UI LAYOUT
# ------------------------------------------------------------
col_obj, col_cons = st.columns(2, gap="large")

with col_obj:
    st.subheader("1. Objective Function")
    
    c1, c2 = st.columns([1, 2])
    # Collapsed label for cleaner alignment
    opt_type = c1.radio("Goal", ["Maximise", "Minimise"], label_visibility="collapsed")
    maximise = opt_type == "Maximise"
    
    # Collapsed label, utilizing placeholder
    obj_label = c2.text_input("Objective Label", value="Profit", placeholder="Enter objective label...", label_visibility="collapsed")
    
    st.write("") # Small spacer
    
    c3, c4 = st.columns(2)
    # Collapsed labels, utilizing placeholders
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
        default_rhs = 16000.0 if i == 0 else 15000.0
        
        ax = r2.number_input("X Coeff", value=default_ax, key=f"ax_{i}", step=0.5, label_visibility="collapsed")
        ay = r3.number_input("Y Coeff", value=default_ay, key=f"ay_{i}", step=0.5, label_visibility="collapsed")
        rhs = r4.number_input("Limit", value=default_rhs, key=f"rhs_{i}", step=100.0, label_visibility="collapsed")
        
        constraints.append((c_label, ax, ay, rhs))

st.write("") 
solve_btn = st.button("Calculate Optimum", type="primary", use_container_width=True)
st.divider()

# ------------------------------------------------------------
# SOLVER & MASSIVE DIGITAL OUTPUT
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
        opt_x = value(x) if value(x) is not None else 0.0
        opt_y = value(y) if value(y) is not None else 0.0
        opt_z = value(model.objective) if value(model.objective) is not None else 0.0
        
        # HTML un-indented so Markdown doesn't parse it as a code block
        lcd_html = f"""
<div style="background-color: #1a1c23; border: 8px solid #2e3440; border-radius: 15px; padding: 40px; text-align: center; box-shadow: inset 0px 0px 25px rgba(0,0,0,0.8); margin-top: 10px;">
    <p style="font-size: 1.5rem; color: #8892b0; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 3px; font-family: 'Segoe UI', sans-serif; font-weight: 600;">Calculated {obj_label}</p>
    <div style="font-size: 6rem; color: #10b981; margin: 0; font-family: 'Courier New', Courier, monospace; font-weight: 900; text-shadow: 0px 0px 20px rgba(16, 185, 129, 0.5); line-height: 1.1;">
        £{opt_z:,.2f}
    </div>
    <hr style="border-color: #3b4252; margin: 35px 0;">
    <p style="font-size: 2rem; color: #eceff4; margin: 0; font-weight: 400; font-family: 'Segoe UI', sans-serif;">
        <span style="color: #10b981; font-weight: bold;">{opt_x:,.2f}</span> {x_label} 
        <span style="color: #4c566a; margin: 0 25px;">|</span> 
        <span style="color: #10b981; font-weight: bold;">{opt_y:,.2f}</span> {y_label}
    </p>
</div>
"""
        st.markdown(lcd_html, unsafe_allow_html=True)
            
    else:
        st.error(f"Solver Status: {status}. Please check your constraints to ensure a feasible region exists.")
else:
    st.info("👈 Configure your variables, objective function, and constraints, then click **Calculate Optimum**.")
