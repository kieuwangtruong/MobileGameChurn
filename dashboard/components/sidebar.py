"""Sidebar filter component with Dark & Light Mode Toggle."""
from typing import Tuple
import pandas as pd
import streamlit as st


def render_sidebar(df_players: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
    """Render Sidebar filters and Theme Switcher, returning (df_filtered, is_dark)."""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand-box">
            <div class="tesla-logo-text">LIVEOPS</div>
            <div class="sidebar-brand-title" style="margin-top: 4px;">Game Intelligence</div>
            <div class="sidebar-brand-subtitle">Studio Edition</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 10px; padding: 8px 12px; margin-bottom: 18px; font-size: 0.78rem; color: #A5B4FC; display: flex; align-items: center; gap: 6px; font-weight: 600;">
            <span>🌙</span> Cyber Dark Studio Active
        </div>
        """, unsafe_allow_html=True)
        is_dark = True
        st.markdown("##### 🎛️ BỘ LỌC DỮ LIỆU")

        all_genres = sorted(df_players['GameGenre'].dropna().unique().tolist())
        selected_genres = st.multiselect("Thể loại game (Genre):", all_genres, default=all_genres)

        all_locations = sorted(df_players['Location'].dropna().unique().tolist())
        selected_locations = st.multiselect("Thị trường / Khu vực:", all_locations, default=all_locations)

        spender_filter = st.radio("Phân khúc người chơi:", ["Tất cả", "Chỉ Spender (Có Nạp)", "Chỉ F2P (Miễn Phí)"])

        st.markdown("---")
        card_bg = "#1E293B" if is_dark else "#F8FAFC"
        border_col = "rgba(255,255,255,0.12)" if is_dark else "#E2E8F0"
        title_col = "#F8FAFC" if is_dark else "#0F172A"
        text_col = "#CBD5E1" if is_dark else "#475569"

        st.markdown(f"""
        <div style="background: {card_bg}; border: 1px solid {border_col}; border-radius: 12px; padding: 14px; font-size: 0.8rem; color: {text_col};">
            <div style="font-weight: 700; color: {title_col}; margin-bottom: 6px;">🤖 AI MODEL ENGINE</div>
            <div>• <b>Model:</b> XGBoost Classifier</div>
            <div>• <b>Accuracy:</b> 95.45%</div>
            <div>• <b>Recall:</b> 89.10%</div>
            <div>• <b>Inference:</b> In-memory cache</div>
        </div>
        """, unsafe_allow_html=True)

    # Filter logic
    df_filtered = df_players[
        (df_players['GameGenre'].isin(selected_genres)) &
        (df_players['Location'].isin(selected_locations))
    ]
    if spender_filter == "Chỉ Spender (Có Nạp)":
        df_filtered = df_filtered[df_filtered['InGamePurchases'] == 1]
    elif spender_filter == "Chỉ F2P (Miễn Phí)":
        df_filtered = df_filtered[df_filtered['InGamePurchases'] == 0]

    return df_filtered, is_dark
