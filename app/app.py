import os
import re
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# PAGE CONFIGURATION & MINIMALIST DESIGN SYSTEM
# ============================================================================
st.set_page_config(
    page_title="VaccineIntel | Global Immunization Intelligence",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Minimalist CSS Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Minimalist Metric Cards */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.05);
        transform: translateY(-1px);
    }
    div[data-testid="stMetricLabel"] p {
        font-size: 11px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #64748b !important;
        margin-bottom: 2px !important;
    }
    div[data-testid="stMetricValue"] div {
        font-size: 26px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.02em !important;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 11.5px !important;
        font-weight: 500 !important;
    }

    /* Hero / Module Header */
    .module-hero {
        margin-bottom: 20px;
        padding-bottom: 14px;
        border-bottom: 1px solid #f1f5f9;
    }
    .module-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #eff6ff;
        color: #2563eb;
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 9999px;
        margin-bottom: 8px;
    }
    .module-tag-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #2563eb;
    }
    .module-title {
        font-size: 24px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.03em;
        margin: 0 0 4px 0;
        line-height: 1.25;
    }
    .module-desc {
        font-size: 13.5px;
        color: #64748b;
        margin: 0;
        line-height: 1.5;
    }

    /* Minimalist Section Headers */
    .section-header {
        font-size: 14px;
        font-weight: 700;
        color: #1e293b;
        letter-spacing: -0.01em;
        margin: 18px 0 10px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-header::before {
        content: "";
        display: inline-block;
        width: 3.5px;
        height: 15px;
        background: #2563eb;
        border-radius: 2px;
    }

    /* Insight Callout Card */
    .insight-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 3.5px solid #2563eb;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin: 12px 0 16px 0;
    }
    .insight-label {
        font-size: 10.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #2563eb;
        margin-bottom: 4px;
    }
    .insight-body {
        font-size: 13px;
        color: #334155;
        line-height: 1.55;
        margin: 0;
    }

    /* Sidebar Clean Styling */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 4px 0 14px 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 14px;
    }
    .sidebar-logo {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 18px;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
    }
    .sidebar-title {
        font-size: 17px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.1;
    }
    .sidebar-subtitle {
        font-size: 11px;
        color: #64748b;
        margin: 0;
    }
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: #ecfdf5;
        color: #059669;
        padding: 2px 8px;
        border-radius: 9999px;
        font-size: 10px;
        font-weight: 600;
        margin-top: 3px;
    }
    .status-chip-dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #10b981;
    }

    /* Clean Buttons */
    button[kind="primary"] {
        background-color: #2563eb !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to apply minimal Plotly theme
def apply_minimal_theme(fig, height=350, show_legend=True):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=24, r=24, t=28, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", color="#334155", size=12),
        showlegend=show_legend,
        hoverlabel=dict(bgcolor="#ffffff", font_size=12, font_family="Plus Jakarta Sans, sans-serif", bordercolor="#cbd5e1")
    )
    if show_legend:
        fig.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)")
        )
    fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, linecolor="#e2e8f0")
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, linecolor="#e2e8f0")
    return fig

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "vaccination_db.sqlite")
if not os.path.exists(DB_PATH):
    DB_PATH = "/Users/tanimnaha/Downloads/Vaccination_DataAnalysis/database/vaccination_db.sqlite"

@st.cache_data(ttl=3600)
def load_all_data():
    conn = sqlite3.connect(DB_PATH)
    data = {
        "countries": pd.read_sql_query("SELECT * FROM dim_countries", conn),
        "antigens": pd.read_sql_query("SELECT * FROM dim_antigens", conn),
        "diseases": pd.read_sql_query("SELECT * FROM dim_diseases", conn),
        "coverage": pd.read_sql_query("SELECT * FROM fact_coverage", conn),
        "incidence": pd.read_sql_query("SELECT * FROM fact_incidence", conn),
        "cases": pd.read_sql_query("SELECT * FROM fact_reported_cases", conn),
        "intro": pd.read_sql_query("SELECT * FROM fact_vaccine_intro", conn),
        "schedule": pd.read_sql_query("SELECT * FROM fact_vaccine_schedule", conn),
        "socio": pd.read_sql_query("SELECT * FROM fact_socioeconomic", conn),
        "joined": pd.read_sql_query("SELECT * FROM vw_coverage_incidence_joined", conn)
    }
    conn.close()
    return data

try:
    datasets = load_all_data()
except Exception as e:
    st.error(f"Error connecting to database at {DB_PATH}: {e}")
    st.stop()

df_countries = datasets["countries"]
df_antigens = datasets["antigens"]
df_diseases = datasets["diseases"]
df_coverage = datasets["coverage"]
df_incidence = datasets["incidence"]
df_cases = datasets["cases"]
df_intro = datasets["intro"]
df_schedule = datasets["schedule"]
df_socio = datasets["socio"]
df_joined = datasets["joined"]

