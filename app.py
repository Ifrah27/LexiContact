import streamlit as st
import os
from streamlit_pdf_viewer import pdf_viewer
from ingestion import process_pdf
from knowledge_base import get_knowledge_base
from analyzer import analyze_clause
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="LexiContract AI",
    layout="wide",
    page_icon="⚖️",
    initial_sidebar_state="expanded"
)

kb = get_knowledge_base()

def get_risk_level_details(score):
    if score >= 7:
        return "High", "🔴", "error"
    elif score >= 4:
        return "Medium", "🟡", "warning"
    else:
        return "Low", "🟢", "success"

# ── Header ──
st.title("⚖️ LexiContract")
st.subheader("AI-Powered Legal Contract Analyzer")
st.markdown("---")

# ── Sidebar ──
with st.sidebar:
    st.header("📄 Upload Contract")
    uploaded_file = st.file_uploader(
        "Upload a PDF contract (NDA, Employment, SaaS ToS)", type=["pdf"]
    )

    analyze_btn = False
    if uploaded_file:
        st.write("")
        analyze_btn = st.button("🚀 Analyze Contract", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("### 📖 How it works")
    st.markdown("""
1. **Upload** your PDF contract.
2. **Extract** clauses intelligently.
3. **Compare** against standard fair clauses.
4. **Review** risk scores, issues & recommendations.
""")

# ── Main ──
if uploaded_file:
    pdf_bytes = uploaded_file.read()

    col_pdf, col_dash = st.columns([1, 1.25], gap="large")

    with col_pdf:
        st.subheader("📑 Document Preview")
        with st.container(height=800, border=True):
            pdf_viewer(pdf_bytes, width="100%")

    with col_dash:
        if analyze_btn:
            with st.spinner("🧠 Analyzing clauses — this may take a moment…"):
                clauses = process_pdf(pdf_bytes)

                results = []
                total_score = 0
                counts = {"High": 0, "Medium": 0, "Low": 0}
                seen = set()

                progress_text = "Processing document clauses..."
                bar = st.progress(0, text=progress_text)

                for i, clause in enumerate(clauses):
                    norm = " ".join(clause.split()).lower()
                    if norm in seen:
                        continue
                    seen.add(norm)

                    fair_text, metadata = kb.query_fair_clause(clause)
                    ctype = metadata["type"] if metadata else "General Clause"
                    fair_text = fair_text or "Standard reasonable commercial terms apply."

                    analysis = analyze_clause(clause, fair_text, ctype)

                    try:
                        score = float(analysis.get("risk_score", 0))
                    except (ValueError, TypeError):
                        score = 0

                    total_score += score
                    
                    level, emoji, state = get_risk_level_details(score)
                    counts[level] += 1

                    results.append({
                        "original_text": clause,
                        "analysis": analysis,
                        "score": score,
                        "level": level,
                        "emoji": emoji,
                        "state": state
                    })
                    
                    bar.progress((i + 1) / len(clauses), text=f"Analyzing clause {i+1} of {len(clauses)}...")

                bar.empty()

                n = len(results)
                avg = round(total_score / n, 1) if n else 0

            # ── Executive Summary ──
            st.subheader("📊 Executive Summary")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(label="Overall Risk", value=f"{avg} / 10")
            m2.metric(label="High Risk", value=counts["High"], delta_color="inverse")
            m3.metric(label="Medium Risk", value=counts["Medium"], delta_color="off")
            m4.metric(label="Low Risk", value=counts["Low"], delta_color="normal")
            
            st.markdown("---")
            st.subheader("🔍 Clause Analysis")

            # Sort by risk descending
            results.sort(key=lambda x: x["score"], reverse=True)

            for res in results:
                an = res["analysis"]
                score = res["score"]
                level = res["level"]
                emoji = res["emoji"]
                state = res["state"]
                
                ctype = str(an.get("clause_type", "General Clause")).replace("_", " ").title()

                issue = an.get("issue", "None") or "None"
                reason = an.get("reason", "—")
                rec = an.get("recommendation", "—")

                is_safe = issue.strip().lower() in ("none", "", "no specific risky language detected.")
                
                # Render using native container
                with st.container(border=True):
                    # Header
                    h_col1, h_col2 = st.columns([3, 1])
                    with h_col1:
                        st.markdown(f"### {ctype}")
                    with h_col2:
                        if state == "error":
                            st.error(f"{emoji} {level} Risk: **{score}/10**")
                        elif state == "warning":
                            st.warning(f"{emoji} {level} Risk: **{score}/10**")
                        else:
                            st.success(f"{emoji} {level} Risk: **{score}/10**")
                    
                    # Issue
                    st.markdown("**⚠️ Issue**")
                    if is_safe:
                        st.success("✅ No risky language detected.")
                    else:
                        st.error(f"_{issue}_")
                    
                    # Reason & Recommendation
                    st.markdown("**🧠 Reason**")
                    st.write(reason)
                    
                    st.markdown("**💡 Recommendation**")
                    st.info(rec)
                    
                    # Original Text
                    with st.expander("📄 View Original Clause Text"):
                        st.text(res["original_text"])

        else:
            # Pre-analysis
            st.info("👈 Click **Analyze Contract** in the sidebar to begin the AI risk assessment.")
else:
    # Empty state landing
    st.info("👈 **Upload a PDF contract** from the sidebar to get started.")
