"""Streamlit Application: Mobile Game Churn Analytics & LiveOps AI Studio."""
import sys
from pathlib import Path
import streamlit as st

# Đảm bảo đường dẫn root có thể import modules
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# 1. Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Mobile Game LiveOps & Churn Studio",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Nạp CSS cơ sở (Design System)
css_path = BASE_DIR / "dashboard" / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. Tải Dữ liệu và Mô hình qua Services
from dashboard.services.data_service import load_game_dataset
from dashboard.services.inference_service import load_ml_predictor
from dashboard.components.sidebar import render_sidebar
from dashboard.views.executive_view import render_executive_view
from dashboard.views.simulator_view import render_simulator_view
from dashboard.views.liveops_view import render_liveops_view
from dashboard.views.explainability_view import render_explainability_view

try:
    df_players = load_game_dataset()
    predictor = load_ml_predictor()
except Exception as e:
    st.error(f"❌ Lỗi khởi tạo hệ thống: {e}")
    st.stop()

# 4. Render Sidebar (Lấy tập dữ liệu đã lọc và trạng thái Dark Mode)
df_filtered, is_dark = render_sidebar(df_players)

# 5. Áp dụng Overrides CSS thích ứng Dark & Light Mode
if is_dark:
    st.markdown("""
    <style>
    :root {
        --bg-canvas: #0B0F19 !important;
        --bg-card: #111827 !important;
        --bg-subtle: #1E293B !important;
        --border-color: rgba(255, 255, 255, 0.12) !important;
        --border-subtle: rgba(255, 255, 255, 0.08) !important;
        --text-primary: #F8FAFC !important;
        --text-secondary: #CBD5E1 !important;
        --text-muted: #94A3B8 !important;
        --brand-blue: #6366F1 !important;
        --brand-blue-light: rgba(99, 102, 241, 0.15) !important;
        --brand-blue-border: rgba(99, 102, 241, 0.35) !important;
    }
    .stApp {
        background: radial-gradient(circle at 15% 10%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 85% 20%, rgba(6, 182, 212, 0.06) 0%, transparent 35%),
                    #0B0F19 !important;
        color: #F8FAFC !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0D121F !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"], .tesla-card, .topic-container {
        background-color: #111827 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.45) !important;
    }
    .tesla-page-title, .topic-title, .tesla-card-val,
    [data-testid="stVerticalBlockBorderWrapper"] h4,
    [data-testid="stVerticalBlockBorderWrapper"] h5 {
        color: #F8FAFC !important;
    }
    .tesla-page-subtitle, .tesla-card-label {
        color: #94A3B8 !important;
    }
    /* Widget Labels & Radio/Slider Text */
    label, label p, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
        color: #F8FAFC !important;
        font-weight: 600 !important;
    }
    div[data-testid="stRadio"] label p, div[data-testid="stRadio"] label span {
        color: #F8FAFC !important;
        font-weight: 500 !important;
    }
    div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
        color: #38BDF8 !important;
        font-weight: 700 !important;
    }
    div[data-testid="stSliderTickBar"] span {
        color: #94A3B8 !important;
    }
    /* Inputs, Selectboxes & Number Inputs */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input {
        background-color: #1E293B !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        color: #F8FAFC !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] span {
        color: #F8FAFC !important;
    }
    div[data-baseweb="select"] svg {
        fill: #CBD5E1 !important;
    }
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        background-color: #1E293B !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        color: #F8FAFC !important;
    }
    button[data-testid="stNumberInputStepDown"] svg,
    button[data-testid="stNumberInputStepUp"] svg {
        fill: #F8FAFC !important;
        stroke: #F8FAFC !important;
    }
    ul[data-baseweb="menu"], div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #111827 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
    }
    li[data-baseweb="menu-item"] {
        background-color: #111827 !important;
        color: #F8FAFC !important;
    }
    li[data-baseweb="menu-item"]:hover {
        background-color: #1E293B !important;
        color: #818CF8 !important;
    }
    div[data-baseweb="tag"] {
        background-color: #312E81 !important;
        border: 1px solid #4F46E5 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="tag"] span {
        color: #E0E7FF !important;
    }
    /* Hero Form Submit Button */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 50%, #06B6D4 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.04em !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.45) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(99, 102, 241, 0.65) !important;
    }
    div[data-testid="stFormSubmitButton"] > button p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #111827 !important;
        border-color: rgba(255, 255, 255, 0.08) !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #818CF8 !important;
        border: 1px solid rgba(99, 102, 241, 0.4) !important;
    }
    .action-callout {
        background: rgba(99, 102, 241, 0.12) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
        border-left: 4px solid #6366F1 !important;
    }
    .action-callout-title {
        color: #A5B4FC !important;
    }
    .action-callout-body {
        color: #F1F5F9 !important;
    }
    [data-testid="stDataFrame"] {
        filter: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 6. Header phong cách Cyber Gaming Studio
st.markdown("""
<div class="tesla-header-bar">
    <div class="tesla-header-left">
        <div>
            <h1 class="tesla-page-title" style="color: #F8FAFC;">Reports & LiveOps Intelligence</h1>
            <p class="tesla-page-subtitle" style="color: #94A3B8;">
                Mobile Game Player Retention, Churn Risk Radar & Targeted LiveOps Studio
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 7. Cấu trúc Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Reports & KPIs (Tổng quan)",
    "🎯 AI Simulator (Mô phỏng Churn)",
    "⚡ LiveOps Action (Can thiệp & Xuất)",
    "🧠 Model Explainability (SHAP)"
])

with tab1:
    render_executive_view(df_filtered, is_dark=is_dark)

with tab2:
    render_simulator_view(predictor, is_dark=is_dark)

with tab3:
    render_liveops_view(df_players, is_dark=is_dark)

with tab4:
    render_explainability_view(is_dark=is_dark)
