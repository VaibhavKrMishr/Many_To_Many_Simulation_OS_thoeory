import streamlit as st
import time
import pandas as pd
import plotly.express as px
from simulator import ManyToManySimulator, ThreadState, TaskType

# Page Configuration
st.set_page_config(
    page_title="M:N Thread Model Simulator",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Configuration
with st.sidebar:
    st.header("🎨 Aesthetic Theme")
    theme = st.radio("Choose Theme", ["Midnight (Dark)", "Lab (Light)"], index=0, label_visibility="collapsed")
    is_dark = "Midnight" in theme

# Dynamic CSS Colors
bg_col = "#0e1117" if is_dark else "#f0f2f6"
card_col = "#1e2130" if is_dark else "#ffffff"
text_col = "white" if is_dark else "#0e1117"
shadow = "rgba(0,0,0,0.3)" if is_dark else "rgba(0,0,0,0.1)"

st.markdown(f"""
<style>
    .main {{
        background-color: {bg_col};
        color: {text_col};
    }}
    .stMetric {{
        background-color: {card_col};
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px {shadow};
        color: {text_col};
    }}
    .thread-card {{
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        color: white;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 2px 4px {shadow};
    }}
    .state-ready {{ background-color: #2c3e50; }}
    .state-running {{ background-color: #27ae60; border: 2px solid #2ecc71; }}
    .state-blocked {{ background-color: #c0392b; animation: pulse 2s infinite; }}
    .state-finished {{ background-color: #7f8c8d; opacity: 0.6; }}
    
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
        100% {{ opacity: 1; }}
    }}
    .thread-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 10px;
    }}
    .klt-container {{
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    h1, h2, h3, .stMarkdown, p {{
        color: {text_col} !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title("🧵 Many-to-Many (M:N) Thread Model Simulator")
st.markdown("---")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Simulation Config")
    m_ults = st.slider("User Threads (M)", 1, 50, 20)
    n_klts = st.slider("Kernel Threads (N)", 1, 10, 4)
    io_ratio = st.slider("IO-Bound Task Ratio", 0.0, 1.0, 0.3)
    sim_speed = st.select_slider("Simulation Speed", options=["Slow", "Normal", "Fast"], value="Normal")
    
    speed_map = {"Slow": 0.5, "Normal": 0.1, "Fast": 0.01}
    
    st.info(f"""
    **M:N Model ({m_ults}:{n_klts})**
    Multiplexes {m_ults} user-level threads into {n_klts} kernel threads (LWPs).
    """)
    
    run_btn = st.button("🚀 Start Simulation", width="stretch")
    reset_btn = st.button("🔄 Reset", width="stretch")

if reset_btn:
    st.session_state.clear()
    st.rerun()

# Initialize Simulator in Session State
if "sim" not in st.session_state or run_btn:
    st.session_state.sim = ManyToManySimulator(m_ults, n_klts, io_ratio)
    st.session_state.running = run_btn
    st.session_state.history = []

sim = st.session_state.sim

# Layout: Metrics -> Visualization -> Details
m1, m2, m3, m4 = st.columns(4)
metric_completed = m1.empty()
metric_util = m2.empty()
metric_cs = m3.empty()
metric_throughput = m4.empty()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🖥️ Kernel Threads (LWPs)")
    klt_elements = st.empty()

with col2:
    st.subheader("👥 User-Level Threads")
    status_grid = st.empty()

# Simulation Loop
if st.session_state.get("running", False):
    progress_bar = st.progress(0)
    
    throttle_map = {"Slow": 1, "Normal": 2, "Fast": 10}
    throttle_factor = throttle_map[sim_speed]
    
    while not sim.is_finished():
        sim.step()
        
        # Only update metrics and history on throttle
        if sim.tick % throttle_factor == 0 or sim.is_finished():
            metrics = sim.get_metrics()
            
            # Update Metrics
            metric_completed.metric("Completed", metrics["Completed"])
            metric_util.metric("CPU Util", f"{metrics['CPU Utilization (%)']}%")
            metric_cs.metric("Context Switches", metrics["Context Switches"])
            metric_throughput.metric("Throughput", metrics["Throughput"])
            
            # Update Progress Bar
            progress = metrics["Completed"] / m_ults
            progress_bar.progress(progress)
            
            # Store history (downsampled)
            st.session_state.history.append({
                "tick": metrics["Tick"],
                "completed": metrics["Completed"],
                "util": metrics["CPU Utilization (%)"]
            })

        # Update KLT and ULT Views on throttle
        if sim.tick % throttle_factor == 0 or sim.is_finished():
            # Consolidated KLT View
            klt_html = "<div class='klt-container'>"
            for kt in sim.klts.values():
                if kt.current_ult:
                    ut = sim.ults[kt.current_ult]
                    klt_html += f"<div class='thread-card state-running'>{kt.name}<br>Running: {ut.name}</div>"
                elif kt.context_switch_cooldown > 0:
                    klt_html += f"<div class='thread-card state-ready' style='border: 1px dashed white;'>{kt.name}<br>Context Switching...</div>"
                else:
                    klt_html += f"<div class='thread-card state-ready'>{kt.name}<br>Idle</div>"
            klt_html += "</div>"
            klt_elements.markdown(klt_html, unsafe_allow_html=True)
    
            # Consolidated ULT Grid
            ult_html = "<div class='thread-grid'>"
            for ut in sim.ults.values():
                state_class = f"state-{ut.state.value.lower()}"
                ult_html += f"<div class='thread-card {state_class}'>{ut.name}<br>{ut.task_type.value}<br>{ut.remaining_work} / {ut.total_work}</div>"
            ult_html += "</div>"
            status_grid.markdown(ult_html, unsafe_allow_html=True)

        time.sleep(speed_map[sim_speed])
        
    st.session_state.running = False
    st.success("Simulation Completed!")
    
    # Final Visualization and Analysis
    final_metrics = sim.get_metrics()
    
    col_g, col_a = st.columns([2, 1])
    
    with col_g:
        st.subheader("📊 Performance Analysis")
        history_df = pd.DataFrame(st.session_state.history)
        fig = px.line(history_df, x="tick", y="completed", 
                     title="Completion Progress (Throughput Dynamics)",
                     labels={"tick": "Simulation Ticks", "completed": "Threads Finished"})
        st.plotly_chart(fig, width="stretch")
        
        st.markdown(f"""
        **Graph Explanation:**
        The curve above represents the **cumulative throughput** of the system. 
        - A **steep linear slope** indicates consistent LWP utilization.
        - Any **plateaus** or slowing down suggests either threads are waiting for I/O (if ratio was high) or the LWP pool is saturated.
        - With **{n_klts} Kernel Threads**, the system can process at most {n_klts} work units per tick.
        """)

    with col_a:
        st.subheader("📋 What Happened?")
        
        # Performance Insight Logic
        ratio = m_ults / n_klts
        efficiency = final_metrics["CPU Utilization (%)"]
        
        if efficiency > 85:
            util_msg = "Excellent LWP utilization. The Kernel threads were almost never idle."
        elif efficiency > 60:
            util_msg = "Moderate utilization. Some idle time detected, likely due to context switches or high I/O blocking."
        else:
            util_msg = "Low utilization. You might have too many LWPs for the amount of work, or extreme I/O blocking."

        st.markdown(f"""
        **Key Insights:**
        
        1. **Thread Ratio ({m_ults}:{n_klts})**: 
           You mapped {m_ults} ULTs to {n_klts} LWPs. This is a **{round(ratio, 1)}:1** oversubscription.
        
        2. **Context Switching**: 
           **{final_metrics["Context Switches"]}** switches occurred. In this model, these occur when an LWP finishes a task or a thread blocks, and the scheduler picks a new ULT from the Ready Queue.
        
        3. **LWP Efficiency**: 
           {util_msg}
        
        4. **I/O Impact**:
           With an I/O ratio of **{int(io_ratio*100)}%**, the model demonstrated its strength: when a thread blocked for I/O, its LWP was immediately freed to run another ready thread.
        """)

elif not st.session_state.get("running", False) and sim.is_finished():
    st.info("Simulation finished. Press Reset to try again with different parameters.")
else:
    st.info("Adjust the parameters in the sidebar and press 'Start Simulation' to see the Many-to-Many mapping in action.")
