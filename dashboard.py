"""
Phantom Consensus Dashboard
Streamlit visualization for consensus engine results.

Run with: streamlit run dashboard.py
"""
import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Phantom Consensus", layout="wide", page_icon="🕸️")

st.title("🕸️ Phantom Consensus — Strategic Decision Engine")

# Load output
output_file = "output/consensus_output.json"
if not os.path.exists(output_file):
    st.error(f"Output file not found: {output_file}")
    st.info("Please run `python consensus_engine.py` first to generate results.")
    st.stop()

with open(output_file) as f:
    result = json.load(f)

# ── METRICS ROW (at top) ─────────────────────────────────────────────
st.subheader("📊 Consensus Metrics")
m1, m2, m3 = st.columns(3)
m1.metric("Proposals Passed", len(result['final_agreement']['proposals']))
m2.metric("Supporting Reps", len(result['final_agreement']['supporting_reps']))
m3.metric("Alliances Found", len(result['alliances']))

st.divider()

# ── COLUMN LAYOUT ────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ Selected Proposals")
    if result['final_agreement']['proposals']:
        for p in result['final_agreement']['proposals']:
            st.success(p)
    else:
        st.warning("No proposals selected")

    st.subheader("🤝 Supporting Representatives")
    if result['final_agreement']['supporting_reps']:
        for r in result['final_agreement']['supporting_reps']:
            st.info(r)
    else:
        st.warning("No supporting representatives")

with col2:
    st.subheader("🔗 Detected Alliances")
    if result['alliances']:
        for pair in result['alliances']:
            st.warning(f"{pair[0]}  ↔  {pair[1]}")
    else:
        st.error("No stable alliances detected (Complete Rivalry)")

st.divider()

# ── NETWORK GRAPH ────────────────────────────────────────────────────
st.subheader("🕸️ Alliance Network Graph")

G = nx.Graph()

# CRITICAL FIX: Add all supporting reps as nodes first (ensures isolated nodes appear)
for rep_id in result['final_agreement']['supporting_reps']:
    G.add_node(rep_id)

# Then add alliance edges
for pair in result['alliances']:
    G.add_edge(pair[0], pair[1])

if G.number_of_nodes() == 0:
    st.info("No nodes to display. Run the consensus engine first.")
else:
    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(G, seed=42)
    
    nx.draw_networkx(G, pos, ax=ax,
        node_color='#1a1a2e', 
        font_color='white',
        edge_color='#e94560', 
        node_size=800, 
        font_size=8,
        with_labels=True)
    
    ax.set_facecolor('#16213e')
    fig.patch.set_facecolor('#16213e')
    ax.axis('off')
    
    st.pyplot(fig)

st.divider()

# ── FOOTER ───────────────────────────────────────────────────────────
st.caption("Phantom Consensus Engine — Strategic decision-making through risk-weighted optimization")
