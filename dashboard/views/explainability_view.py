"""Model Explainability & SHAP Benchmarks View (Tab 4) - Adaptive Theme."""
from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def render_explainability_view(is_dark: bool = True):
    """Hiển thị toàn bộ nội dung Tab 4 (Dark Gaming Studio Theme)."""
    title_color = "#F8FAFC"
    sub_color = "#94A3B8"

    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h3 style="margin-bottom: 6px; color: {title_color}; font-weight: 800; font-size: 1.45rem;">
            🧠 Machine Learning Model Benchmarking & SHAP Explainability
        </h3>
        <p style="color: {sub_color}; font-size: 0.92rem; margin: 0; font-weight: 500;">
            Giải thích cơ chế ra quyết định của mô hình AI dựa trên lý thuyết trò chơi SHAP (SHapley Additive exPlanations) và so sánh hiệu năng các thuật toán.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_bench1, col_bench2 = st.columns([6, 4])

    with col_bench1:
        with st.container(border=True):
            st.markdown("#### 🏆 Bảng Xếp Hạng Mô Hình (Benchmarking)")

            benchmark_df = pd.DataFrame({
                "Mô hình": ["Logistic Regression (Baseline)", "Random Forest", "XGBoost (Được chọn)"],
                "Accuracy": ["84.05%", "93.86%", "95.45%"],
                "Precision": ["63.49%", "86.77%", "92.98%"],
                "Recall (Churn=1)": ["89.78%", "89.88%", "89.10%"],
                "F1-Score": ["74.38%", "88.30%", "91.00%"],
                "ROC-AUC": ["0.9258", "0.9392", "0.9386"]
            })
            st.dataframe(benchmark_df, use_container_width=True, hide_index=True)

            st.markdown("""
            <div class="action-callout" style="margin-top: 14px;">
                <div class="action-callout-title">🎯 LÝ DO CHỌN XGBOOST TRONG SẢN XUẤT:</div>
                <div class="action-callout-body">
                    Trong bài toán Churn Game, <b>Recall 89.10%</b> kết hợp cùng <b>Precision 92.98%</b> giúp studio 
                    <b>tránh lãng phí ngân sách LiveOps</b> (không gửi nhầm giftcode giá trị cao cho người chơi đang gắn bó) 
                    đồng thời <b>bắt trúng gần 90% game thủ sắp rời bỏ</b> trước khi họ gỡ cài đặt.
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_bench2:
        with st.container(border=True):
            st.markdown("#### 🔍 TOP 5 Đặc Trưng Quyết Định (SHAP)")

            txt_primary = "#F8FAFC" if is_dark else "#1E293B"
            txt_muted = "#94A3B8" if is_dark else "#64748B"
            divider = "rgba(255,255,255,0.08)" if is_dark else "#F1F5F9"

            st.markdown(f"""
            <div style="font-size: 0.88rem; line-height: 1.6; color: {txt_primary};">
                <div style="margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid {divider};">
                    <b style="color: #60A5FA;">1. TotalWeeklyMinutes</b> (Trọng số cao nhất)<br>
                    <span style="color: {txt_muted};">Game thủ chơi dưới 180 phút/tuần có xác suất rời bỏ tăng đột biến.</span>
                </div>
                <div style="margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid {divider};">
                    <b style="color: #34D399;">2. PlayerLevel</b> (Điểm nghẽn tân thủ)<br>
                    <span style="color: {txt_muted};">Cấp độ &lt; 10 có nguy cơ rời bỏ cao gấp 3.4 lần so với nhóm cấp 30+.</span>
                </div>
                <div style="margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid {divider};">
                    <b style="color: #FBBF24;">3. AchievementsUnlocked</b> (Động lực tiến trình)<br>
                    <span style="color: {txt_muted};">Người chơi mở khóa nhiều thành tựu hình thành thói quen gắn bó sâu.</span>
                </div>
                <div style="margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid {divider};">
                    <b style="color: #C084FC;">4. AchievementsPerLevel</b><br>
                    <span style="color: {txt_muted};">Tỷ lệ nhận thưởng theo cấp độ phản ánh cảm giác thỏa mãn trong game.</span>
                </div>
                <div>
                    <b style="color: #F87171;">5. PlayTimePerLevel</b><br>
                    <span style="color: {txt_muted};">Cường độ cày cuốc mất cân bằng gây ức chế (burnout) dẫn tới bỏ game.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Hiển thị biểu đồ Beeswarm SHAP thực tế từ pipeline nếu tồn tại
    shap_img_path = BASE_DIR / 'reports' / 'figures' / 'shap_summary_beeswarm.png'
    if shap_img_path.exists():
        with st.container(border=True):
            st.markdown("#### 📊 Biểu Đồ SHAP Beeswarm Plot (Global Feature Impact)")
            st.image(str(shap_img_path), use_column_width=True, caption="Biểu đồ phân phối giá trị SHAP trên tập kiểm thử (Test Set)")
