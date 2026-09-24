"""Streamlit Application: Mobile Game Churn Analytics & LiveOps AI Studio."""
import sys
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Đảm bảo đường dẫn root có thể import src
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.model import get_predictor

# 1. Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Game Churn AI & LiveOps Studio",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho phong cách gaming dark/modern UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(26, 32, 44, 0.8) 0%, rgba(45, 55, 72, 0.7) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(8px);
        margin-bottom: 12px;
    }
    
    .metric-val {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 4px 0;
    }
    
    .metric-lbl {
        font-size: 0.85rem;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .badge-critical {
        background: linear-gradient(90deg, #E53E3E, #FF6B6B);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .badge-medium {
        background: linear-gradient(90deg, #D69E2E, #ECC94B);
        color: #1A202C;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .badge-low {
        background: linear-gradient(90deg, #38A169, #48BB78);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        display: inline-block;
    }
    
    .action-box {
        background: rgba(49, 130, 206, 0.12);
        border-left: 4px solid #3182CE;
        padding: 14px 18px;
        border-radius: 0 10px 10px 0;
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)


# 2. Tải dữ liệu từ SQLite (Cached)
@st.cache_data(ttl=600)
def load_game_data():
    db_path = BASE_DIR / 'data' / 'game_analytics.db'
    if not db_path.exists():
        st.error(f"Không tìm thấy cơ sở dữ liệu tại {db_path}. Vui lòng chạy `python src/data_pipeline.py` trước.")
        st.stop()
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM view_powerbi_churn_analytics", conn)
    conn.close()
    return df


try:
    df_players = load_game_data()
    predictor = get_predictor()
except Exception as e:
    st.error(f"Lỗi khởi tạo hệ thống: {e}")
    st.stop()

# 3. Sidebar điều khiển
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/game-controller.png", width=70)
    st.title("🎮 LiveOps AI Studio")
    st.caption("Hệ thống Giám sát & Dự báo Churn Game Mobile")
    st.markdown("---")
    
    st.markdown("### 🔍 Bộ lọc Dữ liệu")
    all_genres = sorted(df_players['GameGenre'].unique().tolist())
    selected_genres = st.multiselect("Thể loại game:", all_genres, default=all_genres)
    
    all_locations = sorted(df_players['Location'].unique().tolist())
    selected_locations = st.multiselect("Khu vực:", all_locations, default=all_locations)
    
    spender_filter = st.radio("Nhóm nạp tiền:", ["Tất cả", "Chỉ Spender (Nạp)", "Chỉ F2P (Miễn phí)"])
    
    st.markdown("---")
    st.caption("🤖 Model: XGBoost Classifier (95.45% Acc)")
    st.caption("⚡ Serving: FastAPI + Streamlit")

# Lọc dữ liệu theo sidebar
df_filtered = df_players[
    (df_players['GameGenre'].isin(selected_genres)) &
    (df_players['Location'].isin(selected_locations))
]
if spender_filter == "Chỉ Spender (Nạp)":
    df_filtered = df_filtered[df_filtered['InGamePurchases'] == 1]
elif spender_filter == "Chỉ F2P (Miễn phí)":
    df_filtered = df_filtered[df_filtered['InGamePurchases'] == 0]

# 4. Header ứng dụng
st.title("🎮 Game Churn Analytics & Player Retention Dashboard")
st.markdown("Nền tảng phân tích hành vi game thủ, dự báo rời bỏ bằng Machine Learning & kích hoạt chiến dịch LiveOps giữ chân.")

# 5. Cấu trúc Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Executive KPIs (Cấp quản lý)",
    "🎯 AI Churn Simulator (Mô phỏng AI)",
    "⚡ LiveOps Action Center (Can thiệp)",
    "🧠 Model Explainability (SHAP & Benchmarks)"
])

# ==========================================
# TAB 1: EXECUTIVE KPIS & GAME HEALTH
# ==========================================
with tab1:
    total_p = len(df_filtered)
    actual_churn_pct = (df_filtered['IsChurn'].mean() * 100) if total_p > 0 else 0
    spender_pct = (df_filtered['InGamePurchases'].mean() * 100) if total_p > 0 else 0
    avg_playtime = df_filtered['PlayTimeHours'].mean() if total_p > 0 else 0
    risk_players = (df_filtered['Predicted_Risk_Tier'] == 'Critical Risk').sum() if total_p > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Total Players</div>
            <div class="metric-val" style="color: #63B3ED;">{total_p:,}</div>
            <small style="color: #CBD5E0;">Quy mô mẫu theo lọc</small>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Actual Churn Rate</div>
            <div class="metric-val" style="color: #FEB2B2;">{actual_churn_pct:.2f}%</div>
            <small style="color: #CBD5E0;">Nhóm Low Engagement</small>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Spender Conversion</div>
            <div class="metric-val" style="color: #68D391;">{spender_pct:.2f}%</div>
            <small style="color: #CBD5E0;">Tỷ lệ người chơi nạp</small>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Avg Play Time</div>
            <div class="metric-val" style="color: #F6AD55;">{avg_playtime:.1f}h</div>
            <small style="color: #CBD5E0;">Thời lượng chơi TB</small>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-lbl">Critical Risk (AI)</div>
            <div class="metric-val" style="color: #FC8181;">{risk_players:,}</div>
            <small style="color: #CBD5E0;">Cần can thiệp khẩn cấp</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Biểu đồ 1 & 2
    row1_c1, row1_c2 = st.columns([6, 4])
    with row1_c1:
        st.subheader("📌 Tỷ lệ rời bỏ (Actual Churn) theo Thể loại Game")
        genre_churn = df_filtered.groupby('GameGenre')['IsChurn'].mean().reset_index()
        genre_churn['Churn_Rate_Pct'] = genre_churn['IsChurn'] * 100
        genre_churn = genre_churn.sort_values(by='Churn_Rate_Pct', ascending=True)

        fig_genre = px.bar(
            genre_churn,
            x='Churn_Rate_Pct',
            y='GameGenre',
            orientation='h',
            text='Churn_Rate_Pct',
            color='Churn_Rate_Pct',
            color_continuous_scale=['#4299E1', '#E53E3E'],
            labels={'Churn_Rate_Pct': 'Tỷ lệ Churn (%)', 'GameGenre': 'Thể loại Game'}
        )
        fig_genre.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_genre.update_layout(height=340, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
        st.plotly_chart(fig_genre, use_container_width=True)

    with row1_c2:
        st.subheader("🎯 Phân tầng Rủi ro Người chơi (AI Risk Tier)")
        tier_counts = df_filtered['Predicted_Risk_Tier'].value_counts().reset_index()
        tier_counts.columns = ['Risk_Tier', 'Count']
        
        color_map = {
            'Low Risk': '#38A169',
            'Medium Risk': '#D69E2E',
            'Critical Risk': '#E53E3E'
        }
        fig_pie = px.pie(
            tier_counts,
            names='Risk_Tier',
            values='Count',
            color='Risk_Tier',
            color_discrete_map=color_map,
            hole=0.45
        )
        fig_pie.update_layout(height=340, margin=dict(l=10, r=10, t=20, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Biểu đồ 3 & 4
    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        st.subheader("⏱️ Tương quan: Số phút chơi mỗi tuần vs Rủi ro Churn")
        sample_scatter = df_filtered.sample(min(1500, len(df_filtered)), random_state=42) if len(df_filtered) > 0 else df_filtered
        fig_scatter = px.scatter(
            sample_scatter,
            x='TotalWeeklyMinutes',
            y='Churn_Probability',
            color='Predicted_Risk_Tier',
            color_discrete_map=color_map,
            opacity=0.7,
            labels={'TotalWeeklyMinutes': 'Tổng số phút chơi/tuần', 'Churn_Probability': 'Xác suất Churn'}
        )
        fig_scatter.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

    with row2_c2:
        st.subheader("💰 Tỷ lệ Churn: Nhóm Nạp tiền (Spender) vs Miễn phí (F2P)")
        spender_comp = df_filtered.groupby('InGamePurchases')['IsChurn'].mean().reset_index()
        spender_comp['Group'] = spender_comp['InGamePurchases'].map({1: 'Spender (Có nạp)', 0: 'F2P (Chưa nạp)'})
        spender_comp['Churn_Pct'] = spender_comp['IsChurn'] * 100

        fig_spender = px.bar(
            spender_comp,
            x='Group',
            y='Churn_Pct',
            color='Group',
            color_discrete_sequence=['#ED8936', '#4FD1C5'],
            text='Churn_Pct',
            labels={'Group': 'Phân khúc', 'Churn_Pct': 'Tỷ lệ Churn (%)'}
        )
        fig_spender.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_spender.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
        st.plotly_chart(fig_spender, use_container_width=True)


# ==========================================
# TAB 2: AI CHURN PREDICTION SIMULATOR
# ==========================================
with tab2:
    st.subheader("🎮 Công cụ Mô phỏng AI: Dự báo Rủi ro Rời bỏ & Kích hoạt LiveOps")
    st.markdown("Thử nghiệm các hồ sơ hành vi người chơi để nhận kết quả đánh giá rủi ro tức thì từ mô hình Machine Learning.")

    # Preset profiles
    st.markdown("**⚡ Chọn nhanh hồ sơ mẫu (Quick Presets):**")
    p_col1, p_col2, p_col3, p_col4 = st.columns(4)
    
    preset_chosen = None
    if p_col1.button("🚨 Tân thủ nguy cơ (Newbie At-Risk)"):
        preset_chosen = {
            "Age": 19, "Gender": "Male", "Location": "USA", "GameGenre": "Action",
            "GameDifficulty": "Hard", "PlayTimeHours": 1.5, "InGamePurchases": 0,
            "SessionsPerWeek": 1, "AvgSessionDurationMinutes": 15.0,
            "PlayerLevel": 2, "AchievementsUnlocked": 1
        }
    if p_col2.button("💎 Đại gia nạp thẻ sắp rời bỏ (Whale Risk)"):
        preset_chosen = {
            "Age": 28, "Gender": "Female", "Location": "Europe", "GameGenre": "RPG",
            "GameDifficulty": "Medium", "PlayTimeHours": 8.0, "InGamePurchases": 1,
            "SessionsPerWeek": 2, "AvgSessionDurationMinutes": 20.0,
            "PlayerLevel": 15, "AchievementsUnlocked": 6
        }
    if p_col3.button("⚔️ Game thủ cày cuốc (Hardcore F2P)"):
        preset_chosen = {
            "Age": 22, "Gender": "Male", "Location": "Asia", "GameGenre": "Strategy",
            "GameDifficulty": "Medium", "PlayTimeHours": 22.0, "InGamePurchases": 0,
            "SessionsPerWeek": 12, "AvgSessionDurationMinutes": 60.0,
            "PlayerLevel": 45, "AchievementsUnlocked": 35
        }
    if p_col4.button("👑 VIP Gắn bó (Loyal VIP Core)"):
        preset_chosen = {
            "Age": 30, "Gender": "Male", "Location": "USA", "GameGenre": "Simulation",
            "GameDifficulty": "Easy", "PlayTimeHours": 24.0, "InGamePurchases": 1,
            "SessionsPerWeek": 15, "AvgSessionDurationMinutes": 80.0,
            "PlayerLevel": 60, "AchievementsUnlocked": 45
        }

    # Session State để lưu giá trị inputs
    if "sim_values" not in st.session_state:
        st.session_state.sim_values = {
            "Age": 24, "Gender": "Male", "Location": "USA", "GameGenre": "RPG",
            "GameDifficulty": "Medium", "PlayTimeHours": 10.0, "InGamePurchases": 1,
            "SessionsPerWeek": 4, "AvgSessionDurationMinutes": 35.0,
            "PlayerLevel": 12, "AchievementsUnlocked": 8
        }
        
    if preset_chosen:
        st.session_state.sim_values = preset_chosen

    vals = st.session_state.sim_values

    with st.form("churn_sim_form"):
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            st.markdown("##### 👤 Thông tin người chơi")
            in_age = st.number_input("Độ tuổi (Age):", min_value=10, max_value=100, value=int(vals["Age"]))
            in_gender = st.selectbox("Giới tính (Gender):", ["Male", "Female"], index=0 if vals["Gender"] == "Male" else 1)
            in_loc = st.selectbox("Khu vực (Location):", ["USA", "Europe", "Asia", "Other"], index=["USA", "Europe", "Asia", "Other"].index(vals["Location"]))
            in_genre = st.selectbox("Thể loại game (Genre):", ["Action", "RPG", "Simulation", "Sports", "Strategy"], index=["Action", "RPG", "Simulation", "Sports", "Strategy"].index(vals["GameGenre"]))
            in_diff = st.selectbox("Độ khó (Difficulty):", ["Easy", "Medium", "Hard"], index=["Easy", "Medium", "Hard"].index(vals["GameDifficulty"]))

        with col_f2:
            st.markdown("##### ⏱️ Tần suất & Cường độ chơi")
            in_playtime = st.slider("Tổng thời gian chơi (Giờ):", 0.0, 24.0, float(vals["PlayTimeHours"]), step=0.5)
            in_sessions = st.slider("Số phiên chơi/tuần (Sessions/Week):", 0, 19, int(vals["SessionsPerWeek"]))
            in_duration = st.slider("Thời lượng mỗi phiên (Phút):", 10.0, 180.0, float(vals["AvgSessionDurationMinutes"]), step=5.0)
            
        with col_f3:
            st.markdown("##### 🏆 Tiến trình & Tài chính")
            in_level = st.slider("Cấp độ người chơi (Level):", 1, 99, int(vals["PlayerLevel"]))
            in_achieve = st.slider("Thành tựu đã mở khóa (Achievements):", 0, 49, int(vals["AchievementsUnlocked"]))
            in_purchase = st.radio("Từng nạp tiền trong game (Spender):", [1, 0], format_func=lambda x: "Có (Spender)" if x == 1 else "Không (F2P)", index=0 if vals["InGamePurchases"] == 1 else 1)

        submitted = st.form_submit_button("🚀 Chạy Phân Tích & Dự Báo Nguy Cơ Rời Bỏ", use_container_width=True)

    # Chạy dự đoán
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
    
    pred_res = predictor.predict(input_data)
    prob = pred_res["churn_probability"]
    prob_pct = pred_res["churn_probability_pct"]
    risk_tier = pred_res["risk_tier"]
    rec_action = pred_res["recommended_action"]

    st.markdown("---")
    st.markdown("### 📊 Kết Quả Đánh Giá Từ AI Model")
    
    r_col1, r_col2 = st.columns([5, 5])
    with r_col1:
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prob_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Xác suất Churn (Dự báo)", 'font': {'size': 20}},
            number={'suffix': "%", 'font': {'size': 32}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#E53E3E" if prob >= 0.8 else ("#D69E2E" if prob >= 0.5 else "#38A169")},
                'steps': [
                    {'range': [0, 50], 'color': "rgba(56, 161, 105, 0.25)"},
                    {'range': [50, 80], 'color': "rgba(214, 158, 46, 0.25)"},
                    {'range': [80, 100], 'color': "rgba(229, 62, 62, 0.25)"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with r_col2:
        st.markdown("#### 🎯 Phân tầng & Đề xuất LiveOps:")
        
        badge_html = f'<div class="badge-critical">🔴 CẤP ĐỘ: {risk_tier.upper()}</div>' if risk_tier == "Critical Risk" else (
            f'<div class="badge-medium">🟡 CẤP ĐỘ: {risk_tier.upper()}</div>' if risk_tier == "Medium Risk" else
            f'<div class="badge-low">🟢 CẤP ĐỘ: {risk_tier.upper()}</div>'
        )
        st.markdown(badge_html, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="action-box">
            <b>📋 Khuyến nghị can thiệp (Action Plan):</b><br>
            {rec_action}
        </div>
        """, unsafe_allow_html=True)
        
        # Breakdown metric cards
        weekly_min = in_sessions * in_duration
        st.caption(f"⚡ **Chỉ số nội tại:** Tổng thời gian chơi: **{weekly_min:,.0f} phút/tuần** (~{weekly_min/60:.1f}h) | Tỷ lệ thành tựu/cấp: **{(in_achieve/in_level):.2f}**.")


# ==========================================
# TAB 3: LIVEOPS ACTION CENTER
# ==========================================
with tab3:
    st.subheader("⚡ LiveOps Retention Target List (Danh sách can thiệp khẩn cấp)")
    st.markdown("Xuất danh sách người chơi có nguy cơ rời bỏ để đội ngũ vận hành chạy chiến dịch Push Notification / Giftcode.")

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        target_risk = st.multiselect(
            "Cấp độ rủi ro:",
            ["Critical Risk", "Medium Risk", "Low Risk"],
            default=["Critical Risk"]
        )
    with col_t2:
        target_spender = st.selectbox(
            "Phân khúc thanh toán:",
            ["Tất cả", "Chỉ Spenders (VIP & Buyer)", "Chỉ F2P (Người chơi miễn phí)"]
        )
    with col_t3:
        max_rows = st.number_input("Số lượng bản ghi tối đa:", min_value=10, max_value=5000, value=100, step=50)

    df_action = df_players[df_players['Predicted_Risk_Tier'].isin(target_risk)].copy()
    if target_spender == "Chỉ Spenders (VIP & Buyer)":
        df_action = df_action[df_action['InGamePurchases'] == 1]
    elif target_spender == "Chỉ F2P (Người chơi miễn phí)":
        df_action = df_action[df_action['InGamePurchases'] == 0]

    st.markdown(f"**Tìm thấy `{len(df_action):,}` người chơi phù hợp tiêu chí.**")

    display_cols = [
        'PlayerID', 'GameGenre', 'PlayerLevel', 'PlayTimeHours',
        'InGamePurchases', 'TotalWeeklyMinutes', 'Churn_Probability',
        'Predicted_Risk_Tier', 'Retention_Action_Plan'
    ]
    df_show = df_action[display_cols].head(int(max_rows))
    st.dataframe(df_show, use_container_width=True, height=400)

    # Nút tải CSV
    csv_data = df_action[display_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Tải xuống Danh sách CSV cho Đội LiveOps",
        data=csv_data,
        file_name="liveops_retention_target_players.csv",
        mime="text/csv"
    )


# ==========================================
# TAB 4: MODEL EXPLAINABILITY (SHAP)
# ==========================================
with tab4:
    st.subheader("🧠 Machine Learning Model Benchmarking & SHAP Explainability")
    st.markdown("Giải thích cách mô hình Machine Learning đưa ra quyết định dự báo churn dựa trên lý thuyết trò chơi SHAP.")

    c_bench1, c_bench2 = st.columns([6, 4])
    with c_bench1:
        st.markdown("#### 🏆 Bảng Xếp Hạng Mô Hình (Model Benchmarking)")
        benchmark_data = {
            "Mô hình": ["Logistic Regression (Baseline)", "Random Forest", "XGBoost (Được chọn)"],
            "Accuracy": ["84.05%", "93.86%", "95.45%"],
            "Precision": ["63.49%", "86.77%", "92.98%"],
            "Recall (Class 1)": ["89.78%", "89.88%", "89.10%"],
            "F1-Score": ["74.38%", "88.30%", "91.00%"],
            "ROC-AUC": [0.9258, 0.9392, 0.9386]
        }
        st.table(pd.DataFrame(benchmark_data))
        st.caption("🎯 **Đặc biệt với Recall 89.10%**: Mô hình nhận diện chính xác 89/100 game thủ chuẩn bị bỏ game, tạo cơ hội vàng để can thiệp kịp thời.")

    with c_bench2:
        st.markdown("#### 🔍 TOP 5 Yếu Tố Quyết Định (SHAP Top Features)")
        st.markdown("""
        1. **`TotalWeeklyMinutes`**: Tổng số phút chơi trong tuần là yếu tố quan trọng nhất. Game thủ chơi dưới mức chuẩn có nguy cơ churn tăng vọt.
        2. **`PlayerLevel`**: Level càng thấp thì xác suất rời bỏ càng cao (điểm nghẽn tân thủ).
        3. **`AchievementsUnlocked`**: Người chơi mở khóa nhiều thành tựu có tính gắn kết vượt trội.
        4. **`AchievementsPerLevel`**: Tốc độ đạt được thành tựu trên mỗi cấp độ củng cố động lực gắn bó dài hạn.
        5. **`PlayTimePerLevel`**: Cường độ cày cấp hợp lý giúp giảm thiểu nguy cơ chán nản.
        """)

    # Hiển thị ảnh SHAP nếu có
    shap_summary_path = BASE_DIR / 'reports' / 'figures' / 'shap_summary_beeswarm.png'
    if shap_summary_path.exists():
        st.image(str(shap_summary_path), caption="Biểu đồ SHAP Beeswarm Plot từ Notebook 03 (XGBoost Feature Importance)")
