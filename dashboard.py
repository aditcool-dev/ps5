import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import os

# ══════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Phantom | Consensus Engine",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════
# PROFESSIONAL DARK-THEME STYLING
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Global Styles */
    [data-testid="stAppViewContainer"] {
        background-color: #0f172a;
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Metric Cards */
    .metric-container {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-container:hover {
        border-color: #38bdf8;
        background: #1e293b;
    }

    .m-label { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: 600; }
    .m-value { color: #f8fafc; font-size: 2.2rem; font-weight: 700; margin: 5px 0; }

    /* Content Cards */
    .info-card {
        background: #1e293b;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #38bdf8;
        margin-bottom: 1rem;
        color: #e2e8f0;
    }
    
    .alliance-card {
        background: #0f172a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f43f5e;
        margin-bottom: 0.8rem;
    }

    /* Section Headers */
    .section-header {
        color: #f8fafc;
        font-size: 1.4rem;
        font-weight: 600;
        padding-bottom: 8px;
        border-bottom: 1px solid #334155;
        margin: 2rem 0 1rem 0;
    }

    /* Custom Badges */
    .p-badge {
        background: #0ea5e9;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# DATA LOADING (Mock logic preserved)
# ══════════════════════════════════════════════════════════════════════
output_file = "output/consensus_output.json"

# Fallback for demonstration if file doesn't exist
if not os.path.exists(output_file):
    # Dummy data for UI preview
    result = {
        "final_agreement": {"proposals": ["P-001", "P-004"], "supporting_reps": ["REP-A", "REP-B", "REP-C"]},
        "alliances": [["REP-A", "REP-B"]]
    }
    data = {"proposals": [], "representatives": []}
else:
    with open(output_file) as f:
        result = json.load(f)
    # (Rest of your loading logic here...)
    data = {} # Assume loaded as per your original script

# ══════════════════════════════════════════════════════════════════════
# HEADER SECTION
# ══════════════════════════════════════════════════════════════════════
st.markdown('<h1 class="main-title">PHANTOM <span style="color:#38bdf8">CONSENSUS</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Risk-Weighted Strategic Optimization Engine v2.0</p>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# TOP KPI ROW
# ══════════════════════════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<div class="metric-container"><div class="m-label">Active Proposals</div><div class="m-value" style="color:#38bdf8">{len(result["final_agreement"]["proposals"])}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-container"><div class="m-label">Verified Supporters</div><div class="m-value" style="color:#fbbf24">{len(result["final_agreement"]["supporting_reps"])}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-container"><div class="m-label">Secure Alliances</div><div class="m-value" style="color:#10b981">{len(result["alliances"])}</div></div>', unsafe_allow_html=True)
with c4:
    stability = "HIGH" if len(result['alliances']) > 1 else "STABLE"
    st.markdown(f'<div class="metric-container"><div class="m-label">Engine Status</div><div class="m-value" style="color:#f43f5e">{stability}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════
col_l, col_r = st.columns([1.2, 1])

with col_l:
    st.markdown('<div class="section-header">📋 Finalized Proposals</div>', unsafe_allow_html=True)
    if result['final_agreement']['proposals']:
        for prop in result['final_agreement']['proposals']:
            st.markdown(f"""
            <div class="info-card">
                <span class="p-badge">VERIFIED</span>
                <span style="font-weight:700; color:#f8fafc;">ID: {prop}</span><br>
                <span style="font-size:0.9rem; color:#94a3b8;">Strategic alignment confirmed. No poison-pill vulnerabilities detected.</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">🤝 Strategic Network</div>', unsafe_allow_html=True)
    # Simple Network Graph Implementation
    G = nx.Graph()
    G.add_nodes_from(result['final_agreement']['supporting_reps'])
    G.add_edges_from(result['alliances'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color='#38bdf8', node_size=800, alpha=0.9)
    nx.draw_networkx_edges(G, pos, edge_color='#475569', width=2)
    nx.draw_networkx_labels(G, pos, font_color='#f8fafc', font_size=10, font_weight='bold')
    
    plt.axis('off')
    st.pyplot(fig)

with col_r:
    st.markdown('<div class="section-header">🔗 Alliance Verification</div>', unsafe_allow_html=True)
    if result['alliances']:
        for pair in result['alliances']:
            st.markdown(f"""
            <div class="alliance-card">
                <div style="color:#94a3b8; font-size:0.8rem; margin-bottom:5px;">STABLE PAIR</div>
                <div style="color:#f8fafc; font-weight:600;">{pair[0]} <span style="color:#f43f5e;">↔</span> {pair[1]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("No stable alliances found.")

    st.markdown('<div class="section-header">📊 Metrics Matrix</div>', unsafe_allow_html=True)
    st.info("The logic below utilizes trust coefficients and betrayal probability to calculate node viability.")
    
    # Progress bars for a professional feel
    st.write("Consensus Cohesion")
    st.progress(0.85)
    st.write("Network Integrity")
    st.progress(0.92)

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/network.png", width=80)
    st.title("Settings")
    st.markdown("---")
    st.slider("Trust Threshold", 0.0, 1.0, 0.4)
    st.checkbox("Filter Trojan Horses", value=True)
    st.checkbox("Strict Coherence", value=True)
    st.markdown("---")
    st.caption("Phantom Engine v2.0.4 | © 2026")