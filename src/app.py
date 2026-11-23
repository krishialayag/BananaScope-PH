"""
BananaScope PH: Philippine Banana Production Analytics (2010–2026)
------------------------------------------------------------------
Main Interactive Web Application & Advanced Analytics Engine
Built with Streamlit & Plotly Express.

Visual Identity: 6-Color Botanical Blossom Palette (Balanced & Equal Spread)
Official Color Palette:
  • Peach Blush   (#F8D1C5) - Cultivar & KPI accents, growth contraction, Home Nav
  • Sunlit Cream  (#FFF3C7) - Hero banner, Production Nav, seasonality metrics
  • Sage Mist     (#A7C4A0) - Regional Nav, boom years, Bungulan variety
  • Aqua Breeze   (#7FC4C3) - Trajectory line, Varieties Nav, Cavendish variety
  • Cloud Blue    (#A7B7E5) - Lacatan variety, Trends Nav, historical benchmarks
  • Lavender Haze (#C9B4E6) - Records Nav, Holt's forecast projections, footer border

Responsive Navigation:
  • Left Sidebar: Classic Streamlit Neumorphic Sidebar Navigation Menu & Multi-Attribute Filters

Developed for Fundamentals of Data Analytics
Leuteboro National High School (DepEd MIMAROPA, Oriental Mindoro)
Supervised by Sir Aldrin D. Magtibay, Teacher V

Research Team:
  1. Krishia Mae R. Layag (Project Lead & Data Pipeline Engineer)
  2. Ann Ehra V. Avelino (Dashboard & UI/UX Design Lead)
  3. Hannah Aeshell V. Perez (Data Analytics & Documentation Lead)
"""

import os
import base64
import re
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Import Advanced Analytics Engine (PRESERVED 100%)
from analytics_engine import (
    compute_yoy_growth,
    calculate_cagr,
    compute_trend_models,
    detect_statistical_anomalies,
    run_time_series_forecast
)

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & 4-COLOR PALETTE SYSTEM
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BananaScope PH | Philippine Banana Analytics",
    page_icon="🍌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Canonical 6 Analytical Categories
CATEGORIES = [
    {"id": "HOME", "title": "Home", "icon": "🏠", "desc": "Main dashboard and KPI overview"},
    {"id": "PROD", "title": "Production", "icon": "📈", "desc": "Production Overview and Seasonality"},
    {"id": "REG", "title": "Regions", "icon": "🗺️", "desc": "Regional and Geographic Rankings"},
    {"id": "VAR", "title": "Varieties", "icon": "🍌", "desc": "Banana Variety Analysis"},
    {"id": "TREND", "title": "Trends", "icon": "📊", "desc": "Growth Rates, Trendlines and Forecasting"},
    {"id": "REC", "title": "Records", "icon": "📑", "desc": "Structured Tables and Methodology"}
]

# Canonical Sequence of All 13 Analytical Views (for sequential Next/Back buttons)
ALL_VIEWS_ORDER = [
    {"view": "ANNUAL_TRAJECTORY", "cat": "PROD", "sub": "TRAJECTORY", "title": "Annual Production Trajectory", "icon": "📈"},
    {"view": "QUARTERLY_SEASONALITY", "cat": "PROD", "sub": "SEASONALITY", "title": "Quarterly Harvest Patterns", "icon": "⏱️"},
    {"view": "REGIONAL_RANKINGS", "cat": "REG", "sub": "RANKINGS", "title": "Regional Production Comparison", "icon": "🗺️"},
    {"view": "CULTIVAR_DONUT", "cat": "VAR", "sub": "DONUT", "title": "Variety Market Share Breakdown", "icon": "🍌"},
    {"view": "VARIETY_COMPARISON", "cat": "VAR", "sub": "TRENDS", "title": "Multi-Year Harvest Trends by Variety", "icon": "🌿"},
    {"view": "YOY_GROWTH", "cat": "TREND", "sub": "YOY", "title": "Year-over-Year Percentage Growth", "icon": "📊"},
    {"view": "MOVING_AVERAGE", "cat": "TREND", "sub": "SMOOTH", "title": "3-Year Moving Average & Linear Trend", "icon": "🌾"},
    {"view": "ANOMALIES_SCATTER", "cat": "TREND", "sub": "ANOMALIES", "title": "Statistical Anomaly Detection (Z-Score)", "icon": "🔍"},
    {"view": "FORECAST_CHART", "cat": "TREND", "sub": "FORECAST", "title": "Exploratory Time-Series Forecast", "icon": "🔮"},
    {"view": "FORECAST_TABLE", "cat": "REC", "sub": "FC_TABLE", "title": "Projected Scenario Estimates Table", "icon": "📋"},
    {"view": "ANOMALIES_TABLE", "cat": "REC", "sub": "ANOM_TABLE", "title": "Summary Table of Flagged Anomaly Years", "icon": "⚠️"},
    {"view": "RECORDS_TABLE", "cat": "REC", "sub": "RECORDS", "title": "Official Production Records Explorer", "icon": "📑"},
    {"view": "MATH_METHODOLOGY", "cat": "REC", "sub": "MATH", "title": "Mathematical Formulations & Methodology", "icon": "📐"}
]

# Initialize Session State
if "active_category" not in st.session_state:
    st.session_state.active_category = "HOME"
if "prod_subview" not in st.session_state:
    st.session_state.prod_subview = "TRAJECTORY"
if "var_subview" not in st.session_state:
    st.session_state.var_subview = "DONUT"
if "trend_subview" not in st.session_state:
    st.session_state.trend_subview = "YOY"
if "rec_subview" not in st.session_state:
    st.session_state.rec_subview = "FC_TABLE"

def navigate_to(cat, sub=None):
    """Sets active navigation category and subview, then triggers rerun."""
    st.session_state.active_category = cat
    if cat == "PROD" and sub:
        st.session_state.prod_subview = sub
    elif cat == "VAR" and sub:
        st.session_state.var_subview = sub
    elif cat == "TREND" and sub:
        st.session_state.trend_subview = sub
    elif cat == "REC" and sub:
        st.session_state.rec_subview = sub
    st.rerun()

