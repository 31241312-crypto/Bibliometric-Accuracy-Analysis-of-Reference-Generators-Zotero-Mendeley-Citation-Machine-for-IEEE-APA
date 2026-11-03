import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Bibliometric Reference Accuracy Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HEADER SECTION ---
st.title("📚 Bibliometric Accuracy Analysis Dashboard")
st.markdown("""
**Project:** Comparative Evaluation of Reference Management Generators (**Zotero**, **Mendeley**, **Citation Machine**) for **IEEE** & **APA 7th**  
**Author:** Bhagwat Gaikwad (SRN: 31241312) | **Course:** Research Methodology (BSCCS24504)  
*Benchmark Standard: UGC-STRIDE / Journal of Academic Librarianship*
""")
st.divider()

# --- BENCHMARK DATA PREPARATION ---
@st.cache_data
def load_benchmark_data():
    # Overall summary by Tool & Style
    summary_data = {
        "Tool": ["Zotero", "Zotero", "Mendeley", "Mendeley", "Citation Machine", "Citation Machine"],
        "Style": ["APA 7th", "IEEE", "APA 7th", "IEEE", "APA 7th", "IEEE"],
        "Total Evaluated": [100, 100, 100, 100, 100, 100],
        "Error-Free Citations": [86, 88, 78, 81, 54, 59],
        "Total Discrete Errors": [18, 15, 31, 24, 76, 68]
    }
    df_summary = pd.DataFrame(summary_data)
    df_summary["Accuracy (%)"] = (df_summary["Error-Free Citations"] / df_summary["Total Evaluated"]) * 100

    # Error Taxonomy Breakdown
    error_breakdown = {
        "Error Category": [
            "E1: Missing/Invalid DOI & URL",
            "E2: Title Casing Violations",
            "E3: Author/Contributor Errors",
            "E4: Volume/Issue/Pagination",
            "E5: Punctuation & Typography"
        ],
        "Zotero (APA)": [2, 9, 3, 1, 3],
        "Zotero (IEEE)": [1, 6, 2, 2, 4],
        "Mendeley (APA)": [4, 16, 5, 3, 3],
        "Mendeley (IEEE)": [3, 10, 4, 3, 4],
        "Citation Machine (APA)": [24, 22, 14, 9, 7],
        "Citation Machine (IEEE)": [21, 18, 12, 11, 6]
    }
    df_errors = pd.DataFrame(error_breakdown)

    # Accuracy by Source Media Type
    media_data = {
        "Media Type": ["Journal Articles (n=40)", "Conference Proceedings (n=25)", "Book Chapters (n=20)", "Technical/Web Reports (n=15)"],
        "Zotero": [92.5, 88.0, 75.0, 80.0],
        "Mendeley": [85.0, 76.0, 65.0, 73.3],
        "Citation Machine": [67.5, 52.0, 40.0, 46.7]
    }
    df_media = pd.DataFrame(media_data)

    return df_summary, df_errors, df_media

df_summary, df_errors, df_media = load_benchmark_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("⚙️ Dashboard Controls")
selected_style = st.sidebar.radio("Select Citation Style Filter:", ["All", "APA 7th", "IEEE"], index=0)
selected_tools = st.sidebar.multiselect(
    "Select Reference Tools:", 
    options=["Zotero", "Mendeley", "Citation Machine"], 
    default=["Zotero", "Mendeley", "Citation Machine"]
)

# Apply Filters
filtered_summary = df_summary[df_summary["Tool"].isin(selected_tools)]
if selected_style != "All":
    filtered_summary = filtered_summary[filtered_summary["Style"] == selected_style]

# --- KPI METRICS CARDS ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

avg_acc = filtered_summary["Accuracy (%)"].mean() if not filtered_summary.empty else 0
best_tool = filtered_summary.sort_values(by="Accuracy (%)", ascending=False).iloc[0]["Tool"] if not filtered_summary.empty else "N/A"
total_errs = filtered_summary["Total Discrete Errors"].sum() if not filtered_summary.empty else 0

with kpi1:
    st.metric(label="Evaluated Corpus Size", value="100 Items", delta="4 Media Formats")
with kpi2:
    st.metric(label="Average Accuracy (Filtered)", value=f"{avg_acc:.1f}%")
with kpi3:
    st.metric(label="Top Performing Tool", value=best_tool, delta="Zotero: 87.0% Avg")
with kpi4:
    st.metric(label="Total Discrete Errors Logged", value=int(total_errs), delta_color="inverse")

st.markdown("---")

# --- ROW 1: CHARTS (ACCURACY & SOURCE BREAKDOWN) ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Accuracy Rate Comparison (%)")
    fig_acc = px.bar(
        filtered_summary,
        x="Tool",
        y="Accuracy (%)",
        color="Style",
        barmode="group",
        text="Accuracy (%)",
        color_discrete_map={"APA 7th": "#1f77b4", "IEEE": "#ff7f0e"},
        range_y=[0, 100]
    )
    fig_acc.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_acc.update_layout(xaxis_title="", yaxis_title="Accuracy Rate (%)", height=400)
    st.plotly_chart(fig_acc, use_container_width=True)

