import streamlit as st
import cadquery as cq
import os
import base64

# -------------------------------
# PROJECT CONFIG
# -------------------------------
st.set_page_config(page_title="Nova Multi-CAD Web", layout="wide")

st.markdown("""
<style>
.main { background-color: #0d1117; }
.stTextArea textarea {
    font-family: monospace;
    background-color: #161b22;
    color: #d4d4d4;
}
.stButton>button {
    background-color: #0078d4;
    color: white;
    font-weight: bold;
    inline-size: 100%;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SIDEBAR PARAMETERS
# -------------------------------
st.sidebar.title("⚙️ Design Parameters")
h_val = st.sidebar.number_input("Height (mm)", 100.0)
d_val = st.sidebar.number_input("Diameter (mm)", 60.0)
w_val = st.sidebar.number_input("Base Width (mm)", 80.0)
t_val = st.sidebar.number_input("Shell Thickness (mm)", 2.0)
twist = st.sidebar.slider("Twist Angle", 0, 360, 90)

# 🔥 MATERIAL SELECTION
material = st.sidebar.selectbox(
    "Material",
    ["Aluminum", "Steel", "PLA (3D Print)", "ABS"]
)

DENSITY = {
    "Aluminum": 2700,
    "Steel": 7850,
    "PLA (3D Print)": 1240,
    "ABS": 1040
}

# -------------------------------
# MAIN UI
# -------------------------------
st.title("🚀 Multi-CAD Web Studio")
col_edit, col_view = st.columns(2)

with col_edit:
    st.subheader("📝 Script Editor")

    default_code = f"""
import cadquery as cq

result = (
    cq.Workplane("XY")
    .rect({w_val}, {w_val})
    .extrude(5)
    .faces(">Z")
    .workplane()
    .polygon(6, {d_val})
    .twistExtrude({h_val}, {twist})
    .faces(">Z")
    .shell(-{t_val})
)
"""
    user_code = st.text_area("Python Code", default_code, height=380)
    render_btn = st.button("🔨 Generate Model")

# -------------------------------
# EXECUTION & PREVIEW
# -------------------------------
with col_view:
    st.subheader("🔭 3D Web Preview")

    if render_btn:
        try:
            exec_locals = {}
            exec(user_code, {"cq": cq}, exec_locals)
            obj = exec_locals.get("result")

            if obj is None:
                st.error("❌ No variable named `result` found.")
            else:
                # -------- EXPORT 3D FILES --------
                cq.exporters.export(obj, "part.step", cq.exporters.ExportTypes.STEP)
                cq.exporters.export(obj, "part.stl", cq.exporters.ExportTypes.STL)

                # -------- DXF EXPORT (2D SKETCH) --------
                sketch = cq.Workplane("XY").rect(w_val, w_val)
                cq.exporters.export(sketch, "part.dxf", cq.exporters.ExportTypes.DXF)

                # -------- MATERIAL & WEIGHT CALC --------
                volume_mm3 = obj.val().Volume()
                volume_m3 = volume_mm3 * 1e-9
                weight_kg = volume_m3 * DENSITY[material]

                st.success("✅ Model generated successfully")
                st.info(f"""
                **Material:** {material}  
                **Volume:** {volume_mm3:.2f} mm³  
                **Weight:** {weight_kg:.3f} kg
                """)

                # -------- 3D VIEWER --------
                with open("part.stl", "rb") as f:
                    stl_data = base64.b64encode(f.read()).decode()

                st.components.v1.html(f"""
                    <script src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                    <model-viewer
                        src="data:model/stl;base64,{stl_data}"
                        style="inline-size:100%; block-size:500px; background:#121212;"
                        camera-controls auto-rotate>
                    </model-viewer>
                """, height=520)

        except Exception as e:
            st.error(f"🚨 Logic Error: {e}")

# -------------------------------
# DOWNLOAD SECTION
# -------------------------------
st.divider()
if os.path.exists("part.step"):
    c1, c2, c3 = st.columns(3)
    with c1:
        with open("part.step", "rb") as f:
            st.download_button("📐 STEP File", f, "part.step")
    with c2:
        with open("part.stl", "rb") as f:
            st.download_button("🖨️ STL File", f, "part.stl")
    with c3:
        with open("part.dxf", "rb") as f:
            st.download_button("✏️ DXF File", f, "part.dxf")

