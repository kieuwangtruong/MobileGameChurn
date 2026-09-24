"""AI Churn Prediction Simulator & LiveOps What-If View (Tab 2) - Adaptive Theme."""
from typing import Dict, Any
import streamlit as st
from dashboard.services.inference_service import get_simulation_presets, ChurnPredictor
from dashboard.components.charts import create_gauge_meter


def render_simulator_view(predictor: ChurnPredictor, is_dark: bool = True):
    """Hiển thị toàn bộ nội dung Tab 2 (Dark Gaming Studio Theme)."""
    title_color = "#F8FAFC"
    sub_color = "#94A3B8"

    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h3 style="margin-bottom: 6px; color: {title_color}; font-weight: 800; font-size: 1.45rem;">
            🎯 AI Churn Simulator & LiveOps What-If Sandbox
        </h3>
        <p style="color: {sub_color}; font-size: 0.92rem; margin: 0; font-weight: 500;">
            Thử nghiệm các hồ sơ hành vi người chơi để nhận kết quả đánh giá rủi ro tức thì từ mô hình Machine Learning XGBoost và kích hoạt kịch bản LiveOps tương ứng.
        </p>
    </div>
    """, unsafe_allow_html=True)

    presets = get_simulation_presets()

    # Khởi tạo session state cho simulator inputs
    if "sim_profile" not in st.session_state:
        st.session_state.sim_profile = presets["whale_risk"]["data"].copy()

    # Preset Persona Quick-Selection
    st.markdown("##### ⚡ Chọn nhanh hồ sơ mẫu (Quick Persona Presets):")
    p_cols = st.columns(len(presets))

    for idx, (key, preset_info) in enumerate(presets.items()):
        with p_cols[idx]:
            if st.button(preset_info["label"], use_container_width=True, key=f"btn_preset_{key}"):
                st.session_state.sim_profile = preset_info["data"].copy()
                st.rerun()

    profile = st.session_state.sim_profile

    # Form nhập thông số hành vi game thủ trong native container
    with st.form("figma_churn_sim_form"):
        with st.container(border=True):
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                st.markdown("##### 👤 Nhân khẩu & Thể loại")
                in_age = st.number_input("Độ tuổi (Age):", min_value=10, max_value=99, value=int(profile.get("Age", 24)))
                in_gender = st.selectbox("Giới tính (Gender):", ["Male", "Female"], index=0 if profile.get("Gender") == "Male" else 1)
                
                loc_list = ["USA", "Europe", "Asia", "Other"]
                loc_default = profile.get("Location", "USA")
                in_loc = st.selectbox("Khu vực (Location):", loc_list, index=loc_list.index(loc_default) if loc_default in loc_list else 0)
                
                genre_list = ["Action", "RPG", "Simulation", "Sports", "Strategy"]
                genre_default = profile.get("GameGenre", "RPG")
                in_genre = st.selectbox("Thể loại game (Genre):", genre_list, index=genre_list.index(genre_default) if genre_default in genre_list else 0)
                
                diff_list = ["Easy", "Medium", "Hard"]
                diff_default = profile.get("GameDifficulty", "Medium")
                in_diff = st.selectbox("Độ khó trải nghiệm (Difficulty):", diff_list, index=diff_list.index(diff_default) if diff_default in diff_list else 1)

            with col_f2:
                st.markdown("##### ⏱️ Tần suất & Cường độ chơi")
                in_playtime = st.slider("Tổng thời gian đã chơi (Giờ):", 0.0, 30.0, float(profile.get("PlayTimeHours", 10.0)), step=0.5)
                in_sessions = st.slider("Số phiên chơi/tuần (Sessions/Week):", 0, 20, int(profile.get("SessionsPerWeek", 4)))
                in_duration = st.slider("Thời lượng mỗi phiên (Phút):", 10.0, 180.0, float(profile.get("AvgSessionDurationMinutes", 35.0)), step=5.0)

            with col_f3:
                st.markdown("##### 🏆 Tiến trình & Tài chính")
                in_level = st.slider("Cấp độ người chơi (Player Level):", 1, 99, int(profile.get("PlayerLevel", 12)))
                in_achieve = st.slider("Thành tựu đã mở khóa (Achievements):", 0, 50, int(profile.get("AchievementsUnlocked", 8)))
                in_purchase = st.radio(
                    "Lịch sử nạp tiền (In-Game Spender):",
                    [1, 0],
                    format_func=lambda x: "💎 Có (Spender / VIP)" if x == 1 else "🛡️ Không (F2P Grinder)",
                    index=0 if profile.get("InGamePurchases", 0) == 1 else 1
                )

        submitted = st.form_submit_button("🚀 CHẠY MÔ PHỎNG & DỰ BÁO XÁC SUẤT CHURN", use_container_width=True)

    # Dữ liệu phục vụ Inference
    input_data = {
        "Age": in_age,
        "Gender": in_gender,
        "Location": in_loc,
        "GameGenre": in_genre,
        "GameDifficulty": in_diff,
        "PlayTimeHours": in_playtime,
        "InGamePurchases": in_purchase,
        "SessionsPerWeek": in_sessions,
        "AvgSessionDurationMinutes": in_duration,
        "PlayerLevel": in_level,
        "AchievementsUnlocked": in_achieve
    }

    # Cập nhật session_state profile
    st.session_state.sim_profile = input_data

    # Dự đoán
    pred_res = predictor.predict(input_data)
    prob_pct = pred_res["churn_probability_pct"]
    risk_tier = pred_res["risk_tier"]
    rec_action = pred_res["recommended_action"]

    # Hiển thị Kết quả Đánh giá
    with st.container(border=True):
        st.markdown("#### 🤖 Kết Quả Phân Tích Rủi Ro Từ Mô Hình XGBoost")

        r_col1, r_col2 = st.columns([5, 5])
        with r_col1:
            st.markdown(f"<div style='text-align: center; font-weight: 700; font-size: 0.92rem; color: {title_color}; margin-bottom: 6px;'>Xác Suất Churn Dự Báo</div>", unsafe_allow_html=True)
            fig_gauge = create_gauge_meter(prob_pct, risk_tier, is_dark=is_dark)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with r_col2:
            tier_class = "critical" if risk_tier == "Critical Risk" else ("medium" if risk_tier == "Medium Risk" else "low")
            tier_icon = "🔴" if risk_tier == "Critical Risk" else ("🟡" if risk_tier == "Medium Risk" else "🟢")

            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <span style="font-size: 0.82rem; color: {sub_color}; text-transform: uppercase; font-weight: 600;">Cấp Độ Nguy Cơ:</span><br>
                <span class="badge-tier {tier_class}" style="font-size: 0.95rem; margin-top: 4px;">
                    {tier_icon} {risk_tier.upper()} ({prob_pct:.1f}%)
                </span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="action-callout" style="margin-top: 10px;">
                <div class="action-callout-title">
                    📋 KỊCH BẢN GIỮ CHÂN KHUYẾN NGHỊ (LIVEOPS ACTION PLAN)
                </div>
                <div class="action-callout-body">
                    {rec_action}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Micro Metrics Breakdown thích ứng theme
            weekly_min = in_sessions * in_duration
            weekly_hrs = weekly_min / 60.0
            achieve_per_lvl = in_achieve / max(1, in_level)
            play_per_lvl = in_playtime / max(1, in_level)

            box_bg = "#1E293B" if is_dark else "#F8FAFC"
            box_border = "rgba(255,255,255,0.12)" if is_dark else "#E2E8F0"
            box_txt = "#CBD5E1" if is_dark else "#475569"

            st.markdown(f"""
            <div style="background: {box_bg}; border: 1px solid {box_border}; border-radius: 12px; padding: 14px; margin-top: 12px; font-size: 0.82rem; color: {box_txt};">
                <div>⏱️ <b>Thời lượng tuần:</b> {weekly_min:,.0f} phút ({weekly_hrs:.1f} giờ/tuần)</div>
                <div>🏆 <b>Hiệu suất thành tựu:</b> {achieve_per_lvl:.2f} achievements/cấp | ⏳ <b>Cường độ cày:</b> {play_per_lvl:.2f}h/cấp</div>
                <div>💡 <b>LiveOps Tip:</b> {'Tăng tần suất chơi bằng sự kiện đăng nhập ngày (Login streak)' if weekly_hrs < 5 else 'Hồ sơ có thời lượng tốt, tập trung duy trì nội dung end-game.'}</div>
            </div>
            """, unsafe_allow_html=True)

            # Phân tích chuyên sâu cho nhóm Hardcore F2P Grinder (Chiến lược nạp tiền & giảm giá)
            is_hardcore_f2p = (in_purchase == 0) and (in_level >= 20 or in_achieve >= 12 or in_playtime >= 10.0)
            if is_hardcore_f2p:
                f2p_bg = "rgba(16, 185, 129, 0.12)" if is_dark else "#ECFDF5"
                f2p_border = "rgba(16, 185, 129, 0.35)" if is_dark else "#A7F3D0"
                f2p_title = "#34D399" if is_dark else "#059669"
                f2p_txt = "#E2E8F0" if is_dark else "#065F46"

                st.markdown(f"""
                <div style="background: {f2p_bg}; border: 1px solid {f2p_border}; border-left: 4px solid {f2p_title}; border-radius: 12px; padding: 14px 18px; margin-top: 14px;">
                    <div style="color: {f2p_title}; font-weight: 800; font-size: 0.88rem; text-transform: uppercase; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                        <span>⚔️ CHIẾN LƯỢC LIVEOPS & MONETIZATION CHO F2P GRINDER CẤP CAO</span>
                    </div>
                    <div style="font-size: 0.83rem; line-height: 1.6; color: {f2p_txt};">
                        <div style="margin-bottom: 6px;">
                            <b>1. Có nên ép nạp tiền không?</b> ❌ <b>TUYỆT ĐỐI KHÔNG DÙNG PAYWALL</b>. Ép nạp sẽ làm họ cảm thấy bị phủ nhận công sức cày cuốc, dẫn tới bỏ game ngay và review 1 sao. Đây là nhóm <i>"xương sống cộng đồng"</i> tạo sinh khí cho server và giữ chân các Spenders/Whales.
                        </div>
                        <div style="margin-bottom: 6px;">
                            <b>2. Có nên khuyến khích nạp không?</b> ✔️ <b>CÓ, DÙNG CHIẾN THUẬT "PHÁ BĂNG VÍ" (Ice-Breaker):</b>
                            Bán <b>Gói Khởi Động ($0.99 - $1.99)</b> với giá trị tài nguyên gấp 10x (1000% Value Pack) hoặc <b>Vé Mùa Battle Pass</b>. Mục đích là chuyển đổi tâm lý từ <i>"Chưa từng nạp"</i> sang <i>"Đã từng nạp"</i> (tăng 400% khả năng nạp lại trong tương lai).
                        </div>
                        <div>
                            <b>3. Có nên giảm giá gì không?</b> ⚡ <b>CHỈ GIẢM GIÁ CÁ NHÂN HÓA (Triggered Flash Sale):</b>
                            Chỉ kích hoạt ưu đãi giảm giá sâu (ví dụ 80% trong 2 giờ) khi họ vừa đạt cột mốc vinh quang (Level 50, đạt Thành Tựu hiếm). <b>Không giảm giá đại trà</b> vì sẽ làm mất giá trị tiền tệ trong game.
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
