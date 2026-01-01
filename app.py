import streamlit as st
import cadquery as cq
import os
import base64
import io

# --- 1. PROJECT CONFIG ---
st.set_page_config(page_title="Nova Multi-CAD Web", layout="wide")

# Custom CSS for the "Professional Web" look
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    .stTextArea textarea { font-family: 'Fira Code', monospace; background-color: #161b22; color: #d4d4d4; }
    .stButton>button { border-radius: 4px; height: 3em; background-color: #0078d4; color: white; border: none; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR PARAMETERS ---
st.sidebar.title("⚙️ Design Parameters")
h_val = st.sidebar.number_input("Height (mm)", value=100.0)
d_val = st.sidebar.number_input("Diameter (mm)", value=60.0)
w_val = st.sidebar.number_input("Base Width (mm)", value=80.0)
t_val = st.sidebar.number_input("Shell Thickness (mm)", value=2.0)
twist = st.sidebar.slider("Twist Angle", 0, 360, 90)

# --- 3. MAIN INTERFACE ---
st.title("🚀 Multi-CAD Web Studio")
col_edit, col_view = st.columns([1, 1], gap="large")

with col_edit:
    st.subheader("📝 Script Editor")
    default_code = f"""import cadquery as cq
result = (cq.Workplane("XY")
          .rect({w_val}, {w_val})
          .circle({d_val}/2).extrude(1)
          .faces(">Z").polygon(nSides=6, diameter={d_val})
          .twistExtrude({h_val}, {twist})
          .faces(">Z").shell(-{t_val})
          .edges(">Z").fillet(0.5))"""
    user_code = st.text_area("Python Code", value=default_code, height=400)
    render_btn = st.button("🔨 GENERATE WEB ASSETS")

with col_view:
    st.subheader("🔭 3D Web Preview")
    if render_btn:
        try:
            exec_locals = {}
            exec(user_code, {"cq": cq}, exec_locals)
            obj = exec_locals.get('result')
            
            if obj:
                # Export to temp files for the session
                obj.exportStep("part.step")
                obj.exportStl("part.stl")
                # Generate DXF
                dxf_data = obj.section().toPending()
                cq.exporters.export(dxf_data, "part.dxf", cq.exporters.ExportTypes.DXF)

                # Display 3D Viewer
                with open("part.stl", "rb") as f:
                    data = base64.b64encode(f.read()).decode("utf-8")
                st.components.v1.html(f'''
                    <script src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                    <model-viewer src="data:model/stl;base64,{data}" style="width:100%; height:500px; background-color:#121212;" camera-controls auto-rotate></model-viewer>
                ''', height=510)
        except Exception as e:
            st.error(f"Logic Error: {e}")

# --- 4. WEB DOWNLOAD HUB ---
st.divider()
if os.path.exists("part.step"):
    c1, c2, c3 = st.columns(3)
    with c1: st.download_button("📐 STEP (SolidEdge/CATIA)", open("part.step","rb"), "part.step")
    with c2: st.download_button("✏️ DXF (AutoCAD)", open("part.dxf","rb"), "part.dxf")
    with c3: st.download_button("🖨️ STL (3D Print)", open("part.stl","rb"), "part.stl")