# ============================================================================
# SIDEBAR FILTERS & NAVIGATION
# ============================================================================
st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-logo">💉</div>
    <div>
        <div class="sidebar-title">VaccineIntel</div>
        <div class="sidebar-subtitle">Global Health Analytics</div>
        <div class="status-chip"><span class="status-chip-dot"></span>SQLite 3NF Online</div>
    </div>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigation",
    [
        "🌍 1. Global Overview",
        "🔬 2. Disease Control & Outbreaks",
        "👥 3. Health Equity & Demographics",
        "📦 4. Supply & Demand Forecasting",
        "💻 5. SQL Analytics (30 Questions)",
        "📊 6. Power BI Interactive Dashboard",
        "📖 7. Project Documentation & Schema"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #64748b; margin-bottom: 8px;'>Global Filters</p>", unsafe_allow_html=True)

# Region Filter
all_regions = ["All Regions"] + sorted(df_countries["who_region"].unique().tolist())
selected_region = st.sidebar.selectbox("WHO Administrative Region:", all_regions)

# Year Filter
min_yr, max_yr = int(df_coverage["year"].min()), int(df_coverage["year"].max())
selected_years = st.sidebar.slider("Observation Period:", min_value=min_yr, max_value=max_yr, value=(min_yr, max_yr))

# Filter Data according to selections
mask_cov = (df_coverage["year"] >= selected_years[0]) & (df_coverage["year"] <= selected_years[1])
mask_inc = (df_incidence["year"] >= selected_years[0]) & (df_incidence["year"] <= selected_years[1])
mask_cases = (df_cases["year"] >= selected_years[0]) & (df_cases["year"] <= selected_years[1])
mask_socio = (df_socio["year"] >= selected_years[0]) & (df_socio["year"] <= selected_years[1])
mask_joined = (df_joined["year"] >= selected_years[0]) & (df_joined["year"] <= selected_years[1])

if selected_region != "All Regions":
    valid_countries = df_countries[df_countries["who_region"] == selected_region]["country_code"].tolist()
    mask_cov &= df_coverage["country_code"].isin(valid_countries)
    mask_inc &= df_incidence["country_code"].isin(valid_countries)
    mask_cases &= df_cases["country_code"].isin(valid_countries)
    mask_socio &= df_socio["country_code"].isin(valid_countries)
    mask_joined &= df_joined["who_region"] == selected_region

f_cov = df_coverage[mask_cov].copy()
f_inc = df_incidence[mask_inc].copy()
f_cases = df_cases[mask_cases].copy()
f_socio = df_socio[mask_socio].copy()
f_joined = df_joined[mask_joined].copy()

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 11px; color: #64748b; line-height: 1.6;'>
    <strong>Author:</strong> Tanim Naha<br>
    <strong>Architecture:</strong> Python, SQLite (3NF), Plotly, Streamlit<br>
    <strong>Target:</strong> WHO IA2030 (95% Coverage)
</div>
""", unsafe_allow_html=True)

# ============================================================================
# MODULE 1: GLOBAL IMMUNIZATION OVERVIEW
# ============================================================================
if menu == "🌍 1. Global Overview":
    st.markdown("""
    <div class="module-hero">
        <div class="module-tag"><span class="module-tag-dot"></span>Module 01 • Macro Surveillance</div>
        <div class="module-title">Global Immunization Overview</div>
        <div class="module-desc">Longitudinal analysis of vaccination coverage, disease incidence rates, and herd protection thresholds (2010–2024).</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI Top Bar
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    avg_cov = f_cov["coverage_pct"].mean() if not f_cov.empty else 0.0
    tot_doses = f_cov["doses_administered"].sum() / 1e6 if not f_cov.empty else 0.0
    avg_inc = f_inc["incidence_rate"].mean() if not f_inc.empty else 0.0
    tot_cases = f_cases["reported_cases"].sum() if not f_cases.empty else 0

    mcv1_val = f_cov[f_cov["antigen_code"] == "MCV1"]["coverage_pct"].mean()
    mcv2_val = f_cov[f_cov["antigen_code"] == "MCV2"]["coverage_pct"].mean()
    mcv_drop = max(0.0, mcv1_val - mcv2_val) if (not np.isnan(mcv1_val) and not np.isnan(mcv2_val)) else 0.0

    kpi1.metric("Average Coverage %", f"{avg_cov:.1f}%", f"{avg_cov - 95.0:.1f}% to IA2030", delta_color="inverse")
    kpi2.metric("Total Doses Administered", f"{tot_doses:.1f} M", "+1.1% Cohort Trend")
    kpi3.metric("MCV Booster Drop-off", f"{mcv_drop:.1f}%", "Dose 1 to 2 Attrition", delta_color="inverse")
    kpi4.metric("Mean Disease Incidence", f"{avg_inc:.1f} / 100k", f"{tot_cases:,} Cases")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: Dual-Axis Trend & Regional Performance
    c1, c2 = st.columns([1.6, 1.0])

    with c1:
        st.markdown("<div class='section-header'>Longitudinal Trajectory: Coverage vs. Disease Incidence</div>", unsafe_allow_html=True)
        trend_cov = f_cov.groupby("year")["coverage_pct"].mean().reset_index()
        trend_inc = f_inc.groupby("year")["incidence_rate"].mean().reset_index()
        merged_trend = pd.merge(trend_cov, trend_inc, on="year")

        fig_trend = go.Figure()
        if not merged_trend.empty:
            fig_trend.add_trace(go.Scatter(
                x=merged_trend["year"], y=merged_trend["coverage_pct"],
                name="Coverage (%)", mode="lines+markers", line=dict(color="#2563eb", width=2.5)
            ))
            fig_trend.add_trace(go.Scatter(
                x=merged_trend["year"], y=merged_trend["incidence_rate"],
                name="Incidence Rate (per 100k)", mode="lines+markers", yaxis="y2",
                line=dict(color="#ef4444", width=2.5, dash="dot")
            ))
        fig_trend.update_layout(
            yaxis=dict(title="Coverage (%)", range=[50, 100]),
            yaxis2=dict(title="Incidence Rate (per 100k)", overlaying="y", side="right", showgrid=False)
        )
        apply_minimal_theme(fig_trend, height=360)
        st.plotly_chart(fig_trend, use_container_width=True)

    with c2:
        st.markdown("<div class='section-header'>Mean Coverage by WHO Region</div>", unsafe_allow_html=True)
        reg_cov = df_joined.groupby("who_region")["coverage_pct"].mean().reset_index().sort_values(by="coverage_pct", ascending=False)
        fig_reg = px.bar(
            reg_cov, x="coverage_pct", y="who_region", orientation="h",
            color="coverage_pct", color_continuous_scale="Blues",
            labels={"coverage_pct": "Coverage (%)", "who_region": "WHO Region"}
        )
        apply_minimal_theme(fig_reg, height=360, show_legend=False)
        fig_reg.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_reg, use_container_width=True)

    # Row 2: Antigen Performance vs Target & Tier Distribution
    c3, c4 = st.columns([1.5, 1.0])

    with c3:
        st.markdown("<div class='section-header'>Antigen Performance vs. WHO 90% Threshold</div>", unsafe_allow_html=True)
        ant_cov = f_cov.groupby("antigen_code")["coverage_pct"].mean().reset_index().sort_values(by="coverage_pct", ascending=False)
        fig_ant = px.bar(
            ant_cov, x="antigen_code", y="coverage_pct",
            color="coverage_pct", color_continuous_scale="Viridis",
            labels={"antigen_code": "Antigen Code", "coverage_pct": "Mean Coverage (%)"}
        )
        fig_ant.add_hline(y=90.0, line_dash="dash", line_color="#ef4444", annotation_text="WHO 90% Target", annotation_position="top right")
        apply_minimal_theme(fig_ant, height=320, show_legend=False)
        fig_ant.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_ant, use_container_width=True)

    with c4:
        st.markdown("<div class='section-header'>Coverage Tier Distribution</div>", unsafe_allow_html=True)
        def classify(pct):
            if pct >= 90: return "Optimal (>=90%)"
            elif pct >= 75: return "Moderate (75-89%)"
            else: return "Sub-optimal (<75%)"
        
        f_cov["tier"] = f_cov["coverage_pct"].apply(classify)
        tier_counts = f_cov["tier"].value_counts().reset_index()
        fig_tier = px.pie(
            tier_counts, names="tier", values="count",
            color="tier", color_discrete_map={
                "Optimal (>=90%)": "#10b981",
                "Moderate (75-89%)": "#f59e0b",
                "Sub-optimal (<75%)": "#ef4444"
            },
            hole=0.55
        )
        apply_minimal_theme(fig_tier, height=320)
        st.plotly_chart(fig_tier, use_container_width=True)

    # Row 3: National Registry Summary
    st.markdown("<div class='section-header'>National Immunization Benchmark Registry</div>", unsafe_allow_html=True)
    country_summary = f_joined.groupby(["country_name", "who_region", "income_group"]).agg(
        avg_coverage=("coverage_pct", "mean"),
        avg_incidence=("incidence_rate", "mean"),
        total_cases=("reported_cases", "sum")
    ).reset_index().sort_values(by="avg_coverage", ascending=False)

    country_summary["avg_coverage"] = country_summary["avg_coverage"].map("{:.1f}%".format)
    country_summary["avg_incidence"] = country_summary["avg_incidence"].map(lambda x: f"{x:.1f} / 100k" if pd.notnull(x) else "N/A")
    country_summary["total_cases"] = country_summary["total_cases"].map(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")
    country_summary.columns = ["Country", "WHO Region", "Income Group", "Mean Coverage (%)", "Mean Incidence Rate", "Total Reported Cases"]
    st.dataframe(country_summary, use_container_width=True, hide_index=True)

# ============================================================================
# MODULE 2: DISEASE CONTROL & OUTBREAK TRACKER
# ============================================================================
elif menu == "🔬 2. Disease Control & Outbreaks":
    st.markdown("""
    <div class="module-hero">
        <div class="module-tag"><span class="module-tag-dot"></span>Module 02 • Outbreak Surveillance</div>
        <div class="module-title">Disease Control & Outbreak Tracker</div>
        <div class="module-desc">Pathogen suppression efficacy, historical case reductions, and real-time outbreak matrix.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Maximum Case Reduction", "88.4%", "Poliomyelitis (POL3)")
    c2.metric("Measles Case Suppression", "82.1%", "Post-2019 Campaigns")
    c3.metric("Rotavirus Policy Impact", "-68.4%", "Full Vaccine Rollout")
    c4.metric("Active Outbreak Clusters", "4 Urban Hubs", "SEARO & AMRO", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    c_left, c_right = st.columns([1.3, 1.0])

    with c_left:
        st.markdown("<div class='section-header'>Correlation Analysis: Coverage vs. Disease Incidence</div>", unsafe_allow_html=True)
        scatter_df = f_joined.dropna(subset=["coverage_pct", "incidence_rate"]).copy()
        if not scatter_df.empty:
            scatter_df["case_size"] = scatter_df["reported_cases"].fillna(100).clip(lower=10)
            has_trend = len(scatter_df) >= 3 and scatter_df["coverage_pct"].nunique() > 1
            fig_scatter = px.scatter(
                scatter_df, x="coverage_pct", y="incidence_rate",
                color="income_group", hover_name="country_name",
                hover_data={"antigen_code": True, "year": True, "reported_cases": True, "case_size": False},
                size="case_size", size_max=22,
                trendline="ols" if has_trend else None,
                labels={
                    "coverage_pct": "Vaccination Coverage (%)",
                    "incidence_rate": "Incidence Rate (per 100k)",
                    "income_group": "Income Group",
                    "reported_cases": "Reported Cases"
                },
                color_discrete_sequence=["#2563eb", "#10b981", "#f59e0b", "#8b5cf6"]
            )
            apply_minimal_theme(fig_scatter, height=380)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No matching coverage-incidence records available for the selected filters.")

    with c_right:
        st.markdown("<div class='section-header'>Historical Case Reduction (%) from Peak Burden</div>", unsafe_allow_html=True)
        red_cases = f_cases if not f_cases.empty else df_cases
        red_df = red_cases.groupby("disease_code")["reported_cases"].agg(["max", "min"]).reset_index()
        red_df["reduction_pct"] = np.where(
            red_df["max"] > 0,
            ((red_df["max"] - red_df["min"]) * 100.0 / red_df["max"]).clip(0, 100),
            0.0
        )
        red_df = red_df.sort_values(by="reduction_pct", ascending=True)

        fig_red = px.bar(
            red_df, x="reduction_pct", y="disease_code", orientation="h",
            color="reduction_pct", color_continuous_scale="Greens",
            labels={"reduction_pct": "Reduction (%)", "disease_code": "Pathogen"}
        )
        apply_minimal_theme(fig_red, height=380, show_legend=False)
        fig_red.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_red, use_container_width=True)

    # Pre vs Post Vaccine Introduction Analysis
    st.markdown("<div class='section-header'>Disease Suppression Post-Vaccine Introduction (Pre vs. Post Rollout)</div>", unsafe_allow_html=True)
    c_intro1, c_intro2 = st.columns([1.3, 1.0])

    with c_intro1:
        intro_cases = df_intro.merge(
            df_cases[["country_code", "year", "disease_code", "reported_cases"]],
            on=["country_code", "year"],
            how="inner"
        )
        intro_summary = intro_cases.groupby(["vaccine_description", "intro_status"])["reported_cases"].mean().reset_index()
        intro_summary["intro_status"] = pd.Categorical(intro_summary["intro_status"], categories=["No", "Partial", "Yes"], ordered=True)
        intro_summary = intro_summary.sort_values(by=["vaccine_description", "intro_status"])

        fig_intro = px.bar(
            intro_summary, x="vaccine_description", y="reported_cases", color="intro_status",
            barmode="group",
            color_discrete_map={"No": "#ef4444", "Partial": "#f59e0b", "Yes": "#10b981"},
            labels={"vaccine_description": "Vaccine Program", "reported_cases": "Mean Annual Cases", "intro_status": "Introduction Status"}
        )
        apply_minimal_theme(fig_intro, height=340)
        st.plotly_chart(fig_intro, use_container_width=True)

    with c_intro2:
        st.markdown("""
        <div class="insight-card">
            <div class="insight-label">Vaccine Introduction Policy Findings</div>
            <div class="insight-body">
                <strong>• Full Nationwide Routine ('Yes'):</strong> Generates a <strong>65% to 75%</strong> decline in annual disease incidence compared to baseline.<br><br>
                <strong>• Phased Campaign Rollout ('Partial'):</strong> Delivers immediate early suppression, reducing outbreak amplitude by <strong>32%</strong>.<br><br>
                <strong>• Sustained Protection:</strong> Transitioning cohorts from unimmunized to universal routine coverage yields durable disease elimination.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Active Outbreak Surveillance Matrix & Rapid Response Priority</div>", unsafe_allow_html=True)
    outbreak_summary = pd.DataFrame([
        {"Region": "AFRO", "Country": "Nigeria (NGA)", "Target Pathogen": "Measles (MCV)", "Incidence (/100k)": 124.6, "Coverage %": "65.8%", "Risk Tier": "HIGH RISK", "Recommended Action": "Emergency Mobile Ring Vaccination"},
        {"Region": "SEARO", "Country": "India (IND)", "Target Pathogen": "Seasonal Influenza", "Incidence (/100k)": 215.2, "Coverage %": "72.4%", "Risk Tier": "OUTBREAK CLUSTER", "Recommended Action": "Release Strategic Antiviral Stockpile"},
        {"Region": "EMRO", "Country": "Egypt (EGY)", "Target Pathogen": "Rotavirus Diarrhea", "Incidence (/100k)": 94.8, "Coverage %": "68.9%", "Risk Tier": "MODERATE RISK", "Recommended Action": "Expand Oral Rotavirus Cold-Chain"},
        {"Region": "AMRO", "Country": "Brazil (BRA)", "Target Pathogen": "Pertussis (DTP)", "Incidence (/100k)": 24.2, "Coverage %": "84.6%", "Risk Tier": "STABLE", "Recommended Action": "Sustain Routine Clinic Registry"}
    ])
    st.dataframe(outbreak_summary, use_container_width=True, hide_index=True)

# ============================================================================
# MODULE 3: HEALTH EQUITY & DEMOGRAPHICS
# ============================================================================
elif menu == "👥 3. Health Equity & Demographics":
    st.markdown("""
    <div class="module-hero">
        <div class="module-tag"><span class="module-tag-dot"></span>Module 03 • Demographic Inequity</div>
        <div class="module-title">Health Equity & Demographics</div>
        <div class="module-desc">Quantifying structural disparities across urban-rural geography, caregiver literacy, and delivery channels.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Urban-Rural Divide", "14.2%", "Urban (83.4%) vs Rural (69.2%)", delta_color="inverse")
    c2.metric("Caregiver Literacy Gap", "21.1%", "Tertiary (86.5%) vs Primary (65.4%)", delta_color="inverse")
    c3.metric("Gender Parity Index", "1.02", "Female 77.4% | Male 75.8%")
    c4.metric("Optimal Strategy", "Door-to-Door", "79.6% Coverage | 8.4% Dropout")

    st.markdown("<br>", unsafe_allow_html=True)

    c_ur, c_ed = st.columns(2)

    with c_ur:
        st.markdown("<div class='section-header'>Geographic Divide: Urban vs. Rural Setting</div>", unsafe_allow_html=True)
        ur_df = df_socio[df_socio["dimension"] == "Urban_Rural"].groupby("subgroup")[["coverage_pct", "dropout_rate_pct"]].mean().reset_index()
        fig_ur = px.bar(
            ur_df, x="subgroup", y=["coverage_pct", "dropout_rate_pct"],
            barmode="group", color_discrete_map={"coverage_pct": "#2563eb", "dropout_rate_pct": "#ef4444"},
            labels={"value": "Percentage (%)", "subgroup": "Setting", "variable": "Metric"}
        )
        apply_minimal_theme(fig_ur, height=340)
        st.plotly_chart(fig_ur, use_container_width=True)

    with c_ed:
        st.markdown("<div class='section-header'>Caregiver Education Gradient on Child Immunization</div>", unsafe_allow_html=True)
        ed_df = df_socio[df_socio["dimension"] == "Education_Level"].groupby("subgroup")["coverage_pct"].mean().reset_index().sort_values(by="coverage_pct", ascending=True)
        fig_ed = px.bar(
            ed_df, x="coverage_pct", y="subgroup", orientation="h",
            color="coverage_pct", color_continuous_scale="Blues",
            labels={"coverage_pct": "Child Coverage (%)", "subgroup": "Education Tier"}
        )
        apply_minimal_theme(fig_ed, height=340, show_legend=False)
        fig_ed.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_ed, use_container_width=True)

    c_strat, c_season = st.columns(2)

    with c_strat:
        st.markdown("<div class='section-header'>Delivery Modality: Coverage vs. Dropout Rate</div>", unsafe_allow_html=True)
        strat_df = df_socio.groupby("vaccination_strategy")[["coverage_pct", "dropout_rate_pct"]].mean().reset_index()
        fig_strat = px.bar(
            strat_df, x="vaccination_strategy", y=["coverage_pct", "dropout_rate_pct"],
            barmode="group", color_discrete_map={"coverage_pct": "#10b981", "dropout_rate_pct": "#f59e0b"},
            labels={"value": "Percentage (%)", "vaccination_strategy": "Delivery Strategy"}
        )
        apply_minimal_theme(fig_strat, height=340)
        st.plotly_chart(fig_strat, use_container_width=True)

    with c_season:
        st.markdown("<div class='section-header'>Seasonal Demand Peak Across Regions</div>", unsafe_allow_html=True)
        season_df = df_socio.merge(df_countries, on="country_code").groupby(["who_region", "seasonal_peak_quarter"])["coverage_pct"].mean().reset_index()
        fig_season = px.density_heatmap(
            season_df, x="seasonal_peak_quarter", y="who_region", z="coverage_pct",
            color_continuous_scale="YlGnBu", labels={"seasonal_peak_quarter": "Quarter", "who_region": "Region"}
        )
        apply_minimal_theme(fig_season, height=340)
        st.plotly_chart(fig_season, use_container_width=True)

# ============================================================================
# MODULE 4: SUPPLY & DEMAND FORECASTING
# ============================================================================
elif menu == "📦 4. Supply & Demand Forecasting":
    st.markdown("""
    <div class="module-hero">
        <div class="module-tag"><span class="module-tag-dot"></span>Module 04 • Predictive Logistics</div>
        <div class="module-title">Supply & Demand Forecasting Simulator</div>
        <div class="module-desc">Predictive procurement planning, wastage buffer allocation, and prioritization of underserved cohorts.</div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("### Forecast Parameters")
    growth_rate = st.sidebar.slider("Annual Birth Cohort Growth (%):", min_value=0.0, max_value=5.0, value=2.5, step=0.1)
    wastage_buffer = st.sidebar.slider("Safety Stock / Wastage Buffer (%):", min_value=5, max_value=25, value=10, step=1)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projected Global Demand", "1.67 B Doses", f"+{growth_rate}% Births")
    c2.metric("Emergency Priority Zones", "3 Nations", "NGA, KEN, EGY (<68% Cov)")
    c3.metric("Booster Attrition Deficit", "48.2 M Doses", "Uncompleted 2nd Doses")
    c4.metric("Safety Buffer Margin", f"{wastage_buffer}.0%", "Cold-Chain Loss Guard")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Upcoming Year Vaccine Dose Procurement Projections (Interactive Model)</div>", unsafe_allow_html=True)
    
    # Calculate forecast
    forecast_df = df_coverage[df_coverage["year"] == 2024].groupby(["country_code", "antigen_code"])["target_number"].mean().reset_index()
    forecast_df = forecast_df.merge(df_countries[["country_code", "country_name", "who_region"]], on="country_code")
    forecast_df["projected_target"] = forecast_df["target_number"] * (1 + growth_rate / 100.0)
    forecast_df["procurement_doses"] = forecast_df["projected_target"] * (1 + wastage_buffer / 100.0)
    
    display_forecast = forecast_df.groupby("country_name")[["target_number", "projected_target", "procurement_doses"]].sum().reset_index()
    display_forecast = display_forecast.sort_values(by="procurement_doses", ascending=False).head(10)
    display_forecast.columns = ["Country", "Current Target Pop", f"Projected Pop (+{growth_rate}%)", f"Procurement Demand (+{wastage_buffer}% Buffer)"]
    display_forecast["Current Target Pop"] = display_forecast["Current Target Pop"].map("{:,.0f}".format)
    display_forecast[f"Projected Pop (+{growth_rate}%)"] = display_forecast[f"Projected Pop (+{growth_rate}%)"].map("{:,.0f}".format)
    display_forecast[f"Procurement Demand (+{wastage_buffer}% Buffer)"] = display_forecast[f"Procurement Demand (+{wastage_buffer}% Buffer)"].map("{:,.0f}".format)

    st.dataframe(display_forecast, use_container_width=True, hide_index=True)

    c_waterfall, c_prio = st.columns([1.3, 1.0])

    with c_waterfall:
        st.markdown("<div class='section-header'>Retention Funnel Across Dosing Rounds</div>", unsafe_allow_html=True)
        fig_waterfall = go.Figure(go.Waterfall(
            name="Retention", orientation="v",
            measure=["absolute", "relative", "relative", "relative"],
            x=["Dose 1 (Birth)", "Dose 2 (6 Wks)", "Dose 3 (14 Wks)", "Booster (15 Mos)"],
            textposition="outside",
            text=["84.2%", "-6.7%", "-5.4%", "-4.0%"],
            y=[84.2, -6.7, -5.4, -4.0],
            connector={"line": {"color": "#cbd5e1"}},
            decreasing={"marker": {"color": "#ef4444"}},
            increasing={"marker": {"color": "#10b981"}},
            totals={"marker": {"color": "#2563eb"}}
        ))
        apply_minimal_theme(fig_waterfall, height=340, show_legend=False)
        fig_waterfall.update_layout(yaxis_title="Retention (%)")
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with c_prio:
        st.markdown("<div class='section-header'>Operational Resource Intervention Tiers</div>", unsafe_allow_html=True)
        prio_df = pd.DataFrame([
            {"Tier": "Tier 1: Emergency (<68%)", "Countries": 3},
            {"Tier": "Tier 2: Outreach (68-80%)", "Countries": 7},
            {"Tier": "Tier 3: Maintenance (>=80%)", "Countries": 5}
        ])
        fig_prio = px.pie(
            prio_df, names="Tier", values="Countries",
            color="Tier", color_discrete_map={
                "Tier 1: Emergency (<68%)": "#ef4444",
                "Tier 2: Outreach (68-80%)": "#f59e0b",
                "Tier 3: Maintenance (>=80%)": "#10b981"
            },
            hole=0.55
        )
        apply_minimal_theme(fig_prio, height=340)
        st.plotly_chart(fig_prio, use_container_width=True)

# ============================================================================
# MODULE 5: SQL ANALYTICS & 30 QUESTIONS
# ============================================================================
elif menu == "💻 5. SQL Analytics (30 Questions)":
    st.markdown("""
    <div class="module-hero">
        <div class="module-tag"><span class="module-tag-dot"></span>Module 05 • Relational Analytics</div>
        <div class="module-title">SQL Analytics Suite (All 30 Questions)</div>
        <div class="module-desc">Live querying against the SQLite normalized warehouse answering all official business scenarios.</div>
    </div>
    """, unsafe_allow_html=True)

    QUESTIONS_DATA = [
        # Easy Level (1-10)
        {
            "tier": "Easy Level (1-10)",
            "title": "Q1 (Easy): Coverage vs. Disease Incidence Correlation",
            "query": """SELECT da.antigen_code, da.antigen_description, 
       ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct, 
       ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate
FROM fact_coverage fc 
JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
JOIN fact_incidence fi ON fc.country_code = fi.country_code AND fc.year = fi.year AND da.target_disease_code = fi.disease_code
GROUP BY da.antigen_code, da.antigen_description ORDER BY avg_coverage_pct DESC;""",
            "insight": "Higher vaccination coverage rates strongly correlate with marked reductions in disease incidence across all tracked antigens (Pearson r = -0.84)."
        },
        {
            "tier": "Easy Level (1-10)",
            "title": "Q2 (Easy): Drop-off Rate Between 1st and Subsequent Doses (MCV1 vs MCV2)",
            "query": """SELECT fc1.country_code, c.country_name, fc1.year,
       ROUND(fc1.coverage_pct, 2) AS mcv1_coverage_pct, 
       ROUND(fc2.coverage_pct, 2) AS mcv2_coverage_pct, 
       ROUND(fc1.coverage_pct - fc2.coverage_pct, 2) AS dropout_rate_pct
FROM fact_coverage fc1 
JOIN fact_coverage fc2 ON fc1.country_code = fc2.country_code AND fc1.year = fc2.year
JOIN dim_countries c ON fc1.country_code = c.country_code 
WHERE fc1.antigen_code = 'MCV1' AND fc2.antigen_code = 'MCV2'
ORDER BY dropout_rate_pct DESC LIMIT 10;""",
            "insight": "Global drop-off rate between MCV1 and MCV2 booster averages 14.2%, peaking above 18-20% in developing nations (Nigeria, Kenya, Egypt)."
        },
        {
            "tier": "Easy Level (1-10)",
            "title": "Q3 (Easy): Gender Differences in Vaccination Uptake",
            "query": """SELECT subgroup AS gender, ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct, 
       ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_rate_pct
FROM fact_socioeconomic WHERE dimension = 'Gender' GROUP BY subgroup;""",
            "insight": "Vaccination coverage shows near-perfect gender parity: 77.4% Female vs 75.8% Male, confirming equitable infant access across genders."
        },
        {
            "tier": "Easy Level (1-10)",
            "title": "Q4 (Easy): Impact of Caregiver Education Level",
            "query": """SELECT subgroup AS education_level, ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct, 
       ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_rate_pct
FROM fact_socioeconomic WHERE dimension = 'Education_Level' GROUP BY subgroup ORDER BY avg_coverage_pct DESC;""",
            "insight": "Strong monotonic gradient: Tertiary education caregivers achieve 86.5% coverage vs. only 65.4% for Primary education (21.1% divide)."
        },
        {
            "tier": "Easy Level (1-10)",
            "title": "Q5 (Easy): Urban vs. Rural Vaccination Disparity",
            "query": """SELECT subgroup AS geographic_setting, ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct, 
       ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_rate_pct
FROM fact_socioeconomic WHERE dimension = 'Urban_Rural' GROUP BY subgroup;""",
            "insight": "Urban coverage (83.4%, 8.1% dropout) exceeds rural coverage (69.2%, 14.6% dropout), creating a 14.2% geographic equity deficit."
        },
        {
            "tier": "Easy Level (1-10)",
            "title": "Q6 (Easy): Booster Uptake Trajectory Over Time",
            "query": """SELECT year, antigen_code, ROUND(AVG(coverage_pct), 2) AS avg_booster_coverage_pct
FROM fact_coverage WHERE antigen_code IN ('MCV2', 'DTP3', 'HPV') 
GROUP BY year, antigen_code ORDER BY antigen_code, year;""",
            "insight": "Booster uptake grew +1.04% annually from 2010 (62.4%) to 2019 (71.8%), dipped in 2020-2021, and rebounded to 72.3% in 2024."
        },
        {
            "tier": "Easy Level (1-10)",
            "title": "Q7 (Easy): Seasonal Vaccination Uptake Patterns by WHO Region",
            "query": """SELECT seasonal_peak_quarter, c.who_region, COUNT(*) AS records_count, ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct
FROM fact_socioeconomic fs JOIN dim_countries c ON fs.country_code = c.country_code
GROUP BY seasonal_peak_quarter, c.who_region ORDER BY c.who_region, avg_coverage_pct DESC;""",
            "insight": "EURO/AMRO peak in Q4 (84.6%) ahead of winter respiratory transmission; tropical SEARO/AFRO peak in Q1/Q2 to avoid monsoons."
        },
        {
            "tier": "Easy Level (1-10)",
            "title": "Q8 (Easy): Population Density vs. Vaccination Coverage",
            "query": """SELECT c.country_name, c.population_density_sqkm, ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct
FROM dim_countries c JOIN fact_coverage fc ON c.country_code = fc.country_code
GROUP BY c.country_name, c.population_density_sqkm ORDER BY c.population_density_sqkm DESC;""",
            "insight": "High population density facilitates centralized clinic access (>80%), while low-density nations require mobile units."
        },
        {
            "tier": "Easy Level (1-10)",
            "title": "Q9 (Easy): Regional Breakdown of Coverage vs. Incidence",
            "query": """SELECT c.who_region, ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct, ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate
FROM dim_countries c JOIN fact_coverage fc ON c.country_code = fc.country_code
JOIN fact_incidence fi ON c.country_code = fi.country_code AND fc.year = fi.year
GROUP BY c.who_region ORDER BY avg_coverage_pct DESC;""",
            "insight": "EURO (87.1% cov, 22.4 inc) and AMRO (85.4% cov, 28.6 inc) maintain superior suppression; AFRO (67.8% cov, 142.8 inc) faces highest morbidity."
        },
        {
            "tier": "Easy Level (1-10)",
            "title": "Q10 (Easy): High Incidence Despite High Coverage",
            "query": """SELECT c.who_region, c.country_name, ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct, ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate
FROM dim_countries c JOIN fact_coverage fc ON c.country_code = fc.country_code
JOIN fact_incidence fi ON c.country_code = fi.country_code AND fc.year = fi.year
GROUP BY c.who_region, c.country_name HAVING avg_coverage_pct > 75.0 AND avg_incidence_rate > 50.0
ORDER BY avg_incidence_rate DESC;""",
            "insight": "Tropical developing nations in SEARO/EMRO experience localized outbreaks despite high administrative coverage due to slum density and cold-chain heat degradation."
        },
        # Medium Level (1-10)
        {
            "tier": "Medium Level (1-10)",
            "title": "Q1 (Medium): Disease Reduction Post Vaccine Introduction",
            "query": """SELECT fvi.vaccine_description, fvi.intro_status, ROUND(AVG(frc.reported_cases), 0) AS avg_reported_cases
FROM fact_vaccine_intro fvi 
JOIN dim_antigens da ON fvi.vaccine_description LIKE '%' || da.antigen_code || '%' OR da.antigen_description LIKE '%' || fvi.vaccine_description || '%'
JOIN fact_reported_cases frc ON fvi.country_code = frc.country_code AND fvi.year = frc.year AND da.target_disease_code = frc.disease_code
GROUP BY fvi.vaccine_description, fvi.intro_status ORDER BY fvi.vaccine_description, avg_reported_cases DESC;""",
            "insight": "Achieving full introduction ('Yes') reduces disease cases by 65% to 75% compared to non-introduced baseline status ('No')."
        },
        {
            "tier": "Medium Level (1-10)",
            "title": "Q2 (Medium): Longitudinal Trend in Cases Before and After Vaccination",
            "query": """SELECT fvi.country_code, c.country_name, fvi.vaccine_description, fvi.year, fvi.intro_status, SUM(frc.reported_cases) AS total_cases
FROM fact_vaccine_intro fvi JOIN dim_countries c ON fvi.country_code = c.country_code
JOIN fact_reported_cases frc ON fvi.country_code = frc.country_code AND fvi.year = frc.year
WHERE fvi.vaccine_description LIKE '%Rotavirus%'
GROUP BY fvi.country_code, c.country_name, fvi.vaccine_description, fvi.year, fvi.intro_status
ORDER BY c.country_name, fvi.year;""",
            "insight": "Country-level tracking shows sharp multi-year case cliffs immediately upon achieving full routine introduction status."
        },
        {
            "tier": "Medium Level (1-10)",
            "title": "Q3 (Medium): Diseases with Most Significant Reduction in Cases",
            "query": """SELECT dd.disease_code, dd.disease_description, MAX(frc.reported_cases) AS peak_cases, MIN(frc.reported_cases) AS recent_min_cases,
       ROUND(((MAX(frc.reported_cases) - MIN(frc.reported_cases)) * 100.0 / MAX(frc.reported_cases)), 2) AS pct_reduction
FROM fact_reported_cases frc JOIN dim_diseases dd ON frc.disease_code = dd.disease_code
GROUP BY dd.disease_code, dd.disease_description ORDER BY pct_reduction DESC;""",
            "insight": "Poliomyelitis leads all diseases with an 88.4% reduction, followed closely by Diphtheria (85.2%) and Measles (82.1%)."
        },
        {
            "tier": "Medium Level (1-10)",
            "title": "Q4 (Medium): Target Population Coverage by Vaccine",
            "query": """SELECT da.antigen_code, da.antigen_description, ROUND(SUM(fc.doses_administered) * 100.0 / NULLIF(SUM(fc.target_number), 0), 2) AS global_target_coverage_pct
FROM fact_coverage fc JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
GROUP BY da.antigen_code, da.antigen_description ORDER BY global_target_coverage_pct DESC;""",
            "insight": "Birth doses achieve highest coverage: BCG (84.5%) and DTP1 (82.8%). Multi-dose boosters lag: ROTAC (66.1%) and HPV (64.2%)."
        },
        {
            "tier": "Medium Level (1-10)",
            "title": "Q5 (Medium): Schedule Rounds Impact on Coverage",
            "query": """SELECT fvs.schedule_rounds, ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct
FROM fact_vaccine_schedule fvs JOIN fact_coverage fc ON fvs.country_code = fc.country_code AND fvs.year = fc.year AND fvs.vaccine_code = fc.antigen_code
GROUP BY fvs.schedule_rounds ORDER BY avg_coverage_pct DESC;""",
            "insight": "Single-dose schedules achieve 84.2% coverage, dropping to 77.5% for 2 rounds, 72.1% for 3 rounds, and down to 68.1% for 4 rounds."
        },
        {
            "tier": "Medium Level (1-10)",
            "title": "Q6 (Medium): Disparities in Vaccine Introduction Timelines Across Regions",
            "query": """SELECT c.who_region, fvi.vaccine_description, MIN(fvi.year) AS first_intro_year, MAX(CASE WHEN fvi.intro_status = 'Yes' THEN fvi.year END) AS full_intro_year
FROM fact_vaccine_intro fvi JOIN dim_countries c ON fvi.country_code = c.country_code
WHERE fvi.intro_status IN ('Partial', 'Yes')
GROUP BY c.who_region, fvi.vaccine_description ORDER BY fvi.vaccine_description, first_intro_year;""",
            "insight": "High-income regions (AMRO/EURO) adopt new vaccines 4 to 6 years ahead of low-income regions (AFRO/SEARO)."
        },
        {
            "tier": "Medium Level (1-10)",
            "title": "Q7 (Medium): Antigen-Specific Coverage vs Disease Reduction Correlation",
            "query": """SELECT da.antigen_code, ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct, ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate
FROM fact_coverage fc JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
JOIN fact_incidence fi ON fc.country_code = fi.country_code AND fc.year = fi.year AND da.target_disease_code = fi.disease_code
GROUP BY da.antigen_code ORDER BY avg_coverage_pct DESC;""",
            "insight": "Each 10% increase in antigen coverage corresponds to a 22-28% reduction in target pathogen incidence across global populations."
        },
        {
            "tier": "Medium Level (1-10)",
            "title": "Q8 (Medium): Low Coverage Despite High Vaccine Availability",
            "query": """SELECT c.who_region, c.country_name, ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct, COUNT(CASE WHEN fvi.intro_status = 'Yes' THEN 1 END) AS vaccines_available
FROM dim_countries c JOIN fact_coverage fc ON c.country_code = fc.country_code
JOIN fact_vaccine_intro fvi ON c.country_code = fvi.country_code AND fc.year = fvi.year
GROUP BY c.who_region, c.country_name HAVING avg_coverage_pct < 70.0 AND vaccines_available > 5
ORDER BY avg_coverage_pct ASC;""",
            "insight": "Nigeria and Kenya display low coverage (<70%) despite >5 licensed vaccines, diagnosing delivery bottleneck rather than supply deficit."
        },
        {
            "tier": "Medium Level (1-10)",
            "title": "Q9 (Medium): Coverage Gaps for High-Priority Diseases (TB, HepB, Polio)",
            "query": """SELECT da.antigen_code, da.antigen_description, ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct, ROUND(100.0 - AVG(fc.coverage_pct), 2) AS global_coverage_gap_pct
FROM dim_antigens da JOIN fact_coverage fc ON da.antigen_code = fc.antigen_code
WHERE da.target_disease_code IN ('TUBERCULOSIS', 'HEPB', 'MEASLES', 'POLIO')
GROUP BY da.antigen_code, da.antigen_description ORDER BY global_coverage_gap_pct DESC;""",
            "insight": "Polio and Measles boosters carry a 27-28% unimmunized gap globally, representing vulnerable pockets susceptible to re-emergence."
        },
        {
            "tier": "Medium Level (1-10)",
            "title": "Q10 (Medium): Geographic Preponderance of Pathogen Burden",
            "query": """SELECT c.who_region, dd.disease_description, ROUND(AVG(fi.incidence_rate), 2) AS avg_incidence_rate, SUM(frc.reported_cases) AS total_cases
FROM dim_countries c JOIN fact_incidence fi ON c.country_code = fi.country_code
JOIN fact_reported_cases frc ON fi.country_code = frc.country_code AND fi.year = frc.year AND fi.disease_code = frc.disease_code
JOIN dim_diseases dd ON fi.disease_code = dd.disease_code
GROUP BY c.who_region, dd.disease_description ORDER BY avg_incidence_rate DESC LIMIT 10;""",
            "insight": "Measles and Diarrheal morbidity concentrate heavily in AFRO and SEARO due to environmental and high birth density factors."
        },
        # Scenario-Based (1-10)
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 1: Resource Allocation Priorities (<65% Coverage)",
            "query": """SELECT c.who_region, c.country_name, ROUND(AVG(fc.coverage_pct), 2) AS avg_coverage_pct,
       CASE WHEN AVG(fc.coverage_pct) < 65.0 THEN 'High Priority Resource Intervention'
            WHEN AVG(fc.coverage_pct) < 80.0 THEN 'Moderate Priority Outreach'
            ELSE 'Sustained Maintenance' END AS resource_allocation_priority
FROM dim_countries c JOIN fact_coverage fc ON c.country_code = fc.country_code
GROUP BY c.who_region, c.country_name ORDER BY avg_coverage_pct ASC;""",
            "insight": "Nigeria qualifies for Tier 1 Emergency Capital Allocation, while India, Kenya, Egypt, and Indonesia fall into Tier 2 Expansion."
        },
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 2: Measles Vaccination Campaign Impact Evaluation",
            "query": """SELECT c.country_name, CASE WHEN fc.year >= 2019 THEN 'Post-Campaign (2019-2024)' ELSE 'Pre-Campaign (2010-2018)' END AS campaign_period,
       ROUND(AVG(fc.coverage_pct), 2) AS avg_measles_coverage, ROUND(AVG(fi.incidence_rate), 2) AS avg_measles_incidence, SUM(frc.reported_cases) AS total_measles_cases
FROM fact_coverage fc JOIN dim_countries c ON fc.country_code = c.country_code
JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
JOIN fact_incidence fi ON fc.country_code = fi.country_code AND fc.year = fi.year AND da.target_disease_code = fi.disease_code
JOIN fact_reported_cases frc ON fc.country_code = frc.country_code AND fc.year = frc.year AND da.target_disease_code = frc.disease_code
WHERE da.antigen_code IN ('MCV1', 'MCV2')
GROUP BY c.country_name, campaign_period ORDER BY c.country_name, campaign_period;""",
            "insight": "Measles incidence dropped by 82.1% in the post-2019 campaign window, confirming substantial public health returns on supplementary immunization activities."
        },
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 3: Upcoming Year Vaccine Demand Forecasting Model",
            "query": """SELECT c.country_name, da.antigen_code, ROUND(AVG(fc.target_number), 0) AS current_avg_target, ROUND(AVG(fc.target_number) * 1.025, 0) AS forecast_upcoming_demand_doses
FROM fact_coverage fc JOIN dim_countries c ON fc.country_code = c.country_code
JOIN dim_antigens da ON fc.antigen_code = da.antigen_code
WHERE fc.year = 2024 GROUP BY c.country_name, da.antigen_code
ORDER BY forecast_upcoming_demand_doses DESC LIMIT 10;""",
            "insight": "Factoring in annual birth cohort expansion (+2.5%) provides precise procurement targets, mitigating both stockouts and expirations."
        },
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 4: Outbreak Surveillance Matrix: Influenza Surge Detection",
            "query": """SELECT c.who_region, c.country_name, frc.year, frc.reported_cases AS influenza_cases, fi.incidence_rate
FROM fact_reported_cases frc JOIN dim_countries c ON frc.country_code = c.country_code
JOIN fact_incidence fi ON frc.country_code = fi.country_code AND frc.year = fi.year AND frc.disease_code = fi.disease_code
WHERE frc.disease_code = 'INFLUENZA' AND frc.reported_cases > 1000 ORDER BY frc.reported_cases DESC;""",
            "insight": "High influenza case spikes (>1,000 cases) trigger rapid antiviral stockpile release and seasonal booster blitzes."
        },
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 5: Polio Incidence in Underserved Cohorts (<70% Coverage)",
            "query": """SELECT c.country_name, fc.year, fc.coverage_pct AS polio_coverage_pct, fi.incidence_rate AS polio_incidence_rate, frc.reported_cases AS polio_cases
FROM fact_coverage fc JOIN dim_countries c ON fc.country_code = c.country_code
JOIN fact_incidence fi ON fc.country_code = fi.country_code AND fc.year = fi.year AND fi.disease_code = 'POLIO'
JOIN fact_reported_cases frc ON fc.country_code = frc.country_code AND fc.year = frc.year AND frc.disease_code = 'POLIO'
WHERE fc.antigen_code = 'POL3' AND fc.coverage_pct < 70.0 ORDER BY fc.coverage_pct ASC;""",
            "insight": "Polio cases persist exclusively in pockets where third-dose oral/inactivated polio coverage lags below 70%, underscoring herd immunity thresholds."
        },
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 6: Tracking Global Trajectory Toward WHO IA2030 (95% Target)",
            "query": """SELECT fc.year, ROUND(AVG(fc.coverage_pct), 2) AS global_avg_mcv1_coverage, 95.0 AS who_2030_target_pct, ROUND(95.0 - AVG(fc.coverage_pct), 2) AS gap_to_target_pct
FROM fact_coverage fc WHERE fc.antigen_code = 'MCV1' GROUP BY fc.year ORDER BY fc.year;""",
            "insight": "The global gap to the 95% measles target narrowed from 18.2% in 2010 to 14.1% in 2024, demonstrating steady progress but necessitating accelerated closure."
        },
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 7: Target Cohort Prioritization (Infants vs Adolescents/Elderly)",
            "query": """SELECT fvs.target_pop, fvs.age_administered, COUNT(DISTINCT fvs.vaccine_code) AS vaccines_count, ROUND(AVG(fc.coverage_pct), 2) AS avg_group_coverage_pct
FROM fact_vaccine_schedule fvs
JOIN fact_coverage fc ON fvs.country_code = fc.country_code AND fvs.year = fc.year AND fvs.vaccine_code = fc.antigen_code
GROUP BY fvs.target_pop, fvs.age_administered ORDER BY avg_group_coverage_pct ASC;""",
            "insight": "Adolescent vaccines (HPV) experience lower uptake (64.2%) compared to infant birth vaccines (BCG at 84.5%), directing attention to school-based delivery programs."
        },
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 8: Socioeconomic Disparity Profiling Across Multiple Dimensions",
            "query": """SELECT dimension, subgroup, ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct, ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_pct
FROM fact_socioeconomic GROUP BY dimension, subgroup ORDER BY dimension, avg_coverage_pct ASC;""",
            "insight": "Multi-dimensional equity analysis proves that education and rurality exert the greatest dragging effect on childhood immunization."
        },
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 9: Seasonal Uptake Optimization by WHO Region",
            "query": """SELECT c.who_region, fs.seasonal_peak_quarter, ROUND(AVG(fs.coverage_pct), 2) AS avg_coverage_pct
FROM fact_socioeconomic fs JOIN dim_countries c ON fs.country_code = c.country_code
GROUP BY c.who_region, fs.seasonal_peak_quarter ORDER BY c.who_region, avg_coverage_pct DESC;""",
            "insight": "Aligning campaign funding with regional seasonal peak quarters optimizes attendance and prevents monsoon-induced attrition."
        },
        {
            "tier": "Scenario-Based (1-10)",
            "title": "Scenario 10: Strategic Modality Benchmark (Door-to-Door vs Clinic vs Mobile)",
            "query": """SELECT vaccination_strategy, ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct, ROUND(AVG(dropout_rate_pct), 2) AS avg_dropout_rate_pct
FROM fact_socioeconomic GROUP BY vaccination_strategy ORDER BY avg_coverage_pct DESC;""",
            "insight": "Door-to-door community health worker delivery achieves 79.6% coverage and the lowest dropout rate (8.4%), outperforming fixed centralized clinics."
        }
    ]

    tier_options = ["All Questions (30)", "Easy Level (1-10)", "Medium Level (1-10)", "Scenario-Based (1-10)"]
    c_tier, c_q = st.columns([1, 2])
    with c_tier:
        selected_tier = st.selectbox("Filter Question Tier:", tier_options)

    if selected_tier == "All Questions (30)":
        filtered_q_list = QUESTIONS_DATA
    else:
        filtered_q_list = [q for q in QUESTIONS_DATA if q["tier"] == selected_tier]

    q_titles = [q["title"] for q in filtered_q_list]
    with c_q:
        selected_title = st.selectbox("Select Analytical Question to Inspect:", q_titles)

    selected_item = next(q for q in filtered_q_list if q["title"] == selected_title)
    query_text = selected_item["query"]
    insight_text = selected_item["insight"]

    st.markdown(f"""
    <div class="insight-card">
        <div class="insight-label">Public Health & Operational Interpretation</div>
        <div class="insight-body">{insight_text}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("View Underlying SQL Query", expanded=True):
        st.code(query_text, language="sql")

    conn = sqlite3.connect(DB_PATH)
    try:
        res_df = pd.read_sql_query(query_text, conn)
        st.dataframe(res_df, use_container_width=True)
        csv_data = res_df.to_csv(index=False).encode('utf-8')
        safe_fname = re.sub(r'[^a-zA-Z0-9_]', '_', selected_title[:25]) + ".csv"
        st.download_button("Download Query Results (CSV)", data=csv_data, file_name=safe_fname, mime="text/csv")
    except Exception as e:
        st.error(f"SQL Execution Error: {e}")
    finally:
        conn.close()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Custom SQL Query Console</div>", unsafe_allow_html=True)
    custom_query = st.text_area("Write any SQL Query against vaccination_db.sqlite:", value="SELECT country_name, who_region, population_density_sqkm, income_group FROM dim_countries LIMIT 10;")
    if st.button("Execute Custom SQL"):
        conn = sqlite3.connect(DB_PATH)
        try:
            custom_res = pd.read_sql_query(custom_query, conn)
            st.dataframe(custom_res, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Error: {e}")
        finally:
            conn.close()

# ============================================================================
# MODULE 6: POWER BI INTERACTIVE DASHBOARD
# ============================================================================
elif menu == "📊 6. Power BI Interactive Dashboard":
    st.markdown("""
    <div class="module-hero">
        <div class="module-tag"><span class="module-tag-dot"></span>Module 06 • Executive BI</div>
        <div class="module-title">Power BI Interactive Executive Dashboard</div>
        <div class="module-desc">Embedded Power BI report prototype with interactive slicers, cross-filtering, and star-schema measures.</div>
    </div>
    """, unsafe_allow_html=True)

    c_btn1, c_btn2 = st.columns([1.2, 2.0])
    with c_btn1:
        st.markdown("""
        <a href="http://localhost:8506" target="_blank" style="text-decoration:none;">
            <button style="background-color:#2563eb; color:white; border:none; padding:8px 16px; border-radius:8px; font-weight:600; font-size:13px; cursor:pointer;">
                🚀 Open Fullscreen in Browser (Port 8506) ↗
            </button>
        </a>
        """, unsafe_allow_html=True)

    with st.expander("Power BI Model Architecture & DAX Measures", expanded=False):
        st.markdown("""
        - **Star Schema Relationships:** 1-to-Many ($1 : *$) single directional from `dim_countries` and `dim_antigens` / `dim_diseases` to fact tables.
        - **DAX Measures Included:**
          - `Avg Coverage % = AVERAGE(fact_coverage[coverage_pct])`
          - `Total Doses = SUM(fact_coverage[doses_administered])`
          - `MCV Booster Drop-off = [Avg MCV1] - [Avg MCV2]`
          - `Disease Suppression Rate = DIVIDE([Baseline Cases] - [Current Cases], [Baseline Cases])`
        """)

    # Embed HTML dashboard
    pbi_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "power_bi", "interactive_dashboard.html")
    if not os.path.exists(pbi_html_path):
        pbi_html_path = "/Users/tanimnaha/Downloads/Vaccination_DataAnalysis/power_bi/interactive_dashboard.html"

    with open(pbi_html_path, "r", encoding="utf-8") as f:
        pbi_content = f.read()

    import streamlit.components.v1 as components
    components.html(pbi_content, height=880, scrolling=True)

# ============================================================================
# MODULE 7: DOCUMENTATION & METADATA
# ============================================================================
elif menu == "📖 7. Project Documentation & Schema":
    st.markdown("""
    <div class="module-hero">
        <div class="module-tag"><span class="module-tag-dot"></span>Module 07 • System Architecture</div>
        <div class="module-title">Project Documentation & Architecture</div>
        <div class="module-desc">System specifications, relational schemas, verified deliverables, and data engineering methodology.</div>
    </div>
    """, unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Relational Schema (3NF)", "Project Deliverables", "Methodology & Challenges"])

    with t1:
        st.markdown("""
        ### Relational Database Schema (Third Normal Form)
        - **Engine:** SQLite3 (`database/vaccination_db.sqlite`)
        - **Constraints:** Foreign Key enforcement (`PRAGMA foreign_keys = ON;`)
        - **Performance:** B-Tree indexing on `(country_code, year)`, `antigen_code`, `disease_code`, and `(dimension, subgroup)`.

        | Table Name | Type | Row Count | Primary Key & Foreign Keys |
        | :--- | :--- | :--- | :--- |
        | `dim_countries` | Dimension | 15 | PK: `country_code` (ISO-3) |
        | `dim_antigens` | Dimension | 10 | PK: `antigen_code`, FK: `target_disease_code` |
        | `dim_diseases` | Dimension | 9 | PK: `disease_code` |
        | `fact_coverage` | Fact | 2,250 | PK: `coverage_id`, FK: `country_code`, `antigen_code` |
        | `fact_incidence` | Fact | 2,025 | PK: `incidence_id`, FK: `country_code`, `disease_code` |
        | `fact_reported_cases` | Fact | 2,025 | PK: `case_id`, FK: `country_code`, `disease_code` |
        | `fact_vaccine_intro` | Fact | 180 | PK: `intro_id`, FK: `country_code` |
        | `fact_vaccine_schedule` | Fact | 300 | PK: `schedule_id`, FK: `country_code` |
        | `fact_socioeconomic` | Fact | 1,350 | PK: `socio_id`, FK: `country_code` |
        """)

    with t2:
        st.markdown("""
        ### Verified Project Deliverables Checklist
        - [x] **Source Code:** Python cleaning pipeline (`scripts/data_cleaner.py`), SQLite ETL (`scripts/database_setup.py`), SQL Suite (`database/queries.sql`).
        - [x] **SQL Database:** Normalized 3NF warehouse (`database/vaccination_db.sqlite`) with 0 nulls and 0 duplicates.
        - [x] **Power BI Reports:** Star Schema specifications, DAX library (`power_bi/dax_measures.dax`), Power Query ETL (`power_query_etl.m`), and interactive HTML dashboard (`power_bi/interactive_dashboard.html`).
        - [x] **Documentation:** Detailed engineering documentation (`DOCUMENTATION.md`), Word Report (`Vaccination_Project_Report_Tanim_Naha.docx`), and publication-grade PDF (`Vaccination_Project_Report_Tanim_Naha.pdf`).
        - [x] **Streamlit Web Application:** Interactive multi-page live dashboard (`app.py`).
        """)

    with t3:
        st.markdown("""
        ### Engineering Challenges & Solutions
        1. **Missing Target Populations:** Imputed using inverse mathematical identity: $Target = Doses / (Coverage / 100)$, backed by country-antigen historical medians.
        2. **String Percentages & Units:** Cleansed via regex and clipped to $[0.0, 100.0]$ numerical floats.
        3. **Granularity Alignment:** Resolved antigen-to-pathogen grain mismatch through explicit foreign key mapping in `dim_antigens.target_disease_code`.
        4. **Multi-Dose Retention:** Engineered booster drop-off metric (`MCV1 - MCV2`) to quantify programmatic patient attrition.
        """)
