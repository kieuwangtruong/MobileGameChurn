"""LiveOps Action Center & Retention Target Center View (Tab 3) - Adaptive Theme."""
import pandas as pd
import streamlit as st


def render_liveops_view(df_players: pd.DataFrame, is_dark: bool = True):
    """Hiển thị toàn bộ nội dung Tab 3 (Dark Gaming Studio Theme)."""
    title_color = "#F8FAFC"
    sub_color = "#94A3B8"

    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h3 style="margin-bottom: 6px; color: {title_color}; font-weight: 800; font-size: 1.45rem;">
            ⚡ LiveOps Retention Target Center
        </h3>
        <p style="color: {sub_color}; font-size: 0.92rem; margin: 0; font-weight: 500;">
            Truy xuất và lọc danh sách game thủ có nguy cơ rời bỏ cao để đồng bộ sang hệ thống CRM, gửi Push Notification, kích hoạt Giftcode hoặc nhiệm vụ giữ chân.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1. Bộ lọc phân khúc mục tiêu (Native Container)
    with st.container(border=True):
        st.markdown("#### 🎯 Tiêu Chí Phân Khúc Chiến Dịch")

        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            target_risk = st.multiselect(
                "Phân tầng nguy cơ rời bỏ:",
                ["Critical Risk", "Medium Risk", "Low Risk"],
                default=["Critical Risk"]
            )
        with col_t2:
            target_spender = st.selectbox(
                "Phân khúc thanh toán (Monetization):",
                ["Tất cả người chơi", "Chỉ Spenders (VIP & Nạp)", "Chỉ F2P (Người chơi miễn phí)"]
            )
        with col_t3:
            max_rows = st.number_input("Số lượng bản ghi tối đa xuất ra:", min_value=10, max_value=10000, value=200, step=50)

    # Áp dụng bộ lọc cho Action list
    df_action = df_players[df_players['Predicted_Risk_Tier'].isin(target_risk)].copy()
    if target_spender == "Chỉ Spenders (VIP & Nạp)":
        df_action = df_action[df_action['InGamePurchases'] == 1]
    elif target_spender == "Chỉ F2P (Người chơi miễn phí)":
        df_action = df_action[df_action['InGamePurchases'] == 0]

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. LiveOps Quick Stats Banner (Tesla Cards)
    matched_count = len(df_action)
    spender_in_list = int(df_action['InGamePurchases'].sum()) if matched_count > 0 else 0
    est_value_saved = spender_in_list * 25.0  # ARPU $25

    col_m1, col_m2, col_m3 = st.columns(3)
    val_blue = "#60A5FA" if is_dark else "#2563EB"
    val_green = "#34D399" if is_dark else "#059669"
    val_amber = "#FBBF24" if is_dark else "#D97706"

    with col_m1:
        st.markdown(f"""
        <div class="tesla-card">
            <div class="tesla-card-label">Target Audience Size</div>
            <div class="tesla-card-val" style="color: {val_blue}; font-size: 1.8rem;">{matched_count:,}</div>
            <div class="tesla-card-sub">Game thủ khớp tiêu chí lọc</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="tesla-card">
            <div class="tesla-card-label">High-Value Spenders</div>
            <div class="tesla-card-val" style="color: {val_green}; font-size: 1.8rem;">{spender_in_list:,}</div>
            <div class="tesla-card-sub">Tỷ lệ: {(spender_in_list/max(1, matched_count)*100):.1f}% tổng tệp</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"""
        <div class="tesla-card">
            <div class="tesla-card-label">Est. Retention Revenue</div>
            <div class="tesla-card-val" style="color: {val_amber}; font-size: 1.8rem;">${est_value_saved:,.0f}</div>
            <div class="tesla-card-sub">Ước tính doanh thu giữ chân/tháng</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 3. Bảng dữ liệu tương tác định dạng chuẩn
    display_cols = [
        'PlayerID', 'GameGenre', 'PlayerLevel', 'PlayTimeHours',
        'InGamePurchases', 'TotalWeeklyMinutes', 'Churn_Probability',
        'Predicted_Risk_Tier', 'Retention_Action_Plan'
    ]

    df_show = df_action[display_cols].head(int(max_rows)).copy()

    with st.container(border=True):
        badge_color = "#38BDF8" if is_dark else "#2563EB"
        st.markdown(
            f"#### 📋 Danh Sách Mục Tiêu <span style='color: {badge_color}; font-weight: 700;'>({len(df_action):,} Game Thủ)</span>",
            unsafe_allow_html=True
        )
        st.dataframe(
            df_show,
            use_container_width=True,
            height=380,
            column_config={
                "PlayerID": st.column_config.NumberColumn("Player ID", format="%d"),
                "GameGenre": st.column_config.TextColumn("Genre"),
                "PlayerLevel": st.column_config.NumberColumn("Level"),
                "PlayTimeHours": st.column_config.NumberColumn("Play Time (h)", format="%.1f h"),
                "InGamePurchases": st.column_config.CheckboxColumn("Spender?"),
                "TotalWeeklyMinutes": st.column_config.NumberColumn("Weekly Mins", format="%.0f m"),
                "Churn_Probability": st.column_config.ProgressColumn(
                    "Churn Risk",
                    format="%.2f",
                    min_value=0.0,
                    max_value=1.0
                ),
                "Predicted_Risk_Tier": st.column_config.TextColumn("Tier"),
                "Retention_Action_Plan": st.column_config.TextColumn("Recommended LiveOps Action")
            }
        )

        # 4. Nút tải file CSV
        csv_bytes = df_action[display_cols].to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"📥 TẢI XUỐNG DANH SÁCH {len(df_action):,} GAME THỦ (CSV SYNC CHO LIVEOPS)",
            data=csv_bytes,
            file_name=f"liveops_retention_target_{len(df_action)}_players.csv",
            mime="text/csv",
            use_container_width=True
        )
