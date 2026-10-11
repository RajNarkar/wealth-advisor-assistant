import streamlit as st
import time
import pandas as pd
import plotly.express as px
from frontend.utils.api_client import api_client

st.set_page_config(
    page_title="Wealth Advisor Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-high {
        background-color: #FEE2E2;
        color: #DC2626;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-medium {
        background-color: #FEF3C7;
        color: #D97706;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-low {
        background-color: #DBEAFE;
        color: #2563EB;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .log-box {
        background-color: #0F172A;
        color: #38BDF8;
        font-family: 'Courier New', Courier, monospace;
        padding: 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        max-height: 280px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "selected_client_id" not in st.session_state:
    st.session_state.selected_client_id = "C001"

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bullish.png", width=64)
    st.title("Advisor Controls")

    # Backend Health Check
    health = api_client.get_health()
    if health.get("status") == "healthy":
        st.success("● Backend API: Online (Port 8000)")
        gemini_model = health.get("gemini_model", "gemini-3.5-flash-lite")
        key_status = "Configured" if health.get("gemini_api_key_configured") else "Simulation Mode"
        st.caption(f"Model: `{gemini_model}` ({key_status})")
    else:
        st.error("● Backend API: Offline")
        st.caption("Ensure FastAPI is running on `http://127.0.0.1:8000`")

    st.divider()

    # Client Selection
    clients = api_client.get_clients()
    client_ids = [c["client_id"] for c in clients] if clients else ["C001", "C002", "C003"]
    client_names = {c["client_id"]: f"{c['client_id']} - {c['name']} ({c['risk_profile'].capitalize()})" for c in clients}

    selected_cid = st.selectbox(
        "Select Client Profile:",
        options=client_ids,
        format_func=lambda cid: client_names.get(cid, cid),
        index=0
    )
    st.session_state.selected_client_id = selected_cid

    # Active Session Indicator
    if st.session_state.current_session_id:
        st.info(f"Active Session: `{st.session_state.current_session_id}`")
        if st.button("Clear Active Session"):
            st.session_state.current_session_id = None
            st.rerun()

    st.divider()
    st.markdown("### System Architecture")
    st.caption("• **Orchestrator Agent**: LangGraph StateGraph\n• **Specialized Agents**: DataFetcher, Analyzer, Advisor\n• **Tools**: BaseTool abstraction\n• **Human-in-the-Loop**: Checkpoint review\n• **Memory**: Session & Historical Store")

# Main Header
st.markdown('<div class="main-header">Institutional Wealth Advisor Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Multi-Agent Financial Ingestion, Anomaly Auditing & Advisory Engine</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Client Profile & Ingestion",
    "🤖 Agent Execution & Advisory",
    "🛡️ Human Checkpoint Review",
    "🧠 Memory & Historical Audit"
])

# ----------------- TAB 1: CLIENT PROFILE -----------------
with tab1:
    client_data = api_client.get_client_details(st.session_state.selected_client_id)
    if not client_data:
        st.warning("Client record unavailable or backend offline.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Client Name", client_data.get("name"), f"Age: {client_data.get('age')}")
        c2.metric("Risk Profile", client_data.get("risk_profile", "").upper())
        c3.metric("Annual Income", f"${client_data.get('annual_income', 0):,.0f}")
        total_val = client_data.get("portfolio", {}).get("total_value", 0)
        c4.metric("Total Portfolio Value", f"${total_val:,.0f}")

        st.caption(f"**Financial Goals:** {', '.join(client_data.get('goals', []))}")

        st.divider()
        col_chart, col_assets = st.columns([1, 1])

        with col_chart:
            st.subheader("Asset Allocation Breakdown")
            assets = client_data.get("portfolio", {}).get("assets", [])
            if assets:
                df_assets = pd.DataFrame(assets)
                fig = px.pie(
                    df_assets,
                    values="value",
                    names="ticker",
                    hover_data=["type"],
                    title=f"Holdings Distribution (${total_val:,.0f})",
                    hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)

        with col_assets:
            st.subheader("Holdings Detail")
            if assets:
                st.dataframe(
                    df_assets.assign(
                        Allocation=lambda d: (d["weight"] * 100).round(1).astype(str) + "%",
                        Value=lambda d: "$" + d["value"].map("{:,.0f}".format)
                    )[["ticker", "type", "Allocation", "Value"]],
                    use_container_width=True,
                    hide_index=True
                )

        st.subheader("Recent Transaction History")
        txns = client_data.get("transactions", [])
        if txns:
            df_txns = pd.DataFrame(txns)
            st.dataframe(
                df_txns.assign(Amount=lambda d: "$" + d["amount"].map("{:,.2f}".format)),
                use_container_width=True,
                hide_index=True
            )

        st.divider()
        if st.button("🚀 Trigger Multi-Agent Wealth Analysis", type="primary", use_container_width=True):
            resp = api_client.trigger_analysis(st.session_state.selected_client_id)
            if "session_id" in resp:
                st.session_state.current_session_id = resp["session_id"]
                st.success(f"Pipeline started! Session ID: `{resp['session_id']}`")
                # Auto-wait 2 seconds for initial processing
                with st.spinner("Initializing agents and ingesting data..."):
                    time.sleep(2)
                st.rerun()
            else:
                st.error(f"Failed to start pipeline: {resp.get('error')}")