with col_right:
    st.subheader("🎯 Accuracy by Publication Source Type")
    df_media_melt = df_media.melt(id_vars=["Media Type"], var_name="Tool", value_name="Accuracy (%)")
    df_media_filtered = df_media_melt[df_media_melt["Tool"].isin(selected_tools)]
    fig_media = px.line(
        df_media_filtered,
        x="Media Type",
        y="Accuracy (%)",
        color="Tool",
        markers=True,
        line_shape="linear",
        range_y=[20, 100],
        color_discrete_map={"Zotero": "#2ca02c", "Mendeley": "#1f77b4", "Citation Machine": "#d62728"}
    )
    fig_media.update_layout(xaxis_title="", yaxis_title="Accuracy Rate (%)", height=400)
    st.plotly_chart(fig_media, use_container_width=True)

st.markdown("---")

# --- ROW 2: ERROR TAXONOMY ANALYSIS ---
st.subheader("🔍 Error Taxonomy Distribution (Discrete Frequency)")

# Reshaping error table for heatmap / bar visualization
err_cols = []
for tool in selected_tools:
    if selected_style == "All":
        err_cols.extend([f"{tool} (APA)", f"{tool} (IEEE)"])
    elif selected_style == "APA 7th":
        err_cols.append(f"{tool} (APA)")
    else:
        err_cols.append(f"{tool} (IEEE)")

df_errors_display = df_errors.set_index("Error Category")[err_cols]

col_err_chart, col_err_table = st.columns([1.2, 0.8])

with col_err_chart:
    fig_err = px.bar(
        df_errors_display.reset_index().melt(id_vars=["Error Category"], var_name="Tool & Style", value_name="Error Count"),
        x="Error Category",
        y="Error Count",
        color="Tool & Style",
        barmode="group",
        height=450
    )
    fig_err.update_layout(xaxis_tickangle=-25, xaxis_title="", yaxis_title="Number of Errors")
    st.plotly_chart(fig_err, use_container_width=True)

with col_err_table:
    st.markdown("**Error Distribution Matrix**")
    st.dataframe(df_errors_display, use_container_width=True)
    st.info("💡 **Insight:** Category **E2 (Title Casing)** is the most widespread error across Mendeley and Zotero in APA mode due to sentence-case conversion issues on proper nouns.")

st.markdown("---")

# --- ROW 3: INTERACTIVE CITATION INSPECTOR ---
st.subheader("🧪 Live Citation Audit Inspector")
st.markdown("Select an academic artifact to review the ground truth vs. automated generator errors:")

sample_cases = {
    "Case 1: Proper Noun in Journal Title (APA)": {
        "Source": "Journal Article with named algorithm / framework",
        "Ground Truth": "Shaikh, S., & Kamble, A. (2024). Evaluating Markov chain dynamics in edge computing. *IEEE Transactions on Knowledge and Data Engineering*, 36(4), 112–119. https://doi.org/10.1109/TKDE.2024.10112",
        "Zotero Output": "Shaikh, S., & Kamble, A. (2024). Evaluating markov chain dynamics in edge computing. *IEEE Transactions on Knowledge and Data Engineering*, 36(4), 112–119. https://doi.org/10.1109/TKDE.2024.10112",
        "Error Identified": "❌ E2 Violation: 'Markov' converted to lowercase 'markov'."
    },
    "Case 2: Corporate/Institutional Author (IEEE)": {
        "Source": "Institutional Technical Report",
        "Ground Truth": "World Health Organization, 'Digital health interventions for secondary education,' WHO Tech. Rep. 104, Geneva, 2023.",
        "Citation Machine Output": "W. H. Organization, 'Digital health interventions for secondary education,' WHO Tech. Rep. 104, Geneva, 2023.",
        "Error Identified": "❌ E3 Violation: Inverted institutional author treated as human first/last name ('W. H. Organization')."
    },
    "Case 3: Book Chapter with Editors (APA)": {
        "Source": "Edited Volume Chapter",
        "Ground Truth": "Gaikwad, B. (2022). Ensemble tree classifiers. In R. Kumar & S. Roy (Eds.), *Machine Learning Architectures* (pp. 45–67). Springer. https://doi.org/10.1007/978-3-030",
        "Mendeley Output": "Gaikwad, B. (2022). Ensemble tree classifiers. *Machine Learning Architectures*, 45–67. https://doi.org/10.1007/978-3-030",
        "Error Identified": "❌ E3 & E4 Violation: Completely omitted editors 'R. Kumar & S. Roy (Eds.)' and 'pp.' prefix."
    }
}

selected_case = st.selectbox("Select Case Study to Inspect:", list(sample_cases.keys()))
case_info = sample_cases[selected_case]

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Correct 'Gold Standard' Reference:**")
    st.code(case_info["Ground Truth"], language="markdown")
with c2:
    st.markdown("**Automated Tool Output:**")
    st.code(case_info["Zotero Output"] if "Zotero Output" in case_info else (case_info["Citation Machine Output"] if "Citation Machine Output" in case_info else case_info["Mendeley Output"]), language="markdown")

st.warning(case_info["Error Identified"])

# --- FOOTER ---
st.markdown("---")
st.caption("Developed for UGC-STRIDE Research Methodology Project Presentation | Vishwakarma University, Pune | © 2026")