def get_base64_background(image_path="assets/banana_background.jpg"):
    """Reads and encodes local background image to base64."""
    candidate_paths = [
        image_path,
        os.path.join(os.path.dirname(__file__), "..", image_path),
        os.path.join(os.path.dirname(__file__), "assets", "banana_background.jpg"),
        r"C:\Users\Krisha Mae Layag\OneDrive\Desktop\Bananascope_PH\assets\banana_background.jpg",
        r"C:\Users\Krisha Mae Layag\OneDrive\Desktop\Bananascope_PH\assets\banana_leaves_watercolor.jpg",
        r"C:\Users\Krisha Mae Layag\.gemini\antigravity\brain\eb188fac-20d3-48f6-9f87-f78066eff7bb\.user_uploaded\media_1794964844953_1b10d6cd.jpg"
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return ""

BG_IMAGE_BASE64 = get_base64_background()

# -----------------------------------------------------------------------------
# CSS STYLESHEET: TACTILE BOTANICAL NEUMORPHISM (PRECISION SOFT UI SYSTEM)
# -----------------------------------------------------------------------------
CSS_STYLESHEET = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

    :root {
        /* Official 6-Color Botanical Blossom Palette */
        --peach-blush: #F8D1C5;
        --peach-blush-border: #E8AEA0;
        --peach-blush-dark: #3E1D16;
        --peach-blush-shadow: rgba(220, 160, 145, 0.40);

        --sunlit-cream: #FFF3C7;
        --sunlit-cream-border: #F0DA94;
        --sunlit-cream-dark: #3D3209;
        --sunlit-cream-shadow: rgba(215, 185, 110, 0.38);

        --sage-mist: #A7C4A0;
        --sage-mist-border: #80A878;
        --sage-mist-dark: #193815;
        --sage-mist-shadow: rgba(135, 170, 130, 0.40);

        --aqua-breeze: #7FC4C3;
        --aqua-breeze-border: #5AA8A7;
        --aqua-breeze-dark: #103838;
        --aqua-breeze-shadow: rgba(95, 165, 164, 0.40);

        --cloud-blue: #A7B7E5;
        --cloud-blue-border: #7F95DA;
        --cloud-blue-dark: #19274E;
        --cloud-blue-shadow: rgba(135, 155, 205, 0.42);

        --lavender-haze: #C9B4E6;
        --lavender-haze-border: #AC91D8;
        --lavender-haze-dark: #311B4C;
        --lavender-haze-shadow: rgba(175, 150, 205, 0.42);

        /* Neumorphic Base Canvas & Surfaces */
        --nm-bg: #EEF3EB;
        --nm-surface: #EFF4EC;
        --nm-surface-light: #F7FAF5;
        --nm-tray: #E4ECE0;
        --nm-socket: #DEE8DA;

        /* Neumorphic Dual Shadows (High-Precision 3D Extrusion & Recess) */
        --nm-light: #FFFFFF;
        --nm-shadow: rgba(135, 160, 125, 0.30);
        --nm-shadow-deep: rgba(120, 150, 110, 0.38);

        /* Elevation Presets */
        --nm-extruded-card: 8px 8px 20px var(--nm-shadow), -8px -8px 20px var(--nm-light);
        --nm-extruded-btn: 4px 4px 10px var(--nm-shadow), -4px -4px 10px var(--nm-light);
        --nm-hover: 8px 8px 22px rgba(120, 150, 110, 0.42), -8px -8px 22px #FFFFFF;
        --nm-recessed: inset 3px 3px 7px rgba(125, 150, 115, 0.30), inset -3px -3px 7px #FFFFFF;
        --nm-recessed-socket: inset 2px 2px 6px rgba(125, 150, 115, 0.28), inset -2px -2px 6px #FFFFFF;

        /* Deep High-Contrast Typography */
        --text-dark: #22331C;
        --text-body: #32462A;
        --text-muted: #5A7052;
        --nm-border: rgba(255, 255, 255, 0.90);
    }

    /* 1. Global Page Background: Soft Ceramic Neumorphic Canvas with Foliage Watermark */
    .stApp,
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(rgba(242, 246, 240, 0.90), rgba(230, 238, 226, 0.94)),
                    url("data:image/jpeg;base64,__BG_IMAGE_PLACEHOLDER__") center center / cover no-repeat fixed !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-dark) !important;
    }

    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .main {
        background-color: transparent !important;
        background: transparent !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Main Container Padding & Dimensions */
    .block-container {
        padding-top: 1.0rem !important;
        padding-bottom: 2.8rem !important;
        padding-left: 1.8rem !important;
        padding-right: 1.8rem !important;
        max-width: 1400px !important;
    }

    /* Smooth Fade-In Transition */
    @keyframes fadeInView {
        0% { opacity: 0; transform: translateY(4px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .fade-in-view {
        animation: fadeInView 0.22s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }

    /* ========================================================================= */
    /* 2. CLASSIC LEFT SIDEBAR: TACTILE NEUMORPHIC CONSOLE                       */
    /* ========================================================================= */
    [data-testid="stSidebar"] {
        background-color: var(--nm-surface) !important;
        background-image: linear-gradient(180deg, rgba(240, 245, 238, 0.98) 0%, rgba(228, 237, 224, 0.98) 100%) !important;
        border-right: 2px solid rgba(255, 255, 255, 0.95) !important;
        box-shadow: 6px 0 24px rgba(135, 160, 125, 0.28) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.2rem !important;
        padding-left: 1.0rem !important;
        padding-right: 1.0rem !important;
        padding-bottom: 2.5rem !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-dark) !important;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: var(--text-dark) !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] label {
        color: var(--text-dark) !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
    }

    /* Sidebar Brand Console Card (Sunlit Cream with Sage Accent) */
    .sidebar-brand-box {
        background: linear-gradient(135deg, #FFFDF5 0%, #FFF3C7 100%) !important;
        border-radius: 18px !important;
        box-shadow: 6px 6px 18px rgba(200, 175, 110, 0.32), -6px -6px 18px #FFFFFF !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-left: 6px solid var(--sage-mist) !important;
        padding: 14px 12px !important;
        margin-bottom: 16px !important;
    }
    .sidebar-brand-title {
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        color: #38240D !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        line-height: 1.2 !important;
    }
    .sidebar-brand-subtitle {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        color: #5C461E !important;
        margin-top: 4px !important;
        line-height: 1.35 !important;
    }
    .sidebar-tag {
        display: inline-block !important;
        margin-top: 8px !important;
        padding: 3px 10px !important;
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        border-radius: 20px !important;
        background: linear-gradient(135deg, #FDECE7 0%, #F8D1C5 100%) !important;
        color: #3E1D16 !important;
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.12), inset -1px -1px 3px #FFFFFF !important;
        border: 1px solid #E8AEA0 !important;
    }

    /* Sidebar Section Titles */
    .sidebar-section-title {
        font-size: 0.82rem !important;
        font-weight: 800 !important;
        color: var(--text-dark) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin: 14px 0 8px 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
    }

    /* Base Styling for Sidebar Navigation Buttons */
    div[class*="st-key-sb_nav_"] button {
        width: 100% !important;
        height: 44px !important;
        min-height: 44px !important;
        font-size: 0.84rem !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        padding: 8px 14px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
        margin-bottom: 7px !important;
        transition: all 0.20s cubic-bezier(0.25, 1, 0.5, 1) !important;
        box-sizing: border-box !important;
    }
    div[class*="st-key-sb_nav_"] button:hover {
        transform: translateY(-2px) !important;
    }

    /* 6-Color Dedicated Navigation Identity (Every Nav Box Has Its Own Palette Color) */
    /* 1. Home - Sunlit Cream */
    div[class*="st-key-sb_nav_HOME"] button {
        background: #FFFDF4 !important;
        border: 1.5px solid #F0DA94 !important;
        color: #4A3E0E !important;
        box-shadow: 3px 3px 8px rgba(215, 185, 110, 0.30), -3px -3px 8px #FFFFFF !important;
    }
    div[class*="st-key-sb_nav_HOME"] button[kind="primary"] {
        background: linear-gradient(135deg, #FFECA3 0%, #FFD85E 100%) !important;
        color: #38240D !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: inset 2px 2px 5px rgba(180, 140, 50, 0.30), 0 4px 14px rgba(220, 180, 80, 0.40) !important;
        font-weight: 800 !important;
    }

    /* 2. Production - Peach Blush */
    div[class*="st-key-sb_nav_PROD"] button {
        background: #FDF3EF !important;
        border: 1.5px solid #E8AEA0 !important;
        color: #4D2319 !important;
        box-shadow: 3px 3px 8px rgba(220, 160, 145, 0.30), -3px -3px 8px #FFFFFF !important;
    }
    div[class*="st-key-sb_nav_PROD"] button[kind="primary"] {
        background: linear-gradient(135deg, #F8C3B4 0%, #F3A894 100%) !important;
        color: #2E0F07 !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: inset 2px 2px 5px rgba(160, 80, 60, 0.30), 0 4px 14px rgba(240, 160, 140, 0.40) !important;
        font-weight: 800 !important;
    }

    /* 3. Regions - Sage Mist */
    div[class*="st-key-sb_nav_REG"] button {
        background: #F2F8F1 !important;
        border: 1.5px solid #80A878 !important;
        color: #1C3B18 !important;
        box-shadow: 3px 3px 8px rgba(135, 170, 130, 0.30), -3px -3px 8px #FFFFFF !important;
    }
    div[class*="st-key-sb_nav_REG"] button[kind="primary"] {
        background: linear-gradient(135deg, #99C092 0%, #7EAC74 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: inset 2px 2px 5px rgba(50, 80, 45, 0.30), 0 4px 14px rgba(120, 165, 110, 0.40) !important;
        font-weight: 800 !important;
    }

    /* 4. Varieties - Aqua Breeze */
    div[class*="st-key-sb_nav_VAR"] button {
        background: #EDF8F8 !important;
        border: 1.5px solid #5AA8A7 !important;
        color: #133E3E !important;
        box-shadow: 3px 3px 8px rgba(95, 165, 164, 0.30), -3px -3px 8px #FFFFFF !important;
    }
    div[class*="st-key-sb_nav_VAR"] button[kind="primary"] {
        background: linear-gradient(135deg, #74C0BF 0%, #51A8A7 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: inset 2px 2px 5px rgba(30, 75, 75, 0.30), 0 4px 14px rgba(95, 170, 168, 0.40) !important;
        font-weight: 800 !important;
    }

    /* 5. Trends - Cloud Blue */
    div[class*="st-key-sb_nav_TREND"] button {
        background: #F1F5FE !important;
        border: 1.5px solid #7F95DA !important;
        color: #1E2B56 !important;
        box-shadow: 3px 3px 8px rgba(135, 155, 205, 0.30), -3px -3px 8px #FFFFFF !important;
    }
    div[class*="st-key-sb_nav_TREND"] button[kind="primary"] {
        background: linear-gradient(135deg, #9DB0E5 0%, #7C94D9 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: inset 2px 2px 5px rgba(45, 60, 110, 0.30), 0 4px 14px rgba(135, 160, 215, 0.40) !important;
        font-weight: 800 !important;
    }

    /* 6. Records - Lavender Haze */
    div[class*="st-key-sb_nav_REC"] button {
        background: #F7F2FD !important;
        border: 1.5px solid #AC91D8 !important;
        color: #341C52 !important;
        box-shadow: 3px 3px 8px rgba(175, 150, 205, 0.30), -3px -3px 8px #FFFFFF !important;
    }
    div[class*="st-key-sb_nav_REC"] button[kind="primary"] {
        background: linear-gradient(135deg, #C2A8E5 0%, #A887D6 100%) !important;
        color: #FFFFFF !important;
        border: 2px solid #FFFFFF !important;
        box-shadow: inset 2px 2px 5px rgba(70, 45, 100, 0.30), 0 4px 14px rgba(175, 145, 215, 0.40) !important;
        font-weight: 800 !important;
    }

    /* Sidebar Filter Sockets */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #FFFDF8 !important;
        border: 1.5px solid #F0DA94 !important;
        border-radius: 12px !important;
        box-shadow: inset 2px 2px 5px rgba(180, 150, 90, 0.22), inset -2px -2px 5px #FFFFFF !important;
        color: var(--text-dark) !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] {
        background: #F4FAF8 !important;
        padding: 8px 12px !important;
        border-radius: 14px !important;
        box-shadow: inset 2px 2px 5px rgba(95, 165, 164, 0.22), inset -2px -2px 5px #FFFFFF !important;
        border: 1.5px solid #7FC4C3 !important;
        gap: 6px !important;
    }
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {
        padding-top: 10px !important;
    }

    /* Sidebar Footer Metadata Card (Lavender Haze) */
    .sidebar-footer-card {
        background: linear-gradient(135deg, #F6F1FC 0%, #C9B4E6 100%) !important;
        border-radius: 14px !important;
        border: 1.5px solid #AC91D8 !important;
        box-shadow: 4px 4px 14px rgba(175, 150, 205, 0.35), -4px -4px 14px #FFFFFF !important;
        padding: 10px 12px !important;
        margin-top: 18px !important;
        text-align: center !important;
    }

    /* ========================================================================= */
    /* 3. HERO BANNER & SURVEILLANCE OVERVIEW CARDS (COLORED NEUMORPHIC)          */
    /* ========================================================================= */
    .hero-banner {
        background: linear-gradient(135deg, #FFFDF5 0%, #FFF3C7 100%) !important;
        border-radius: 26px !important;
        box-shadow: 8px 8px 24px rgba(210, 185, 110, 0.35), -8px -8px 24px #FFFFFF !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-left: 7px solid #7FC4C3 !important;
        padding: 20px 24px !important;
        margin-bottom: 14px !important;
        transition: box-shadow 0.20s ease !important;
    }
    .dashboard-title {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: 2.15rem !important;
        font-weight: 700 !important;
        color: #38240D !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        letter-spacing: 0.2px !important;
        text-shadow: 0 1px 2px rgba(255, 255, 255, 0.8) !important;
    }
    .hero-subtitle {
        font-size: 0.88rem !important;
        color: #5C461E !important;
        margin: 4px 0 0 0 !important;
        font-weight: 600 !important;
    }
    .hero-badges-container {
        display: flex !important;
        gap: 8px !important;
        flex-wrap: wrap !important;
        margin-top: 10px !important;
    }
    .hero-pill-badge {
        display: inline-flex !important;
        align-items: center !important;
        gap: 5px !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        padding: 4px 12px !important;
        border-radius: 12px !important;
        box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.08), -2px -2px 6px rgba(255, 255, 255, 0.9) !important;
    }
    .badge-peach { background: #F8D1C5 !important; border: 1px solid #E8AEA0 !important; color: #3E1D16 !important; }
    .badge-cream { background: #FFF3C7 !important; border: 1px solid #F0DA94 !important; color: #3D3209 !important; }
    .badge-sage { background: #A7C4A0 !important; border: 1px solid #80A878 !important; color: #193815 !important; }
    .badge-aqua { background: #7FC4C3 !important; border: 1px solid #5AA8A7 !important; color: #103838 !important; }
    .badge-cloud { background: #A7B7E5 !important; border: 1px solid #7F95DA !important; color: #19274E !important; }
    .badge-lavender { background: #C9B4E6 !important; border: 1px solid #AC91D8 !important; color: #311B4C !important; }

    /* Surveillance / Insights Card (Sage Mist Neumorphic Box) */
    .insights-card {
        background: linear-gradient(135deg, #F1F8F0 0%, #A7C4A0 100%) !important;
        border-radius: 22px !important;
        box-shadow: 7px 7px 20px rgba(130, 165, 125, 0.35), -7px -7px 20px #FFFFFF !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-left: 6px solid #80A878 !important;
        padding: 16px 20px !important;
        margin: 12px 0 14px 0 !important;
    }
    .insights-title {
        font-size: 0.94rem !important;
        font-weight: 800 !important;
        color: #193815 !important;
        margin-bottom: 5px !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
    }
    .insights-body {
        font-size: 0.88rem !important;
        color: #274A21 !important;
        line-height: 1.50 !important;
    }

    /* ========================================================================= */
    /* 4. 2x2 EQUAL-SIZED NEUMORPHIC KPI CARDS (EVERY CARD IS COMPLETELY COLORED)*/
    /* ========================================================================= */
    .kpi-card-rect {
        border-radius: 24px !important;
        padding: 18px 22px !important;
        margin-bottom: 14px !important;
        height: 142px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
        transition: transform 0.20s cubic-bezier(0.25, 1, 0.5, 1), box-shadow 0.20s ease !important;
    }
    .kpi-card-rect:hover {
        transform: translateY(-3px) !important;
    }

    /* KPI 1: Peach Blush */
    .kpi-peach {
        background: linear-gradient(135deg, #FDEEE9 0%, #F8D1C5 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #E8AEA0 !important;
        box-shadow: 8px 8px 22px rgba(220, 160, 145, 0.40), -8px -8px 22px #FFFFFF !important;
    }
    .kpi-peach:hover {
        box-shadow: 10px 10px 26px rgba(220, 160, 145, 0.48), -10px -10px 26px #FFFFFF !important;
    }
    .kpi-peach .kpi-label-rect { color: #5D271B !important; }
    .kpi-peach .kpi-value-rect { color: #3E1D16 !important; }
    .kpi-peach .kpi-subtext-rect { color: #6F3528 !important; }
    .kpi-peach .kpi-icon-rect { background: #FFF3C7 !important; border: 1.5px solid #F0DA94 !important; box-shadow: inset 2px 2px 5px rgba(180,150,90,0.25) !important; }

    /* KPI 2: Sunlit Cream */
    .kpi-cream {
        background: linear-gradient(135deg, #FFFDF2 0%, #FFF3C7 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #F0DA94 !important;
        box-shadow: 8px 8px 22px rgba(215, 185, 110, 0.38), -8px -8px 22px #FFFFFF !important;
    }
    .kpi-cream:hover {
        box-shadow: 10px 10px 26px rgba(215, 185, 110, 0.45), -10px -10px 26px #FFFFFF !important;
    }
    .kpi-cream .kpi-label-rect { color: #5C490D !important; }
    .kpi-cream .kpi-value-rect { color: #3D3209 !important; }
    .kpi-cream .kpi-subtext-rect { color: #6D5612 !important; }
    .kpi-cream .kpi-icon-rect { background: #F8D1C5 !important; border: 1.5px solid #E8AEA0 !important; box-shadow: inset 2px 2px 5px rgba(200,130,120,0.25) !important; }

    /* KPI 3: Sage Mist */
    .kpi-sage {
        background: linear-gradient(135deg, #F3FAF2 0%, #A7C4A0 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #80A878 !important;
        box-shadow: 8px 8px 22px rgba(135, 170, 130, 0.40), -8px -8px 22px #FFFFFF !important;
    }
    .kpi-sage:hover {
        box-shadow: 10px 10px 26px rgba(135, 170, 130, 0.48), -10px -10px 26px #FFFFFF !important;
    }
    .kpi-sage .kpi-label-rect { color: #234720 !important; }
    .kpi-sage .kpi-value-rect { color: #193815 !important; }
    .kpi-sage .kpi-subtext-rect { color: #2E5429 !important; }
    .kpi-sage .kpi-icon-rect { background: #7FC4C3 !important; border: 1.5px solid #5AA8A7 !important; box-shadow: inset 2px 2px 5px rgba(90,140,140,0.25) !important; }

    /* KPI 4: Aqua Breeze */
    .kpi-aqua {
        background: linear-gradient(135deg, #EDF8F8 0%, #7FC4C3 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #5AA8A7 !important;
        box-shadow: 8px 8px 22px rgba(95, 165, 164, 0.40), -8px -8px 22px #FFFFFF !important;
    }
    .kpi-aqua:hover {
        box-shadow: 10px 10px 26px rgba(95, 165, 164, 0.48), -10px -10px 26px #FFFFFF !important;
    }
    .kpi-aqua .kpi-label-rect { color: #174A4A !important; }
    .kpi-aqua .kpi-value-rect { color: #103838 !important; }
    .kpi-aqua .kpi-subtext-rect { color: #205E5E !important; }
    .kpi-aqua .kpi-icon-rect { background: #A7C4A0 !important; border: 1.5px solid #80A878 !important; box-shadow: inset 2px 2px 5px rgba(100,140,95,0.25) !important; }

    /* KPI 5 / Alternate: Cloud Blue */
    .kpi-cloud {
        background: linear-gradient(135deg, #F2F5FD 0%, #A7B7E5 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #7F95DA !important;
        box-shadow: 8px 8px 22px rgba(135, 155, 205, 0.42), -8px -8px 22px #FFFFFF !important;
    }
    .kpi-cloud:hover {
        box-shadow: 10px 10px 26px rgba(135, 155, 205, 0.50), -10px -10px 26px #FFFFFF !important;
    }
    .kpi-cloud .kpi-label-rect { color: #24366A !important; }
    .kpi-cloud .kpi-value-rect { color: #19274E !important; }
    .kpi-cloud .kpi-subtext-rect { color: #344D8C !important; }
    .kpi-cloud .kpi-icon-rect { background: #C9B4E6 !important; border: 1.5px solid #AC91D8 !important; box-shadow: inset 2px 2px 5px rgba(150,120,180,0.25) !important; }

    .kpi-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        height: 32px !important;
    }
    .kpi-label-rect {
        font-size: 0.82rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    .kpi-icon-rect {
        font-size: 1.15rem !important;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 12px !important;
    }
    .kpi-value-rect {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 1.90rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        line-height: 1.15 !important;
        margin: 4px 0 !important;
    }
    .kpi-value-rect .unit-text {
        font-size: 0.84rem !important;
        font-weight: 700 !important;
        opacity: 0.85 !important;
    }
    .kpi-subtext-rect {
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        line-height: 1.25 !important;
    }

    /* ========================================================================= */
    /* 5. BOTTOM MODULES CONTAINER (EVERY MODULE BOX IS COMPLETELY COLORED)      */
    /* ========================================================================= */
    .bottom-modules-container {
        background: linear-gradient(180deg, #F5EFFB 0%, #E9DCF7 100%) !important;
        border-radius: 26px !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        box-shadow: inset 3px 3px 10px rgba(160, 135, 195, 0.28), inset -3px -3px 10px #FFFFFF !important;
        padding: 20px !important;
        margin-top: 14px !important;
        margin-bottom: 24px !important;
    }
    .bottom-modules-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        margin-bottom: 8px !important;
    }
    .header-badge-lavender {
        background: #C9B4E6 !important;
        border: 1px solid #AC91D8 !important;
        border-radius: 12px !important;
        padding: 3px 10px !important;
        font-size: 0.72rem !important;
        font-weight: 800 !important;
        color: #311B4C !important;
    }
    .bottom-modules-grid {
        display: grid !important;
        grid-template-columns: repeat(5, 1fr) !important;
        gap: 12px !important;
        margin-top: 10px !important;
    }
    @media (max-width: 900px) {
        .bottom-modules-grid {
            grid-template-columns: repeat(2, 1fr) !important;
        }
    }
    @media (max-width: 600px) {
        .bottom-modules-grid {
            grid-template-columns: 1fr !important;
        }
    }
    .bottom-module-box {
        border-radius: 18px !important;
        padding: 14px 12px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        min-height: 145px !important;
        transition: transform 0.20s ease, box-shadow 0.20s ease !important;
    }
    .bottom-module-box:hover {
        transform: translateY(-3px) !important;
    }

    /* Module 1: Peach Blush */
    .box-peach {
        background: linear-gradient(135deg, #FDF0EC 0%, #F8D1C5 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #E8AEA0 !important;
        box-shadow: 6px 6px 18px rgba(220, 160, 145, 0.40), -6px -6px 18px #FFFFFF !important;
    }
    .box-peach .box-title { color: #3E1D16 !important; }
    .box-peach .box-desc { color: #5D271B !important; }
    .box-peach .box-meta { color: #6F3528 !important; }

    /* Module 2: Sunlit Cream */
    .box-cream {
        background: linear-gradient(135deg, #FFFCEE 0%, #FFF3C7 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #F0DA94 !important;
        box-shadow: 6px 6px 18px rgba(215, 185, 110, 0.38), -6px -6px 18px #FFFFFF !important;
    }
    .box-cream .box-title { color: #3D3209 !important; }
    .box-cream .box-desc { color: #5C490D !important; }
    .box-cream .box-meta { color: #6D5612 !important; }

    /* Module 3: Sage Mist */
    .box-sage {
        background: linear-gradient(135deg, #F0F8EF 0%, #A7C4A0 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #80A878 !important;
        box-shadow: 6px 6px 18px rgba(135, 170, 130, 0.40), -6px -6px 18px #FFFFFF !important;
    }
    .box-sage .box-title { color: #193815 !important; }
    .box-sage .box-desc { color: #2E5429 !important; }
    .box-sage .box-meta { color: #3B6935 !important; }

    /* Module 4: Aqua Breeze */
    .box-aqua {
        background: linear-gradient(135deg, #E6F7F7 0%, #7FC4C3 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #5AA8A7 !important;
        box-shadow: 6px 6px 18px rgba(95, 165, 164, 0.40), -6px -6px 18px #FFFFFF !important;
    }
    .box-aqua .box-title { color: #103838 !important; }
    .box-aqua .box-desc { color: #174A4A !important; }
    .box-aqua .box-meta { color: #205E5E !important; }

    /* Module 5: Lavender Haze */
    .box-cloud,
    .box-lavender {
        background: linear-gradient(135deg, #F5EFFB 0%, #C9B4E6 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-top: 5px solid #AC91D8 !important;
        box-shadow: 6px 6px 18px rgba(175, 150, 205, 0.42), -6px -6px 18px #FFFFFF !important;
    }
    .box-cloud .box-title, .box-lavender .box-title { color: #311B4C !important; }
    .box-cloud .box-desc, .box-lavender .box-desc { color: #4E2E72 !important; }
    .box-cloud .box-meta, .box-lavender .box-meta { color: #5D388A !important; }

    .box-top {
        margin-bottom: 6px !important;
    }
    .box-tag {
        display: inline-block !important;
        font-size: 0.65rem !important;
        font-weight: 800 !important;
        padding: 2px 7px !important;
        border-radius: 8px !important;
        margin-bottom: 5px !important;
        border: 1px solid rgba(255, 255, 255, 0.70) !important;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.10) !important;
    }
    .box-title {
        font-size: 0.86rem !important;
        font-weight: 800 !important;
        line-height: 1.25 !important;
    }
    .box-desc {
        font-size: 0.74rem !important;
        line-height: 1.40 !important;
        margin-bottom: 6px !important;
    }
    .box-meta {
        font-size: 0.68rem !important;
        font-weight: 700 !important;
    }

    /* ========================================================================= */
    /* 6. ANALYTICAL VIEWS: SUB-NAV PILLS & EXPLANATION CARDS                     */
    /* ========================================================================= */
    /* Sub-Navigation Pills (Neumorphic Floating Capsules) */
    div[class*="st-key-pill_"] button {
        border-radius: 20px !important;
        font-size: 0.80rem !important;
        font-weight: 700 !important;
        height: 38px !important;
        min-height: 38px !important;
        padding: 6px 14px !important;
        transition: all 0.20s cubic-bezier(0.25, 1, 0.5, 1) !important;
    }
    div[class*="st-key-pill_"] button[kind="secondary"] {
        background: linear-gradient(135deg, #FFFDF6 0%, #EFF4EC 100%) !important;
        color: var(--text-dark) !important;
        border: 1.5px solid var(--nm-border) !important;
        box-shadow: 3px 3px 8px var(--nm-shadow), -3px -3px 8px var(--nm-light) !important;
    }
    div[class*="st-key-pill_"] button[kind="secondary"]:hover {
        background: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 4px 4px 12px var(--nm-shadow), -4px -4px 12px #FFFFFF !important;
        color: #103838 !important;
    }
    div[class*="st-key-pill_"] button[kind="primary"] {
        background: linear-gradient(135deg, #7FC4C3 0%, #5AA8A7 100%) !important;
        color: #FFFFFF !important;
        border: 1.5px solid rgba(255, 255, 255, 0.50) !important;
        box-shadow: inset 2px 2px 5px rgba(20, 60, 60, 0.35), inset -2px -2px 5px rgba(255, 255, 255, 0.25), 0 4px 12px rgba(95, 165, 164, 0.35) !important;
        font-weight: 800 !important;
        transform: translateY(0) !important;
    }

    /* Explanation Card (Aqua Breeze Soft Card) */
    .chart-explanation {
        background: linear-gradient(135deg, #F0F9F9 0%, #E0F2F2 100%) !important;
        border-radius: 20px !important;
        box-shadow: 6px 6px 18px rgba(95, 165, 164, 0.30), -6px -6px 18px #FFFFFF !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-left: 6px solid #7FC4C3 !important;
        padding: 14px 18px !important;
        margin-top: 12px !important;
        margin-bottom: 16px !important;
    }
    .chart-explanation-title {
        font-size: 0.90rem !important;
        font-weight: 800 !important;
        color: #103838 !important;
        margin-bottom: 4px !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
    }
    .chart-explanation-body {
        font-size: 0.86rem !important;
        color: #1B4A4A !important;
        line-height: 1.50 !important;
    }

    /* Growth KPI Cards (Full Colored Neumorphic Cards) */
    .growth-kpi-card {
        border-radius: 18px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        height: 100px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        transition: transform 0.20s ease, box-shadow 0.20s ease !important;
    }
    .growth-kpi-card:hover {
        transform: translateY(-2px) !important;
    }
    .growth-kpi-sage {
        background: linear-gradient(135deg, #F0F8EF 0%, #A7C4A0 100%) !important;
        border: 2px solid rgba(255,255,255,0.95) !important;
        border-top: 4px solid #80A878 !important;
        box-shadow: 6px 6px 16px rgba(135, 170, 130, 0.38), -6px -6px 16px #FFFFFF !important;
    }
    .growth-kpi-aqua {
        background: linear-gradient(135deg, #EAF7F7 0%, #7FC4C3 100%) !important;
        border: 2px solid rgba(255,255,255,0.95) !important;
        border-top: 4px solid #5AA8A7 !important;
        box-shadow: 6px 6px 16px rgba(95, 165, 164, 0.38), -6px -6px 16px #FFFFFF !important;
    }
    .growth-kpi-cloud {
        background: linear-gradient(135deg, #F0F4FD 0%, #A7B7E5 100%) !important;
        border: 2px solid rgba(255,255,255,0.95) !important;
        border-top: 4px solid #7F95DA !important;
        box-shadow: 6px 6px 16px rgba(135, 155, 205, 0.40), -6px -6px 16px #FFFFFF !important;
    }
    .growth-kpi-peach {
        background: linear-gradient(135deg, #FDF2EE 0%, #F8D1C5 100%) !important;
        border: 2px solid rgba(255,255,255,0.95) !important;
        border-top: 4px solid #E8AEA0 !important;
        box-shadow: 6px 6px 16px rgba(220, 160, 145, 0.38), -6px -6px 16px #FFFFFF !important;
    }
    .growth-kpi-lavender {
        background: linear-gradient(135deg, #F6F1FC 0%, #C9B4E6 100%) !important;
        border: 2px solid rgba(255,255,255,0.95) !important;
        border-top: 4px solid #AC91D8 !important;
        box-shadow: 6px 6px 16px rgba(175, 150, 205, 0.40), -6px -6px 16px #FFFFFF !important;
    }
    .growth-kpi-label {
        font-size: 0.74rem !important;
        font-weight: 800 !important;
        color: var(--text-dark) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.4px !important;
    }
    .growth-kpi-val {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        color: var(--text-dark) !important;
        line-height: 1.15 !important;
    }
    .growth-kpi-val .unit-text {
        font-size: 0.74rem !important;
        font-weight: 700 !important;
    }
    .growth-kpi-sub {
        font-size: 0.70rem !important;
        font-weight: 700 !important;
        color: var(--text-dark) !important;
        opacity: 0.85 !important;
    }

    /* Math Methodology Reference Card (Lavender Haze) */
    .math-methodology-card {
        background: linear-gradient(135deg, #F6F1FC 0%, #EDE2F8 100%) !important;
        border-radius: 20px !important;
        box-shadow: 6px 6px 18px rgba(175, 150, 205, 0.32), -6px -6px 18px #FFFFFF !important;
        border: 2px solid rgba(255, 255, 255, 0.95) !important;
        border-left: 6px solid #A7B7E5 !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
    }

    /* Plotly Chart Card Container */
    [data-testid="stPlotlyChart"] {
        background: rgba(247, 250, 246, 0.85) !important;
        border-radius: 22px !important;
        padding: 12px 14px !important;
        box-shadow: 6px 6px 18px rgba(135, 160, 125, 0.28), -6px -6px 18px #FFFFFF !important;
        border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
        margin-bottom: 12px !important;
    }

    /* Streamlit Dataframe / Table Container */
    [data-testid="stDataFrame"] {
        background: rgba(247, 250, 246, 0.90) !important;
        border-radius: 18px !important;
        box-shadow: inset 2px 2px 6px rgba(125, 150, 115, 0.22), inset -2px -2px 6px #FFFFFF !important;
        padding: 8px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
    }

    /* Standard Interactive Button Elevation */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7FC4C3 0%, #5AA8A7 100%) !important;
        color: #FFFFFF !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        border: 1.5px solid rgba(255, 255, 255, 0.50) !important;
        box-shadow: 4px 4px 12px rgba(95, 165, 164, 0.38), -4px -4px 12px #FFFFFF !important;
        transition: all 0.20s cubic-bezier(0.25, 1, 0.5, 1) !important;
    }
    button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 6px 6px 16px rgba(95, 165, 164, 0.48), -6px -6px 16px #FFFFFF !important;
    }
    button[kind="secondary"], .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #FFFDF6 0%, #FFF3C7 100%) !important;
        color: #3D3209 !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        border: 1.5px solid #F0DA94 !important;
        box-shadow: 3px 3px 10px rgba(215, 185, 110, 0.30), -3px -3px 10px #FFFFFF !important;
        transition: all 0.20s cubic-bezier(0.25, 1, 0.5, 1) !important;
    }
    button[kind="secondary"]:hover, .stButton > button[kind="secondary"]:hover {
        background: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 5px 5px 14px rgba(215, 185, 110, 0.38), -5px -5px 14px #FFFFFF !important;
        color: #103838 !important;
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #F0F8EF 0%, #A7C4A0 100%) !important;
        color: #193815 !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        border: 1.5px solid #80A878 !important;
        box-shadow: 4px 4px 12px rgba(135, 170, 130, 0.35), -4px -4px 12px #FFFFFF !important;
        transition: all 0.20s ease !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 6px 6px 16px rgba(135, 170, 130, 0.45), -6px -6px 16px #FFFFFF !important;
    }

    /* Dashboard Footer Card */
    .dashboard-footer {
        background: linear-gradient(135deg, #FFFDF5 0%, #FFF3C7 100%) !important;
        border-radius: 18px !important;
        border: 1.5px solid rgba(255, 255, 255, 0.95) !important;
        box-shadow: 6px 6px 18px rgba(210, 185, 110, 0.30), -6px -6px 18px #FFFFFF !important;
        padding: 16px 20px !important;
        margin-top: 24px !important;
        text-align: center !important;
        font-size: 0.78rem !important;
        color: #38240D !important;
        line-height: 1.6 !important;
    }
</style>"""
st.markdown(CSS_STYLESHEET.replace("__BG_IMAGE_PLACEHOLDER__", BG_IMAGE_BASE64), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. DATA INGESTION & CACHING (PRESERVED 100%)
# -----------------------------------------------------------------------------
@st.cache_data
def load_dataset():
    """Loads and standardizes the cleaned dataset."""
    possible_paths = [
        "outputs/cleaned_banana_data.csv",
        "cleaned_banana_data.csv",
        "data/cleaned_banana_data.csv"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['Year'] = df['Year'].astype(int)
            df['Volume_MT'] = pd.to_numeric(df['Volume_MT'], errors='coerce')
            return df
            
    st.error("Cleaned dataset not found! Please run `src/data_cleaning.py` first.")
    st.stop()

df = load_dataset()


# -----------------------------------------------------------------------------
# 3. SIDEBAR NAVIGATION & SURVEILLANCE FILTERS (RESTORED TO CLASSIC SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-box">
        <div class="sidebar-brand-title">
            <span>🍌</span> BananaScope PH
        </div>
        <div class="sidebar-brand-subtitle">
            Philippine Banana Production Analytics Platform (2010–2026)
        </div>
        <span class="sidebar-tag">🇵🇭 DepEd MIMAROPA • Grade 12</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section-title">🧭 Navigation Menu</div>
    """, unsafe_allow_html=True)

    # Tactile Neumorphic Navigation Buttons
    for cat in CATEGORIES:
        is_active = (st.session_state.active_category == cat["id"])
        btn_label = f"{cat['icon']}  {cat['title']}"
        if st.button(btn_label, key=f"sb_nav_{cat['id']}", type="primary" if is_active else "secondary", use_container_width=True):
            navigate_to(cat["id"])

    st.markdown("<hr style='margin: 16px 0 14px 0; border: none; border-top: 1.5px solid rgba(160, 182, 150, 0.35);'>", unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section-title">🎛️ Surveillance Filters</div>
    """, unsafe_allow_html=True)

    # 1. Year Range Filter (PRESERVED 100%)
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    selected_years = st.slider(
        "📅 Select Year Horizon:",
        min_value=min_year,
        max_value=max_year,
        value=(2010, min(2024, max_year)),
        step=1
    )

    # 2. Measurement Frequency (PRESERVED 100%)
    period_options = ["Annual (Recommended)", "Quarterly (Q1–Q4)", "Semester (S1–S2)"]
    selected_period_type = st.radio(
        "⏱️ Reporting Frequency:",
        options=period_options,
        index=0,
        help="Annual totals prevent double-counting. Choose Quarterly to inspect intra-annual cycles."
    )

    quarter_filter = "All"
    if selected_period_type == "Quarterly (Q1–Q4)":
        quarter_filter = st.selectbox("Quarter:", ["All", "Q1", "Q2", "Q3", "Q4"])

    # 3. Banana Variety Scope (PRESERVED 100%)
    all_varieties = sorted(df['Crop'].unique().tolist())
    variety_mode = st.radio(
        "🍌 Cultivar Scope:",
        ["Total Banana (Aggregated)", "Specific Cultivars Breakdown", "Custom Selection"],
        index=0
    )

    if variety_mode == "Total Banana (Aggregated)":
        selected_varieties = ["Banana (Total)"]
    elif variety_mode == "Specific Cultivars Breakdown":
        selected_varieties = [v for v in all_varieties if v != "Banana (Total)"]
    else:
        selected_varieties = st.multiselect(
            "Select Varieties:",
            options=all_varieties,
            default=["Banana (Total)"]
        )
        if not selected_varieties:
            selected_varieties = ["Banana (Total)"]

    st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px dashed rgba(160, 182, 150, 0.35);'>", unsafe_allow_html=True)

    # 4. Regional & Geographic Filter (PRESERVED 100%)
    available_regions = sorted(df[df['Hierarchy_Level'] == 'Regional']['Region'].unique().tolist())
    all_regions_opt = "All Administrative Regions (National Scope)"
    region_options = [all_regions_opt] + available_regions
    selected_region = st.selectbox(
        "🗺️ Select Region:",
        options=region_options,
        index=0
    )

    if selected_region == all_regions_opt:
        available_provinces = sorted(df[df['Hierarchy_Level'].isin(['Provincial', 'City'])]['Province_City'].unique().tolist())
    else:
        available_provinces = sorted(df[(df['Region'] == selected_region) & 
                                        (df['Hierarchy_Level'].isin(['Provincial', 'City']))]['Province_City'].unique().tolist())
    all_prov_opt = "All Provinces / Cities"
    province_options = [all_prov_opt] + available_provinces
    selected_province = st.selectbox(
        "📍 Select Province / City:",
        options=province_options,
        index=0
    )

    st.markdown("""
    <div class="sidebar-footer-card">
        <div style="font-weight: 700; font-size: 0.78rem; color: var(--text-dark);">🌾 Official PSA OpenStat Data</div>
        <div style="font-size: 0.70rem; color: var(--text-muted); margin-top: 2px;">84,133 Production Records • 15-Yr Longitudinal Scope</div>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. FILTERING LOGIC (PRESERVED 100%)
# -----------------------------------------------------------------------------
filtered_df = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1])].copy()

# Period Type Filter
if selected_period_type == "Annual (Recommended)":
    filtered_df = filtered_df[filtered_df['Period_Type'] == 'Annual'].copy()
elif selected_period_type == "Quarterly (Q1–Q4)":
    filtered_df = filtered_df[filtered_df['Period_Type'] == 'Quarterly'].copy()
    if quarter_filter != "All":
        filtered_df = filtered_df[filtered_df['Period'] == quarter_filter].copy()
elif selected_period_type == "Semester (S1–S2)":
    filtered_df = filtered_df[filtered_df['Period_Type'] == 'Semester'].copy()

# Cultivar Filter
filtered_df = filtered_df[filtered_df['Crop'].isin(selected_varieties)].copy()

# Geographic Hierarchy Routing
if selected_province != all_prov_opt:
    active_df = filtered_df[filtered_df['Province_City'] == selected_province].copy()
    geo_label = selected_province
    geo_level = "Provincial"
elif selected_region != all_regions_opt:
    active_df = filtered_df[(filtered_df['Region'] == selected_region) & 
                            (filtered_df['Hierarchy_Level'] == 'Regional')].copy()
    geo_label = selected_region
    geo_level = "Regional"
else:
    active_df = filtered_df[filtered_df['Hierarchy_Level'] == 'National'].copy()
    geo_label = "Philippines (National Aggregate)"
    geo_level = "National"


# -----------------------------------------------------------------------------
# 6. SUMMARY CALCULATIONS FOR KPI SUMMARY (PRESERVED CALCULATIONS)
# -----------------------------------------------------------------------------
valid_vols = active_df['Volume_MT'].dropna()
total_production_mt = valid_vols.sum()

if not active_df.empty and active_df['Year'].nunique() > 0:
    yearly_totals = active_df.groupby('Year')['Volume_MT'].sum()
    avg_annual_mt = yearly_totals.mean()
    if not yearly_totals.empty:
        peak_year = int(yearly_totals.idxmax())
        peak_vol_mt = yearly_totals.max()
        lowest_year = int(yearly_totals.idxmin())
        lowest_vol_mt = yearly_totals.min()
    else:
        peak_year, peak_vol_mt, lowest_year, lowest_vol_mt = "N/A", 0, "N/A", 0
else:
    avg_annual_mt = 0
    peak_year, peak_vol_mt, lowest_year, lowest_vol_mt = "N/A", 0, "N/A", 0

# Benchmark Top Producing Region across selected period (PRESERVED)
reg_benchmark = df[
    (df['Year'] >= selected_years[0]) & 
    (df['Year'] <= selected_years[1]) & 
    (df['Hierarchy_Level'] == 'Regional') &
    (df['Crop'].isin(selected_varieties)) &
    (df['Period_Type'] == ('Annual' if selected_period_type == "Annual (Recommended)" else 'Quarterly'))
]
if not reg_benchmark.empty:
    top_reg_series = reg_benchmark.groupby('Region')['Volume_MT'].sum()
    top_region_name = top_reg_series.idxmax().replace("REGION ", "Reg ").replace("ADMINISTRATIVE REGION", "CAR")
    top_region_vol = top_reg_series.max()
else:
    top_region_name, top_region_vol = "N/A", 0


# -----------------------------------------------------------------------------
# 7. PLOTLY PALETTE & VISUAL HELPERS (4-COLOR SYSTEM)
# -----------------------------------------------------------------------------
PLOT_THEME = dict(
    plot_bgcolor="#EFF4EC",
    paper_bgcolor="#EFF4EC",
    font=dict(family="'Plus Jakarta Sans', sans-serif", color="#24331E"),
    hoverlabel=dict(bgcolor="#24331E", font_color="#FFFFFF", font_family="'Plus Jakarta Sans', sans-serif")
)

def render_explanation(chart_title, explanation_text):
    """Renders a concise 2-sentence explanation card directly below each visual."""
    st.markdown(f"""
    <div class="chart-explanation">
        <div class="chart-explanation-title">🌿 Understanding This Visual: {chart_title}</div>
        <div class="chart-explanation-body">{explanation_text}</div>
    </div>
    """, unsafe_allow_html=True)

def render_view_header(view_id):
    """Renders category status header and sequential Previous / Next buttons."""
    view_info = next((v for v in ALL_VIEWS_ORDER if v["view"] == view_id), None)
    if not view_info:
        return
    current_idx = ALL_VIEWS_ORDER.index(view_info)
    has_prev = current_idx > 0
    prev_item = ALL_VIEWS_ORDER[current_idx - 1] if has_prev else None
    has_next = current_idx < len(ALL_VIEWS_ORDER) - 1
    next_item = ALL_VIEWS_ORDER[current_idx + 1] if has_next else None

    cat_styles = {
        "PROD": ("linear-gradient(135deg, #FDEEE9 0%, #F8D1C5 100%)", "#E8AEA0", "#3E1D16", "rgba(220, 160, 145, 0.38)"),
        "REG":  ("linear-gradient(135deg, #F3FAF2 0%, #A7C4A0 100%)", "#80A878", "#193815", "rgba(135, 170, 130, 0.38)"),
        "VAR":  ("linear-gradient(135deg, #FFFDF2 0%, #FFF3C7 100%)", "#F0DA94", "#3D3209", "rgba(215, 185, 110, 0.35)"),
        "TREND": ("linear-gradient(135deg, #F2F5FD 0%, #A7B7E5 100%)", "#7F95DA", "#19274E", "rgba(135, 155, 205, 0.40)"),
        "REC":  ("linear-gradient(135deg, #F6F1FC 0%, #C9B4E6 100%)", "#AC91D8", "#311B4C", "rgba(175, 150, 205, 0.40)")
    }
    bg_grad, border_c, text_c, shadow_c = cat_styles.get(view_info["cat"], ("linear-gradient(135deg, #EDF8F8 0%, #7FC4C3 100%)", "#5AA8A7", "#103838", "rgba(95,165,164,0.35)"))

    st.markdown(f"""
    <div style="background: {bg_grad}; border-radius: 20px; border: 2px solid rgba(255,255,255,0.95); border-left: 6px solid {border_c}; padding: 12px 18px; margin-bottom: 14px; box-shadow: 7px 7px 20px {shadow_c}, -7px -7px 20px #FFFFFF;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.25rem;">{view_info['icon']}</span>
                <div>
                    <div style="font-size: 0.72rem; font-weight: 800; color: {text_c}; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px;">
                        Category: {view_info['cat']} • Section {current_idx + 1} of 13
                    </div>
                    <div style="margin: 0; font-size: 1.10rem; font-weight: 700; color: {text_c};">
                        {view_info['title']}
                    </div>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.70); border: 1.5px solid {border_c}; border-radius: 12px; padding: 4px 12px; font-weight: 800; font-size: 0.76rem; color: {text_c}; box-shadow: 2px 2px 6px rgba(0,0,0,0.06);">
                {view_info['icon']} {view_info['cat']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Secondary Navigation Bar (Home | Previous | Next)
    c_prev, c_home, c_next = st.columns([1.5, 1.2, 1.8])
    with c_prev:
        if has_prev:
            if st.button(f"⬅️ {prev_item['title']}", key=f"top_prev_{view_id}", type="secondary", use_container_width=True):
                navigate_to(prev_item["cat"], prev_item["sub"])
        else:
            if st.button("🏠 Return to Home", key=f"top_prev_home_{view_id}", type="secondary", use_container_width=True):
                navigate_to("HOME")
    with c_home:
        if st.button("🏠 Home Overview", key=f"top_home_{view_id}", type="secondary", use_container_width=True):
            navigate_to("HOME")
    with c_next:
        if has_next:
            if st.button(f"Next: {next_item['title']} ➡️", key=f"top_next_{view_id}", type="primary", use_container_width=True):
                navigate_to(next_item["cat"], next_item["sub"])
        else:
            if st.button("🏠 Back to Home", key=f"top_next_home_{view_id}", type="primary", use_container_width=True):
                navigate_to("HOME")

def render_view_footer(view_id):
    """Renders bottom navigation controls."""
    view_info = next((v for v in ALL_VIEWS_ORDER if v["view"] == view_id), None)
    if not view_info:
        return
    current_idx = ALL_VIEWS_ORDER.index(view_info)
    has_prev = current_idx > 0
    prev_item = ALL_VIEWS_ORDER[current_idx - 1] if has_prev else None
    has_next = current_idx < len(ALL_VIEWS_ORDER) - 1
    next_item = ALL_VIEWS_ORDER[current_idx + 1] if has_next else None

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    c_prev, c_home, c_next = st.columns([1.5, 1.2, 1.8])
    with c_prev:
        if has_prev:
            if st.button(f"⬅️ {prev_item['title']}", key=f"bot_prev_{view_id}", type="secondary", use_container_width=True):
                navigate_to(prev_item["cat"], prev_item["sub"])
        else:
            if st.button("🏠 Return to Home", key=f"bot_prev_home_{view_id}", type="secondary", use_container_width=True):
                navigate_to("HOME")
    with c_home:
        if st.button("🏠 Home Overview", key=f"bot_home_{view_id}", type="secondary", use_container_width=True):
            navigate_to("HOME")
    with c_next:
        if has_next:
            if st.button(f"Next: {next_item['title']} ➡️", key=f"bot_next_{view_id}", type="primary", use_container_width=True):
                navigate_to(next_item["cat"], next_item["sub"])
        else:
            if st.button("🏠 Back to Home", key=f"bot_next_home_{view_id}", type="primary", use_container_width=True):
                navigate_to("HOME")


# =============================================================================
# 8. CORE ANALYTICAL VIEW RENDERERS (PRESERVED 100%)
# =============================================================================

def render_annual_trajectory_content():
    if not active_df.empty:
        annual_plot_data = active_df.groupby(['Year', 'Crop'])['Volume_MT'].sum().reset_index()
        fig_traj = px.line(
            annual_plot_data, x='Year', y='Volume_MT', color='Crop',
            markers=True, line_shape='spline',
            color_discrete_sequence=['#7FC4C3', '#F8D1C5', '#A7B7E5', '#A7C4A0', '#C9B4E6', '#FFF3C7'],
            labels={'Volume_MT': 'Volume (Metric Tons)', 'Year': 'Calendar Year'}
        )
        fig_traj.update_layout(
            **PLOT_THEME,
            height=460,
            hovermode="x unified",
            margin=dict(l=55, r=25, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255,255,255,0.95)")
        )
        fig_traj.update_traces(marker=dict(size=7, line=dict(color='#FFFFFF', width=1.5)))
        fig_traj.update_yaxes(gridcolor='rgba(150, 172, 140, 0.22)', tickformat=",.0f", title_standoff=8)
        fig_traj.update_xaxes(gridcolor='rgba(150, 172, 140, 0.22)', dtick=1, title_standoff=8)
        st.plotly_chart(fig_traj, use_container_width=True)
        render_explanation(
            "Annual Banana Production Trajectory",
            "This line chart tracks the multi-year volume of bananas harvested across the selected geographic scope from 2010 to 2024. "
            "It shows steady national growth toward the 2018 peak of 9.36 million metric tons, followed by a multi-year contraction."
        )
    else:
        st.warning("No data available for the current filter selection.")

def render_quarterly_seasonality_content():
    q_subset = df[(df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1]) & (df['Period_Type'] == 'Quarterly') & (df['Crop'].isin(selected_varieties))]
    if selected_province != all_prov_opt:
        q_subset = q_subset[q_subset['Province_City'] == selected_province]
    elif selected_region != all_regions_opt:
        q_subset = q_subset[(q_subset['Region'] == selected_region) & (q_subset['Hierarchy_Level'] == 'Regional')]
    else:
        q_subset = q_subset[q_subset['Hierarchy_Level'] == 'National']

    if not q_subset.empty:
        q_agg = q_subset.groupby('Period')['Volume_MT'].mean().reindex(['Q1', 'Q2', 'Q3', 'Q4']).reset_index()
        labels_txt = [f"{v/1e6:.2f}M MT" if v >= 1e6 else f"{v/1e3:,.0f}K MT" for v in q_agg['Volume_MT']]
        fig_q = px.bar(
            q_agg, x='Period', y='Volume_MT', color='Period',
            color_discrete_sequence=['#F8D1C5', '#FFF3C7', '#A7C4A0', '#7FC4C3'],
            labels={'Volume_MT': 'Average Harvest (Metric Tons)', 'Period': 'Quarter'},
            text=labels_txt
        )
        max_val = q_agg['Volume_MT'].max()
        fig_q.update_traces(
            marker_line_color='#1E293B', marker_line_width=0.8,
            textposition='outside', cliponaxis=False,
            textfont=dict(size=11, family="'Plus Jakarta Sans', sans-serif", color='#1E293B')
        )
        fig_q.update_layout(
            **PLOT_THEME,
            height=440,
            showlegend=False,
            margin=dict(l=55, r=25, t=40, b=40)
        )
        fig_q.update_yaxes(gridcolor='rgba(150, 172, 140, 0.22)', range=[0, max_val * 1.20], tickformat=",.0f")
        fig_q.update_xaxes(gridcolor='rgba(150, 172, 140, 0.22)')
        st.plotly_chart(fig_q, use_container_width=True)
        render_explanation(
            "Seasonal Quarterly Harvest Patterns",
            "This bar chart compares average banana harvests across all four calendar quarters to highlight seasonal production rhythms. "
            "Quarter 1 regularly experiences the lowest harvest volume of the year, while Quarters 2 through 4 sustain higher yields."
        )
    else:
        st.warning("No quarterly records found for the current selection.")

def render_regional_rankings_content():
    reg_data = df[
        (df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1]) & 
        (df['Hierarchy_Level'] == 'Regional') & 
        (df['Period_Type'] == ('Annual' if selected_period_type == "Annual (Recommended)" else 'Quarterly')) &
        (df['Crop'].isin(selected_varieties))
    ].groupby('Region')['Volume_MT'].sum().reset_index().sort_values('Volume_MT', ascending=True)

    if not reg_data.empty:
        reg_data['Clean_Region'] = reg_data['Region'].str.replace(r'REGION [IVX]+ \((.*?)\)', r'\1', regex=True)
        bar_labels = [f"{v/1e6:.2f}M MT" if v >= 1e6 else f"{v/1e3:,.0f}K MT" for v in reg_data['Volume_MT']]
        fig_reg = px.bar(
            reg_data, x='Volume_MT', y='Clean_Region', orientation='h',
            color='Volume_MT', color_continuous_scale=['#FFF3C7', '#A7C4A0', '#7FC4C3', '#A7B7E5', '#C9B4E6'],
            labels={'Volume_MT': 'Total Production (Metric Tons)', 'Clean_Region': 'Administrative Region'},
            text=bar_labels
        )
        max_reg = reg_data['Volume_MT'].max()
        fig_reg.update_traces(
            marker_line_color='#1E293B', marker_line_width=0.8,
            textposition='outside', cliponaxis=False,
            textfont=dict(size=10, family="'Plus Jakarta Sans', sans-serif", color='#1E293B')
        )
        fig_reg.update_layout(
            **PLOT_THEME,
            height=max(520, len(reg_data) * 30),
            coloraxis_showscale=False,
            margin=dict(l=145, r=60, t=30, b=30)
        )
        fig_reg.update_xaxes(gridcolor='rgba(150, 172, 140, 0.22)', range=[0, max_reg * 1.22], tickformat=",.0f")
        fig_reg.update_yaxes(gridcolor='rgba(150, 172, 140, 0.22)')
        st.plotly_chart(fig_reg, use_container_width=True)
        render_explanation(
            "Regional Banana Production Comparison",
            "This horizontal ranking chart benchmarks total banana production across all 17 Philippine administrative regions. "
            "It highlights heavy production concentration in Mindanao, led by Davao Region with over half of the national harvest."
        )
    else:
        st.warning("No regional records found for current filters.")

def render_cultivar_donut_content():
    cult_df = df[
        (df['Year'] >= selected_years[0]) & (df['Year'] <= selected_years[1]) & 
        (df['Crop'] != 'Banana (Total)') & 
        (df['Period_Type'] == ('Annual' if selected_period_type == "Annual (Recommended)" else 'Quarterly'))
    ]
    if selected_province != all_prov_opt:
        cult_df = cult_df[cult_df['Province_City'] == selected_province]
    elif selected_region != all_regions_opt:
        cult_df = cult_df[(cult_df['Region'] == selected_region) & (cult_df['Hierarchy_Level'] == 'Regional')]
    else:
        cult_df = cult_df[cult_df['Hierarchy_Level'] == 'National']

    if not cult_df.empty:
        cult_agg = cult_df.groupby('Crop')['Volume_MT'].sum().reset_index()
        cult_agg['Crop_Name'] = cult_agg['Crop'].str.replace('Banana ', '')
        fig_donut = px.pie(
            cult_agg, names='Crop_Name', values='Volume_MT', hole=0.48,
            color_discrete_sequence=['#7FC4C3', '#F8D1C5', '#A7B7E5', '#A7C4A0', '#C9B4E6', '#FFF3C7']
        )
        fig_donut.update_traces(
            marker=dict(line=dict(color='#FFFFFF', width=2)),
            textposition='inside', textinfo='percent+label',
            textfont=dict(size=12, color='#FFFFFF')
        )
        fig_donut.update_layout(
            **PLOT_THEME,
            height=440,
            margin=dict(l=20, r=20, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=-0.16, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        render_explanation(
            "Variety Market Share Breakdown",
            "This donut chart displays the percentage share of each major banana cultivar in total recorded production. "
            "Cavendish for commercial export and Saba for domestic consumption together account for approximately 80% of total output."
        )
    else:
        st.warning("No cultivar records found for current selection.")

def render_variety_comparison_content():
    multi_var_df = df[(df['Hierarchy_Level'] == 'National') & (df['Crop'] != 'Banana (Total)') & (df['Period_Type'] == 'Annual') & (df['Year'] <= selected_years[1]) & (df['Year'] >= selected_years[0])]
    if not multi_var_df.empty:
        fig_cult_growth = px.line(
            multi_var_df, x='Year', y='Volume_MT', color='Crop',
            markers=True, line_shape='spline',
            color_discrete_sequence=['#7FC4C3', '#F8D1C5', '#A7B7E5', '#A7C4A0', '#C9B4E6'],
            labels={'Volume_MT': 'Volume (Metric Tons)', 'Year': 'Calendar Year'}
        )
        fig_cult_growth.update_layout(
            **PLOT_THEME,
            height=460,
            hovermode="x unified",
            margin=dict(l=55, r=25, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255,255,255,0.95)")
        )
        fig_cult_growth.update_traces(marker=dict(size=7, line=dict(color='#FFFFFF', width=1.5)))
        fig_cult_growth.update_yaxes(gridcolor='rgba(150, 172, 140, 0.22)', tickformat=",.0f", title_standoff=8)
        fig_cult_growth.update_xaxes(gridcolor='rgba(150, 172, 140, 0.22)', dtick=1, title_standoff=8)
        st.plotly_chart(fig_cult_growth, use_container_width=True)
        render_explanation(
            "Multi-Year Harvest Trends by Variety",
            "This multi-line chart tracks historical harvest trajectories for individual cultivars over the 15-year period. "
            "It reveals significant contraction in Cavendish post-2018 due to Fusarium Wilt, while local staple varieties like Saba exhibited resilience."
        )
    else:
        st.warning("No multi-variety records available for current selection.")

def render_yoy_growth_content():
    if len(yearly_totals) >= 2:
        yoy_base = pd.DataFrame({'Year': yearly_totals.index, 'Volume_MT': yearly_totals.values})
        yoy_df = compute_yoy_growth(yoy_base)
        yoy_clean = yoy_df.dropna(subset=['YoY_Growth_Pct']).copy()

        start_y = yearly_totals.index.min()
        end_y = yearly_totals.index.max()
        v_start = yearly_totals.loc[start_y]
        v_end = yearly_totals.loc[end_y]
        cagr_val = calculate_cagr(v_start, v_end, end_y - start_y)
        mean_yoy = yoy_clean['YoY_Growth_Pct'].mean()
        max_growth_row = yoy_clean.loc[yoy_clean['YoY_Growth_Pct'].idxmax()]
        min_growth_row = yoy_clean.loc[yoy_clean['YoY_Growth_Pct'].idxmin()]

        g_c1, g_c2, g_c3, g_c4 = st.columns(4)
        with g_c1:
            st.markdown(f"""
            <div class="growth-kpi-card growth-kpi-sage">
                <div class="growth-kpi-label">CAGR (Annualized Rate)</div>
                <div class="growth-kpi-val">{cagr_val:+.2f}% <span class="unit-text">/ yr</span></div>
                <div class="growth-kpi-sub">Trajectory ({start_y}–{end_y})</div>
            </div>
            """, unsafe_allow_html=True)
        with g_c2:
            st.markdown(f"""
            <div class="growth-kpi-card growth-kpi-aqua">
                <div class="growth-kpi-label">Average YoY Growth</div>
                <div class="growth-kpi-val">{mean_yoy:+.2f}%</div>
                <div class="growth-kpi-sub">Mean annual change</div>
            </div>
            """, unsafe_allow_html=True)
        with g_c3:
            st.markdown(f"""
            <div class="growth-kpi-card growth-kpi-cloud">
                <div class="growth-kpi-label">Highest Growth Surge</div>
                <div class="growth-kpi-val">{max_growth_row['YoY_Growth_Pct']:+.1f}%</div>
                <div class="growth-kpi-sub">Recorded in year {int(max_growth_row['Year'])}</div>
            </div>
            """, unsafe_allow_html=True)
        with g_c4:
            st.markdown(f"""
            <div class="growth-kpi-card growth-kpi-peach">
                <div class="growth-kpi-label">Deepest Contraction</div>
                <div class="growth-kpi-val">{min_growth_row['YoY_Growth_Pct']:+.1f}%</div>
                <div class="growth-kpi-sub">Recorded in year {int(min_growth_row['Year'])}</div>
            </div>
            """, unsafe_allow_html=True)

        yoy_clean['Growth_Color'] = np.where(yoy_clean['YoY_Growth_Pct'] >= 0, 'Expansion (+)', 'Contraction (-)')
        yoy_clean['Display_Text'] = yoy_clean['YoY_Growth_Pct'].apply(lambda x: f"{x:+.1f}%")

        min_pct = yoy_clean['YoY_Growth_Pct'].min()
        max_pct = yoy_clean['YoY_Growth_Pct'].max()
        y_lower = min(0, min_pct) * 1.35 if min_pct < 0 else -2
        y_upper = max(0, max_pct) * 1.35 if max_pct > 0 else 5

        fig_yoy = px.bar(
            yoy_clean, x='Year', y='YoY_Growth_Pct', color='Growth_Color',
            color_discrete_map={'Expansion (+)': '#7FC4C3', 'Contraction (-)': '#F8D1C5'},
            labels={'YoY_Growth_Pct': 'Annual Growth Rate (%)', 'Year': 'Calendar Year'},
            text='Display_Text'
        )
        fig_yoy.add_hline(y=0, line_dash="solid", line_color="#1E293B", line_width=1.2)
        fig_yoy.update_traces(
            textposition='outside', cliponaxis=False,
            textfont=dict(size=11, family="'Plus Jakarta Sans', sans-serif", color='#1E293B'),
            marker_line_color='#1E293B', marker_line_width=0.8
        )
        fig_yoy.update_layout(
            **PLOT_THEME,
            height=440,
            bargap=0.28,
            margin=dict(l=55, r=25, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_yoy.update_yaxes(gridcolor='rgba(150, 172, 140, 0.22)', ticksuffix='%', range=[y_lower, y_upper], title_standoff=8)
        fig_yoy.update_xaxes(gridcolor='rgba(150, 172, 140, 0.22)', dtick=1, title_standoff=8)
        st.plotly_chart(fig_yoy, use_container_width=True)
        render_explanation(
            "Annual Year-over-Year Percentage Growth",
            "This chart shows annual harvest expansion and contraction percentages relative to the preceding year. "
            "Fern green bars indicate growth years, while marigold bars highlight agricultural contractions such as the severe 2013 shock."
        )
    else:
        st.warning("Insufficient data points to compute Year-over-Year growth rates. Expand the year horizon slider.")

def render_moving_average_content():
    if len(yearly_totals) >= 2:
        yoy_base = pd.DataFrame({'Year': yearly_totals.index, 'Volume_MT': yearly_totals.values})
        trend_df, t_stats = compute_trend_models(yoy_base)

        fig_smooth = go.Figure()
        fig_smooth.add_trace(go.Scatter(
            x=trend_df['Year'], y=trend_df['Volume_MT'], mode='lines+markers',
            name='Actual Annual Output', line=dict(color='#1E293B', width=2.8),
            marker=dict(size=8, color='#1E293B', line=dict(color='#FFFFFF', width=1.5))
        ))
        fig_smooth.add_trace(go.Scatter(
            x=trend_df['Year'], y=trend_df['SMA_3'], mode='lines',
            name='3-Year Moving Average (SMA-3)', line=dict(color='#7FC4C3', width=2.8, dash='dot')
        ))
        fig_smooth.add_trace(go.Scatter(
            x=trend_df['Year'], y=trend_df['Linear_Trend'], mode='lines',
            name=f"OLS Linear Trend (R² = {t_stats['r_squared']:.2f})", line=dict(color='#A7B7E5', width=2.8, dash='dash')
        ))
        fig_smooth.update_layout(
            **PLOT_THEME,
            height=460,
            hovermode="x unified",
            margin=dict(l=55, r=25, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255,255,255,0.95)")
        )
        fig_smooth.update_yaxes(gridcolor='rgba(150, 172, 140, 0.22)', tickformat=",.0f", title_standoff=8)
        fig_smooth.update_xaxes(gridcolor='rgba(150, 172, 140, 0.22)', dtick=1, title_standoff=8)
        st.plotly_chart(fig_smooth, use_container_width=True)
        render_explanation(
            "3-Year Moving Average & Long-Term Trendline",
            "This chart combines actual annual production with a 3-year smoothed rolling average and an Ordinary Least Squares (OLS) linear trendline. "
            "The smoothed series mitigates annual volatility to illustrate the true multi-year direction of Philippine banana output."
        )
    else:
        st.warning("Insufficient data points to compute rolling moving averages.")

def render_anomalies_scatter_content():
    if len(yearly_totals) >= 4:
        anom_base = pd.DataFrame({'Year': yearly_totals.index, 'Volume_MT': yearly_totals.values})
        anom_df = detect_statistical_anomalies(anom_base, z_thresh=1.4)

        anomaly_text = [str(y) if flag != 'Normal Production' else '' for y, flag in zip(anom_df['Year'], anom_df['Anomaly_Flag'])]

        fig_anom = px.scatter(
            anom_df, x='Year', y='Volume_MT', color='Anomaly_Flag',
            size=np.abs(anom_df['Z_Score']) + 3.0,
            color_discrete_map={
                'Normal Production': '#A7B7E5',
                'Unusually High Output': '#A7C4A0',
                'Unusually Low Shock': '#F8D1C5',
                'Unrecorded': '#CBD5E1'
            },
            labels={'Volume_MT': 'Harvest Volume (Metric Tons)', 'Year': 'Calendar Year'},
            text=anomaly_text
        )
        fig_anom.update_traces(
            textposition='top center',
            textfont=dict(size=12, family="'Plus Jakarta Sans', sans-serif", color='#1E293B'),
            marker=dict(line=dict(color='#1E293B', width=1.2))
        )
        
        v_mean = anom_base['Volume_MT'].mean()
        v_std = anom_base['Volume_MT'].std()
        fig_anom.add_hline(y=v_mean, line_color="#1E293B", line_width=1.8, annotation_text=f"Mean: {v_mean/1e3:.1f}K MT", annotation_position="top left")
        fig_anom.add_hline(y=v_mean + 1.4 * v_std, line_dash="dot", line_color="#A7C4A0", line_width=1.8, annotation_text="+1.4σ Upper Bound", annotation_position="top left")
        fig_anom.add_hline(y=max(0, v_mean - 1.4 * v_std), line_dash="dot", line_color="#F8D1C5", line_width=1.8, annotation_text="-1.4σ Lower Bound", annotation_position="bottom left")

        fig_anom.update_layout(
            **PLOT_THEME,
            height=460,
            margin=dict(l=55, r=25, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_anom.update_yaxes(gridcolor='rgba(150, 172, 140, 0.22)', tickformat=",.0f", title_standoff=8)
        fig_anom.update_xaxes(gridcolor='rgba(150, 172, 140, 0.22)', dtick=1, title_standoff=8)
        st.plotly_chart(fig_anom, use_container_width=True)
        render_explanation(
            "Statistical Anomaly & Shock Detection",
            "This scatter plot uses standardized Z-scores to objectively identify harvest years that deviated significantly from the historical average. "
            "Data points falling beyond the ±1.4σ threshold isolate major climatic shocks (e.g. Typhoon Nona) and exceptional agricultural boom years."
        )
    else:
        st.info("At least 4 observation years are required to compute statistical Z-score bounds.")

def render_forecasting_chart_content():
    st.markdown("""
    <div class="warning-banner">
        ⚠️ <b>Academic Disclaimer:</b> The projections below are <b>exploratory estimates</b> calculated using 
        Holt's Linear Trend Model for research planning. They are statistical projections and should not be treated as certified future yields.
    </div>
    """, unsafe_allow_html=True)

    fc_horizon = st.slider("Select Forecast Horizon (Years into future):", min_value=2, max_value=5, value=4)
    fc_base = pd.DataFrame({'Year': yearly_totals.index, 'Volume_MT': yearly_totals.values})
    
    forecast_results = run_time_series_forecast(fc_base, train_ratio=0.8, forecast_horizon=fc_horizon)

    if forecast_results is not None:
        metrics = forecast_results['eval_metrics']
        train_df = forecast_results['train_df']
        test_df = forecast_results['test_df']
        future_df = forecast_results['forecast_df']

        f1, f2, f3 = st.columns(3)
        with f1:
            st.markdown(f"""
            <div class="growth-kpi-card growth-kpi-cloud">
                <div class="growth-kpi-label">MAE (Mean Error)</div>
                <div class="growth-kpi-val">{metrics['MAE_MT']/1e3:,.1f}K <span class="unit-text">MT</span></div>
                <div class="growth-kpi-sub">Average error magnitude</div>
            </div>
            """, unsafe_allow_html=True)
        with f2:
            st.markdown(f"""
            <div class="growth-kpi-card growth-kpi-aqua">
                <div class="growth-kpi-label">RMSE (Std Error)</div>
                <div class="growth-kpi-val">{metrics['RMSE_MT']/1e3:,.1f}K <span class="unit-text">MT</span></div>
                <div class="growth-kpi-sub">Residual standard dev</div>
            </div>
            """, unsafe_allow_html=True)
        with f3:
            st.markdown(f"""
            <div class="growth-kpi-card growth-kpi-lavender">
                <div class="growth-kpi-label">MAPE (Accuracy)</div>
                <div class="growth-kpi-val">{metrics['MAPE_Pct']:.2f}%</div>
                <div class="growth-kpi-sub">Test accuracy (< 10% is strong)</div>
            </div>
            """, unsafe_allow_html=True)

        st.caption(f"🧪 **Validation Setup:** Trained on {metrics['Train_Years']} • Evaluated on held-out test data from {metrics['Test_Years']}.")

        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=train_df['Year'], y=train_df['Volume_MT'],
            mode='lines+markers', name='Historical Training Data',
            line=dict(color='#1E293B', width=2.6), marker=dict(size=7, color='#1E293B')
        ))
        fig_fc.add_trace(go.Scatter(
            x=test_df['Year'], y=test_df['Volume_MT'],
            mode='lines+markers', name='Actual Test Data (Holdout)',
            line=dict(color='#7FC4C3', width=2.6), marker=dict(size=8, symbol='diamond', color='#7FC4C3')
        ))
        fig_fc.add_trace(go.Scatter(
            x=test_df['Year'], y=test_df['Predicted_MT'],
            mode='lines+markers', name='Model Predictions',
            line=dict(color='#F8D1C5', width=2.2, dash='dot'), marker=dict(size=7, symbol='cross', color='#F8D1C5')
        ))
        fig_fc.add_trace(go.Scatter(
            x=future_df['Year'], y=future_df['Projected_MT'],
            mode='lines+markers', name='Projected Estimate (Forecast)',
            line=dict(color='#C9B4E6', width=2.8, dash='dash'),
            marker=dict(size=9, symbol='star', color='#C9B4E6', line=dict(color='#1E293B', width=1.2))
        ))
        fig_fc.add_trace(go.Scatter(
            x=list(future_df['Year']) + list(future_df['Year'])[::-1],
            y=list(future_df['Upper_CI_MT']) + list(future_df['Lower_CI_MT'])[::-1],
            fill='toself', fillcolor='rgba(201, 180, 230, 0.25)',
            line=dict(color='rgba(201, 180, 230, 0.50)', width=1, dash='dot'),
            hoverinfo="skip", showlegend=True, name='95% Confidence Interval'
        ))
        fig_fc.update_layout(
            **PLOT_THEME,
            height=480,
            xaxis_title="Calendar Year",
            yaxis_title="Volume of Production (Metric Tons)",
            hovermode="x unified",
            margin=dict(l=55, r=25, t=50, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(255,255,255,0.95)")
        )
        fig_fc.update_yaxes(gridcolor='rgba(150, 172, 140, 0.22)', tickformat=",.0f", title_standoff=8)
        fig_fc.update_xaxes(gridcolor='rgba(150, 172, 140, 0.22)', dtick=1, title_standoff=8)
        st.plotly_chart(fig_fc, use_container_width=True)
        render_explanation(
            "Exploratory Time-Series Production Forecast",
            "This forecasting chart models future banana harvest volume using Holt's Linear Exponential Smoothing. "
            "The shaded band represents the 95% confidence interval, illustrating the range of probable future outcomes."
        )
    else:
        st.warning("Insufficient continuous historical observations to train the time-series model. Please expand your year selection.")

def render_forecasting_table_content():
    fc_base = pd.DataFrame({'Year': yearly_totals.index, 'Volume_MT': yearly_totals.values})
    forecast_results = run_time_series_forecast(fc_base, train_ratio=0.8, forecast_horizon=4)
    if forecast_results is not None:
        future_df = forecast_results['forecast_df']
        st.dataframe(
            future_df[['Year', 'Projected_MT', 'Lower_CI_MT', 'Upper_CI_MT', 'Type']].style.format({
                'Projected_MT': '{:,.2f}',
                'Lower_CI_MT': '{:,.2f}',
                'Upper_CI_MT': '{:,.2f}'
            }),
            use_container_width=True,
            column_config={
                "Year": st.column_config.NumberColumn("Calendar Year", format="%d"),
                "Projected_MT": st.column_config.NumberColumn("Projected Estimate (Metric Tons)", format="%,.2f MT"),
                "Lower_CI_MT": st.column_config.NumberColumn("Lower 95% Confidence Bound (MT)", format="%,.2f MT"),
                "Upper_CI_MT": st.column_config.NumberColumn("Upper 95% Confidence Bound (MT)", format="%,.2f MT"),
                "Type": st.column_config.TextColumn("Projection Type")
            }
        )
        render_explanation(
            "Projected Scenario Table",
            "This table outlines statistical projection estimates for upcoming calendar years alongside lower and upper 95% confidence bounds. "
            "Agricultural planners can use these estimates to plan interventions, seed propagation, and cooperative resource allocation."
        )
    else:
        st.warning("Insufficient historical data to generate scenario estimates table.")

def render_anomalies_table_content():
    if len(yearly_totals) >= 4:
        anom_base = pd.DataFrame({'Year': yearly_totals.index, 'Volume_MT': yearly_totals.values})
        anom_df = detect_statistical_anomalies(anom_base, z_thresh=1.4)
        flagged_rows = anom_df[anom_df['Anomaly_Flag'] != 'Normal Production']
        if not flagged_rows.empty:
            display_flags = flagged_rows[['Year', 'Volume_MT', 'Z_Score', 'Anomaly_Flag']].copy()
            st.dataframe(
                display_flags.style.format({'Volume_MT': '{:,.2f}', 'Z_Score': '{:+.2f}'}),
                use_container_width=True,
                column_config={
                    "Year": st.column_config.NumberColumn("Calendar Year", format="%d"),
                    "Volume_MT": st.column_config.NumberColumn("Harvest Volume (Metric Tons)", format="%,.2f MT"),
                    "Z_Score": st.column_config.NumberColumn("Standardized Z-Score", format="%+,.2f"),
                    "Anomaly_Flag": st.column_config.TextColumn("Statistical Classification")
                }
            )
            render_explanation(
                "Flagged Anomaly Summary Table",
                "This audit table catalogs all calendar years classified as statistically unusual within the active filter scope. "
                "It enables agricultural evaluators to cross-reference historical yields with verified typhoons, droughts, and disease outbreaks."
            )
        else:
            st.success("All observed production years in this selection remain within standard statistical variance bounds (between -1.4σ and +1.4σ).")
    else:
        st.info("At least 4 observation years are required to compute statistical Z-score bounds.")

def render_records_table_content():
    table_display = active_df[['Year', 'Period', 'Crop', 'Region', 'Province_City', 'Volume_MT', 'Data_Status']].sort_values(by=['Year', 'Crop'], ascending=[False, True])
    st.dataframe(
        table_display.style.format({'Volume_MT': '{:,.2f}'}),
        use_container_width=True,
        height=400,
        column_config={
            "Year": st.column_config.NumberColumn("Calendar Year", format="%d", width="small"),
            "Period": st.column_config.TextColumn("Reporting Period", width="small"),
            "Crop": st.column_config.TextColumn("Banana Variety", width="medium"),
            "Region": st.column_config.TextColumn("Administrative Region", width="large"),
            "Province_City": st.column_config.TextColumn("Province / City", width="medium"),
            "Volume_MT": st.column_config.NumberColumn("Volume (Metric Tons)", format="%,.2f MT", width="medium"),
            "Data_Status": st.column_config.TextColumn("Data Audit Status", width="small")
        }
    )
    render_explanation(
        "Official Production Records Explorer",
        "This interactive table presents verified PSA statistical records matching your active filter criteria. "
        "Users can sort any column, search by variety or province, and download the filtered records directly as a spreadsheet."
    )
    csv_bytes = table_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Filtered Records as CSV",
        data=csv_bytes,
        file_name=f"bananascope_filtered_{selected_years[0]}_{selected_years[1]}.csv",
        mime="text/csv"
    )

def render_math_methodology_content():
    st.markdown("""
    <div class="math-methodology-card">
        <p style="font-size: 0.90rem; font-weight: 700; color: #1E293B; margin-bottom: 12px;">
            This section documents the formal mathematical and statistical formulations implemented in the <b>BananaScope PH Analytics Engine</b>:
        </p>
        <div style="font-size: 0.88rem; font-weight: 800; color: #1E293B; margin-top: 10px;">1. Year-over-Year (YoY) Growth Rate</div>
        <p style="font-size: 0.84rem; color: #1E293B; margin: 4px 0 8px 0;">Formula: &Delta;V<sub>t</sub> = V<sub>t</sub> &minus; V<sub>t&minus;1</sub>, &emsp; YoY Growth (%) = ((V<sub>t</sub> &minus; V<sub>t&minus;1</sub>) / V<sub>t&minus;1</sub>) &times; 100</p>
        
        <div style="font-size: 0.88rem; font-weight: 800; color: #1E293B; margin-top: 10px;">2. Compound Annual Growth Rate (CAGR)</div>
        <p style="font-size: 0.84rem; color: #1E293B; margin: 4px 0 8px 0;">Formula: CAGR = (V<sub>end</sub> / V<sub>start</sub>)<sup>1/n</sup> &minus; 1</p>
        
        <div style="font-size: 0.88rem; font-weight: 800; color: #1E293B; margin-top: 10px;">3. Ordinary Least Squares (OLS) Linear Trend</div>
        <p style="font-size: 0.84rem; color: #1E293B; margin: 4px 0 8px 0;">Formula: &ycirc;<sub>t</sub> = &beta;<sub>0</sub> + &beta;<sub>1</sub>t, &emsp; R<sup>2</sup> = 1 &minus; (&sum;(y<sub>i</sub> &minus; &ycirc;<sub>i</sub>)<sup>2</sup> / &sum;(y<sub>i</sub> &minus; y&#772;)<sup>2</sup>)</p>
        
        <div style="font-size: 0.88rem; font-weight: 800; color: #1E293B; margin-top: 10px;">4. Statistical Anomaly & Outlier Detection (Z-Score)</div>
        <p style="font-size: 0.84rem; color: #1E293B; margin: 4px 0 8px 0;">Formula: Z<sub>t</sub> = (V<sub>t</sub> &minus; &mu;) / &sigma; &emsp; (Boom: Z<sub>t</sub> &gt; +1.4, Shock: Z<sub>t</sub> &lt; &minus;1.4)</p>
        
        <div style="font-size: 0.88rem; font-weight: 800; color: #1E293B; margin-top: 10px;">5. Double Exponential Smoothing (Holt's Linear Forecast)</div>
        <p style="font-size: 0.84rem; color: #1E293B; margin: 4px 0 8px 0;">Formula: &ell;<sub>t</sub> = &alpha;y<sub>t</sub> + (1 &minus; &alpha;)(&ell;<sub>t&minus;1</sub> + b<sub>t&minus;1</sub>), &emsp; b<sub>t</sub> = &beta;(&ell;<sub>t</sub> &minus; &ell;<sub>t&minus;1</sub>) + (1 &minus; &beta;)b<sub>t&minus;1</sub>, &emsp; &ycirc;<sub>t+h</sub> = &ell;<sub>t</sub> + hb<sub>t</sub><br>
        <span style="font-size: 0.78rem; color: #556270;">Parameters: Smoothing weight &alpha; = 0.6, Trend weight &beta; = 0.2</span></p>
        
        <div style="font-size: 0.88rem; font-weight: 800; color: #1E293B; margin-top: 10px;">6. Forecast Accuracy Metrics</div>
        <p style="font-size: 0.84rem; color: #1E293B; margin: 4px 0 4px 0;">MAE = (1/n)&sum;|y<sub>i</sub> &minus; &ycirc;<sub>i</sub>|, &emsp; RMSE = &radic;((1/n)&sum;(y<sub>i</sub> &minus; &ycirc;<sub>i</sub>)<sup>2</sup>), &emsp; MAPE = (100%/n)&sum;|(y<sub>i</sub> &minus; &ycirc;<sub>i</sub>)/y<sub>i</sub>|</p>
    </div>
    """, unsafe_allow_html=True)
    render_explanation(
        "Mathematical Formulations & Statistical Methods",
        "This section documents the formal mathematical equations powering BananaScope PH's calculations. "
        "All growth, regression, anomaly detection, and exponential smoothing algorithms follow standard statistical methodologies."
    )


# =============================================================================
# 9. MAIN CONTENT ROUTER BY CATEGORY
# =============================================================================

st.markdown("<div class='fade-in-view'>", unsafe_allow_html=True)

# ----------------- CATEGORY 1: HOME (MAIN DASHBOARD OVERVIEW) -----------------
if st.session_state.active_category == "HOME":
    # 1. Buff Header Card
    st.markdown("""
    <div class="hero-banner">
        <h1 class="dashboard-title">
            <span>🍌</span> BananaScope PH
        </h1>
        <p class="hero-subtitle">
            Philippine Banana Production Analytics Platform (2010–2026)
        </p>
        <div class="hero-badges-container">
            <span class="hero-pill-badge badge-peach">🌾 Official PSA OpenStat</span>
            <span class="hero-pill-badge badge-sage">🌿 15-Year Scope (2010–2024)</span>
            <span class="hero-pill-badge badge-aqua">📊 17 Regions Benchmarked</span>
            <span class="hero-pill-badge badge-cloud">🔮 Forecast Horizon to 2028</span>
            <span class="hero-pill-badge badge-lavender">🏛️ DepEd MIMAROPA Capstone</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Concise Surveillance Summary Callout
    if not active_df.empty and len(yearly_totals) > 1:
        start_y = yearly_totals.index.min()
        end_y = yearly_totals.index.max()
        v_start = yearly_totals.loc[start_y]
        v_end = yearly_totals.loc[end_y]
        pct_change = ((v_end - v_start) / v_start) * 100 if v_start > 0 else 0
        cagr_val = calculate_cagr(v_start, v_end, end_y - start_y)
        dir_text = "net expansion" if pct_change >= 0 else "net contraction"
        
        st.markdown(f"""
        <div class="insights-card">
            <div class="insights-title">💡 Production Surveillance Overview: {geo_label}</div>
            <div class="insights-body">
                Between <b>{start_y}</b> and <b>{end_y}</b>, banana production in <b>{geo_label}</b> recorded a 
                <b>{dir_text} of {abs(pct_change):.1f}%</b> (CAGR: <b>{cagr_val:+.2f}%/yr</b>). 
                Peak production reached <b>{peak_vol_mt/1e3:,.1f}K MT in {peak_year}</b>, while lowest recorded volume was 
                <b>{lowest_vol_mt/1e3:,.1f}K MT in {lowest_year}</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3. STRICT 2x2 EQUAL-SIZED KPI CARDS (Balanced 4-Color Spread)
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        st.markdown(f"""
        <div class="kpi-card-rect kpi-peach">
            <div class="kpi-header">
                <span class="kpi-label-rect">Total Production Volume</span>
                <span class="kpi-icon-rect" >🍌</span>
            </div>
            <div class="kpi-value-rect">{total_production_mt/1e6:.2f}M <span class="unit-text">MT</span></div>
            <div class="kpi-subtext-rect">📍 Scope: {geo_label} ({total_production_mt:,.0f} MT)</div>
        </div>
        """, unsafe_allow_html=True)

    with row1_c2:
        st.markdown(f"""
        <div class="kpi-card-rect kpi-cream">
            <div class="kpi-header">
                <span class="kpi-label-rect">Average Annual Production</span>
                <span class="kpi-icon-rect">⚖️</span>
            </div>
            <div class="kpi-value-rect">{avg_annual_mt/1e6:.2f}M <span class="unit-text">MT / yr</span></div>
            <div class="kpi-subtext-rect">📅 Average across {selected_years[1] - selected_years[0] + 1} years ({selected_years[0]}–{selected_years[1]})</div>
        </div>
        """, unsafe_allow_html=True)

    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        st.markdown(f"""
        <div class="kpi-card-rect kpi-sage">
            <div class="kpi-header">
                <span class="kpi-label-rect">Peak Harvest Year</span>
                <span class="kpi-icon-rect" >🏆</span>
            </div>
            <div class="kpi-value-rect">{peak_year}</div>
            <div class="kpi-subtext-rect">📈 Peak: {peak_vol_mt/1e6:.2f}M MT (Lowest: {lowest_vol_mt/1e6:.2f}M in {lowest_year})</div>
        </div>
        """, unsafe_allow_html=True)

    with row2_c2:
        st.markdown(f"""
        <div class="kpi-card-rect kpi-cloud">
            <div class="kpi-header">
                <span class="kpi-label-rect">Leading Banana Region</span>
                <span class="kpi-icon-rect" >🗺️</span>
            </div>
            <div class="kpi-value-rect" style="font-size: 1.70rem;">{top_region_name}</div>
            <div class="kpi-subtext-rect">🌾 Output: {top_region_vol/1e6:.2f}M MT (54% National Share)</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Consolidated Analytical Scope & Research Framework (Aligned & Space Maximized)
    st.markdown("""
    <div class="bottom-modules-container">
        <div class="bottom-modules-header">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.10rem;">📋</span>
                <span style="font-size: 0.95rem; font-weight: 800; color: var(--text-dark);">Analytical Modules & Research Coverage</span>
            </div>
            <span class="header-badge-lavender">84,133 Verified Observations • PSA OpenStat (2010–2024)</span>
        </div>
        <p style="font-size: 0.82rem; color: var(--text-muted); margin: 4px 0 12px 0; line-height: 1.45;">
            BananaScope PH synthesizes <b>84,133 verified observations</b> from the Philippine Statistics Authority across 17 administrative regions.
            Access each analytical module directly via the left sidebar navigation menu:
        </p>
        <div class="bottom-modules-grid">
            <div class="bottom-module-box box-peach">
                <div class="box-top">
                    <span class="box-tag" >Module 1</span>
                    <div class="box-title">📈 Production Overview</div>
                </div>
                <div class="box-desc">15-Year historical volume trajectory and quarterly harvest seasonality patterns.</div>
                <div class="box-meta">⏱️ Trajectory & Seasonality</div>
            </div>
            <div class="bottom-module-box box-cream">
                <div class="box-top">
                    <span class="box-tag" style="background: var(--sunlit-cream); border-color: var(--sunlit-cream-border);">Module 2</span>
                    <div class="box-title">🗺️ Regional Rankings</div>
                </div>
                <div class="box-desc">Geographic production shares across 17 administrative regions led by Davao Region.</div>
                <div class="box-meta">📍 17 PH Regions Benchmarked</div>
            </div>
            <div class="bottom-module-box box-sage">
                <div class="box-top">
                    <span class="box-tag" >Module 3</span>
                    <div class="box-title">🍌 Variety Analysis</div>
                </div>
                <div class="box-desc">Market share breakdown and multi-year trajectories for Cavendish, Saba, Lacatan, Bungulan.</div>
                <div class="box-meta">🌿 4 Major Cultivars</div>
            </div>
            <div class="bottom-module-box box-aqua">
                <div class="box-top">
                    <span class="box-tag" style="background: var(--aqua-breeze); border-color: var(--aqua-breeze-border);">Module 4</span>
                    <div class="box-title">📊 Trends & Forecast</div>
                </div>
                <div class="box-desc">YoY growth rates, 3-year smoothed trendlines, Z-score anomaly shocks, and Holt's models.</div>
                <div class="box-meta">🔮 Projections to 2028</div>
            </div>
            <div class="bottom-module-box box-cloud">
                <div class="box-top">
                    <span class="box-tag" >Module 5</span>
                    <div class="box-title">📑 Records & Methods</div>
                </div>
                <div class="box-desc">Searchable PSA records database, anomaly audit tables, forecast spreadsheets, and math formulas.</div>
                <div class="box-meta">📐 Methodology & Data Explorer</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ----------------- CATEGORY 2: PRODUCTION OVERVIEW & SEASONALITY -------------
elif st.session_state.active_category == "PROD":
    # Sub-Navigation Pills
    p1, p2, _ = st.columns([1.2, 1.2, 2.5])
    with p1:
        is_t1 = (st.session_state.prod_subview == "TRAJECTORY")
        if st.button("📈 Annual Trajectory", key="pill_prod_traj", type="primary" if is_t1 else "secondary", use_container_width=True):
            st.session_state.prod_subview = "TRAJECTORY"
            st.rerun()
    with p2:
        is_t2 = (st.session_state.prod_subview == "SEASONALITY")
        if st.button("⏱️ Quarterly Harvest", key="pill_prod_seas", type="primary" if is_t2 else "secondary", use_container_width=True):
            st.session_state.prod_subview = "SEASONALITY"
            st.rerun()

    if st.session_state.prod_subview == "TRAJECTORY":
        render_view_header("ANNUAL_TRAJECTORY")
        render_annual_trajectory_content()
        render_view_footer("ANNUAL_TRAJECTORY")
    else:
        render_view_header("QUARTERLY_SEASONALITY")
        render_quarterly_seasonality_content()
        render_view_footer("QUARTERLY_SEASONALITY")


# ----------------- CATEGORY 3: REGIONAL & GEOGRAPHIC RANKINGS ----------------
elif st.session_state.active_category == "REG":
    render_view_header("REGIONAL_RANKINGS")
    render_regional_rankings_content()
    render_view_footer("REGIONAL_RANKINGS")


# ----------------- CATEGORY 4: BANANA VARIETY ANALYSIS -----------------------
elif st.session_state.active_category == "VAR":
    # Sub-Navigation Pills
    p1, p2, _ = st.columns([1.4, 1.4, 2.2])
    with p1:
        is_v1 = (st.session_state.var_subview == "DONUT")
        if st.button("🍌 Variety Market Share", key="pill_var_donut", type="primary" if is_v1 else "secondary", use_container_width=True):
            st.session_state.var_subview = "DONUT"
            st.rerun()
    with p2:
        is_v2 = (st.session_state.var_subview == "TRENDS")
        if st.button("🌿 Variety Multi-Year Trends", key="pill_var_trends", type="primary" if is_v2 else "secondary", use_container_width=True):
            st.session_state.var_subview = "TRENDS"
            st.rerun()

    if st.session_state.var_subview == "DONUT":
        render_view_header("CULTIVAR_DONUT")
        render_cultivar_donut_content()
        render_view_footer("CULTIVAR_DONUT")
    else:
        render_view_header("VARIETY_COMPARISON")
        render_variety_comparison_content()
        render_view_footer("VARIETY_COMPARISON")


# ----------------- CATEGORY 5: GROWTH RATES, TRENDLINES & FORECASTING ---------
elif st.session_state.active_category == "TREND":
    # Sub-Navigation Pills
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        is_tr1 = (st.session_state.trend_subview == "YOY")
        if st.button("📊 YoY % Growth", key="pill_trend_yoy", type="primary" if is_tr1 else "secondary", use_container_width=True):
            st.session_state.trend_subview = "YOY"
            st.rerun()
    with p2:
        is_tr2 = (st.session_state.trend_subview == "SMOOTH")
        if st.button("🌾 3-Yr Trendline", key="pill_trend_smooth", type="primary" if is_tr2 else "secondary", use_container_width=True):
            st.session_state.trend_subview = "SMOOTH"
            st.rerun()
    with p3:
        is_tr3 = (st.session_state.trend_subview == "ANOMALIES")
        if st.button("🔍 Anomaly Shocks", key="pill_trend_anom", type="primary" if is_tr3 else "secondary", use_container_width=True):
            st.session_state.trend_subview = "ANOMALIES"
            st.rerun()
    with p4:
        is_tr4 = (st.session_state.trend_subview == "FORECAST")
        if st.button("🔮 Future Forecast", key="pill_trend_fc", type="primary" if is_tr4 else "secondary", use_container_width=True):
            st.session_state.trend_subview = "FORECAST"
            st.rerun()

    if st.session_state.trend_subview == "YOY":
        render_view_header("YOY_GROWTH")
        render_yoy_growth_content()
        render_view_footer("YOY_GROWTH")
    elif st.session_state.trend_subview == "SMOOTH":
        render_view_header("MOVING_AVERAGE")
        render_moving_average_content()
        render_view_footer("MOVING_AVERAGE")
    elif st.session_state.trend_subview == "ANOMALIES":
        render_view_header("ANOMALIES_SCATTER")
        render_anomalies_scatter_content()
        render_view_footer("ANOMALIES_SCATTER")
    else:
        render_view_header("FORECAST_CHART")
        render_forecasting_chart_content()
        render_view_footer("FORECAST_CHART")


# ----------------- CATEGORY 6: STRUCTURED TABLES & METHODOLOGY ----------------
elif st.session_state.active_category == "REC":
    # Sub-Navigation Pills
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        is_r1 = (st.session_state.rec_subview == "FC_TABLE")
        if st.button("📋 Forecast Table", key="pill_rec_fc", type="primary" if is_r1 else "secondary", use_container_width=True):
            st.session_state.rec_subview = "FC_TABLE"
            st.rerun()
    with p2:
        is_r2 = (st.session_state.rec_subview == "ANOM_TABLE")
        if st.button("⚠️ Anomaly Table", key="pill_rec_anom", type="primary" if is_r2 else "secondary", use_container_width=True):
            st.session_state.rec_subview = "ANOM_TABLE"
            st.rerun()
    with p3:
        is_r3 = (st.session_state.rec_subview == "RECORDS")
        if st.button("📑 Records Explorer", key="pill_rec_records", type="primary" if is_r3 else "secondary", use_container_width=True):
            st.session_state.rec_subview = "RECORDS"
            st.rerun()
    with p4:
        is_r4 = (st.session_state.rec_subview == "MATH")
        if st.button("📐 Methodology", key="pill_rec_math", type="primary" if is_r4 else "secondary", use_container_width=True):
            st.session_state.rec_subview = "MATH"
            st.rerun()

    if st.session_state.rec_subview == "FC_TABLE":
        render_view_header("FORECAST_TABLE")
        render_forecasting_table_content()
        render_view_footer("FORECAST_TABLE")
    elif st.session_state.rec_subview == "ANOM_TABLE":
        render_view_header("ANOMALIES_TABLE")
        render_anomalies_table_content()
        render_view_footer("ANOMALIES_TABLE")
    elif st.session_state.rec_subview == "RECORDS":
        render_view_header("RECORDS_TABLE")
        render_records_table_content()
        render_view_footer("RECORDS_TABLE")
    else:
        render_view_header("MATH_METHODOLOGY")
        render_math_methodology_content()
        render_view_footer("MATH_METHODOLOGY")

st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 10. DASHBOARD FOOTER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="dashboard-footer">
    🍌 <strong>BananaScope PH</strong> • Philippine Banana Production Analytics Platform (2010–2026)<br>
    Senior High School Capstone Project • <strong>Leuteboro National High School</strong> (Socorro, Oriental Mindoro)<br>
    Research Team: <strong>Krishia Mae R. Layag</strong>, <strong>Ann Ehra V. Avelino</strong>, and <strong>Hannah Aeshell V. Perez</strong><br>
    Supervised by <strong>Sir Aldrin D. Magtibay, Teacher V</strong> • Department of Education MIMAROPA
</div>
""", unsafe_allow_html=True)