# ----------------- TAB 2: AGENT EXECUTION & ADVISORY -----------------
with tab2:
    if not st.session_state.current_session_id:
        st.info("No active analysis session. Please select a client and click 'Trigger Multi-Agent Wealth Analysis' on the first tab.")
    else:
        sess_id = st.session_state.current_session_id
        session_info = api_client.get_session_status(sess_id)
        current_status = session_info.get("status", "UNKNOWN")

        # Auto-poll if session is currently progressing
        if current_status in ["RUNNING", "DATA_FETCHED", "ANALYZED", "APPROVED"] and not session_info.get("advisory_output"):
            with st.spinner(f"Agent pipeline executing ({current_status})... synthesizing Gemini advisory..."):
                time.sleep(2)
                session_info = api_client.get_session_status(sess_id)
                current_status = session_info.get("status", "UNKNOWN")
                if current_status == "COMPLETED" or session_info.get("advisory_output"):
                    st.rerun()

        st.subheader(f"Execution Console — Session `{sess_id}`")

        # Status Banner
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1:
            if current_status == "COMPLETED":
                st.success(f"Status: **{current_status}** — Institutional advisory generated successfully.")
            elif current_status == "AWAITING_APPROVAL":
                st.warning(f"Status: **{current_status}** — Paused at Human Checkpoint Gate.")
            elif current_status == "REJECTED":
                st.error(f"Status: **{current_status}** — Rejected by Wealth Advisor.")
            elif current_status in ["RUNNING", "DATA_FETCHED", "ANALYZED", "APPROVED"]:
                st.info(f"Status: **{current_status}** — LLM Synthesis in progress...")
            else:
                st.write(f"Status: **{current_status}**")

        with col_s2:
            if st.button("🔄 Refresh Status", key="refresh_tab2"):
                st.rerun()

        with col_s3:
            if current_status == "AWAITING_APPROVAL":
                st.info("👉 Switch to Tab 3 to review & approve")

        # Execution Progress Visualizer
        status_map = {
            "RUNNING": 0.25,
            "DATA_FETCHED": 0.25,
            "ANALYZED": 0.50,
            "AWAITING_APPROVAL": 0.50,
            "APPROVED": 0.75,
            "COMPLETED": 1.0,
            "REJECTED": 0.50
        }
        st.progress(status_map.get(current_status, 0.25))

        # Real-time Execution Logs
        st.markdown("**Live Agent Execution Trace:**")
        logs = session_info.get("logs", [])
        log_text = "\n".join(logs) if logs else "No execution logs captured yet..."
        st.markdown(f'<div class="log-box">{log_text.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

        st.divider()

        # Anomalies Section
        anomalies = session_info.get("anomalies", [])
        st.subheader(f"Audited Risk Signals & Anomalies ({len(anomalies)})")

        if anomalies:
            for idx, anom in enumerate(anomalies):
                sev = anom.get("severity", "LOW")
                badge_class = "badge-high" if sev == "HIGH" else "badge-medium" if sev == "MEDIUM" else "badge-low"
                with st.expander(f"⚠️ {anom.get('type')} — {anom.get('item_id')} [{sev}]", expanded=True):
                    st.markdown(f'<span class="{badge_class}">{sev} SEVERITY</span>', unsafe_allow_html=True)
                    st.write(f"**Description:** {anom.get('description')}")
                    st.info(f"**Recommended Action:** {anom.get('suggested_action')}")
        else:
            st.success("No anomalies or statistical outliers identified for this portfolio.")

        st.divider()

        # Advisory Synthesis Section
        st.subheader("Actionable Institutional Advisory Report")
        advisory_text = session_info.get("advisory_output")
        if advisory_text:
            st.markdown(advisory_text)
            st.download_button(
                "📥 Download Advisory Report (Markdown)",
                data=advisory_text,
                file_name=f"advisory_report_{sess_id}.md",
                mime="text/markdown"
            )
        elif current_status == "AWAITING_APPROVAL":
            st.warning("⚠️ Advisory report generation is paused awaiting Human Checkpoint approval on Tab 3.")
        elif current_status == "REJECTED":
            st.error("Advisory report was cancelled due to Human Advisor rejection.")
        else:
            st.caption("Advisory report is being synthesized by Gemini LLM. Click '🔄 Refresh Status' if it does not automatically update.")

# ----------------- TAB 3: HUMAN CHECKPOINT -----------------
with tab3:
    st.subheader("Human-in-the-Loop Validation Gate")
    st.caption("Inspect elevated risk signals, verify client rationale, and provide advisor override directives.")

    if not st.session_state.current_session_id:
        st.info("No active session selected. Run an analysis on Tab 1 first.")
    else:
        chk_info = api_client.get_checkpoint_status(st.session_state.current_session_id)
        chk_status = chk_info.get("status")

        if chk_status == "AWAITING_APPROVAL":
            st.warning("⚠️ **Human Approval Required:** Anomalies detected require manual sign-off before generating final advisory.")

            report = chk_info.get("analysis_report", {})
            st.markdown(f"**Audited Risk Score:** `{report.get('risk_score')}/100` ({report.get('risk_tier')})")

            anom_list = chk_info.get("anomalies", [])
            st.markdown(f"**Flagged Anomalies ({len(anom_list)}):**")
            for a in anom_list:
                st.write(f"• **[{a.get('severity')}] {a.get('type')}**: {a.get('description')}")

            st.divider()
            override_note = st.text_area(
                "Advisor Override Directive / Context:",
                placeholder="Example: Client confirmed large transaction corresponds to home purchase down-payment. Proceed with rebalancing advice."
            )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("✅ Approve Checkpoint & Generate Advisory", type="primary", use_container_width=True):
                    res = api_client.approve_checkpoint(st.session_state.current_session_id, note=override_note)
                    with st.spinner("Resuming pipeline... Synthesizing institutional advisory via Gemini LLM..."):
                        # Poll until complete (up to 10 seconds)
                        for _ in range(6):
                            time.sleep(1.5)
                            s = api_client.get_session_status(st.session_state.current_session_id)
                            if s.get("status") == "COMPLETED" or s.get("advisory_output"):
                                break
                    st.success("Advisory successfully synthesized!")
                    st.rerun()

            with col_btn2:
                if st.button("❌ Reject & Terminate Pipeline", type="secondary", use_container_width=True):
                    res = api_client.reject_checkpoint(st.session_state.current_session_id, note=override_note)
                    st.error("Rejected! Pipeline terminated.")
                    time.sleep(1)
                    st.rerun()

        elif chk_status in ["APPROVED", "COMPLETED"]:
            st.success("✅ This session was **APPROVED** and the final institutional advisory report has been synthesized!")
            sess_data = api_client.get_session_status(st.session_state.current_session_id)
            adv = sess_data.get("advisory_output")
            if adv:
                st.markdown("### Generated Advisory Preview")
                st.markdown(adv)
            else:
                with st.spinner("Finalizing report..."):
                    time.sleep(2)
                    st.rerun()
        elif chk_status == "REJECTED":
            st.error("This session was **REJECTED** by the human wealth advisor.")
        else:
            st.info(f"Current session status is `{chk_status}`. Checkpoint is not awaiting action.")

# ----------------- TAB 4: MEMORY & AUDIT TRAIL -----------------
with tab4:
    st.subheader("Memory Layer Inspection")
    m_col1, m_col2 = st.columns([1, 1])

    with m_col1:
        st.markdown("### 🏛️ Long-Term Memory (Historical Summaries)")
        st.caption("Persistent historical records stored per client across consults.")

        mem_data = api_client.get_client_memory(st.session_state.selected_client_id)
        if mem_data and mem_data.get("sessions"):
            st.markdown(f"**Cumulative Pattern Notes:** {mem_data.get('cumulative_notes')}")
            st.markdown(f"**Total Prior Consultations:** `{mem_data.get('sessions_count', len(mem_data.get('sessions', [])))}`")

            hist_sessions = mem_data.get("sessions", [])
            df_hist = pd.DataFrame(hist_sessions)
            if not df_hist.empty and "timestamp" in df_hist.columns:
                df_hist["Date"] = pd.to_datetime(df_hist["timestamp"], unit='s').dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(
                    df_hist[["Date", "session_id", "risk_score", "anomalies_detected", "summary"]],
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info(f"No long-term consultation records found yet for Client `{st.session_state.selected_client_id}`.")

    with m_col2:
        st.markdown("### ⚡ Short-Term Memory (Active Sessions)")
        st.caption("In-memory live session state and checkpoint status.")

        active_dict = api_client.get_active_sessions()
        if active_dict:
            summary_list = []
            for s_id, s_data in active_dict.items():
                summary_list.append({
                    "Session ID": s_id,
                    "Client": s_data.get("client_id"),
                    "Status": s_data.get("status"),
                    "Approved": str(s_data.get("human_approved")),
                    "Logs Count": len(s_data.get("logs", []))
                })
            st.dataframe(pd.DataFrame(summary_list), use_container_width=True, hide_index=True)
        else:
            st.info("No active short-term sessions currently in memory.")
