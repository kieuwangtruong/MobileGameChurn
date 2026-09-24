"""Executive KPIs and Game Health View (Tab 1) - Adaptive Theme."""
import pandas as pd
import streamlit as st
from dashboard.services.data_service import (
    compute_executive_kpis,
    get_genre_churn_stats,
    get_risk_distribution,
    get_spender_churn_comparison
)
from dashboard.components.kpi_cards import render_executive_kpis
from dashboard.components.charts import (
    create_genre_churn_chart,
    create_risk_donut_chart,
    create_playtime_risk_scatter,
    create_spender_comparison_chart
)


def render_executive_view(df_filtered: pd.DataFrame, is_dark: bool = False):
    """Hiển thị toàn bộ nội dung Tab 1 (Đã sửa triệt để lỗi đè chữ biểu đồ)."""
    if df_filtered.empty:
        st.warning("⚠️ Không tìm thấy người chơi nào khớp với bộ lọc hiện tại. Vui lòng mở rộng điều kiện lọc ở Sidebar.")
        return

    # 1. Hàng Thẻ KPI (6 Thẻ)
    kpi_metrics = compute_executive_kpis(df_filtered)
    render_executive_kpis(kpi_metrics)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # 2. Executive Insights Summary Pill
    crit_count = kpi_metrics["critical_risk_count"]
    rev_risk = kpi_metrics["revenue_at_risk_usd"]

    st.markdown(f"""
    <div class="action-callout">
        <div class="action-callout-title">
            ⚡ LIVE EXECUTIVE BRIEFING & CHURN RADAR
        </div>
        <div class="action-callout-body">
            Phát hiện <b>{crit_count:,} game thủ</b> ({crit_count/max(1, len(df_filtered))*100:.1f}%) đang ở mức 
            <span class="badge-tier critical">Critical Risk (Xác suất rời bỏ ≥ 80%)</span>. 
            Doanh thu đang bị đe dọa (Revenue at Risk) ước tính đạt <b>${rev_risk:,.0f}/tháng</b> từ nhóm Spenders. 
            Khuyến nghị đội LiveOps đồng bộ danh sách can thiệp trong Tab 3 để kích hoạt chuỗi sự kiện Comeback Quest.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Lưới Biểu Đồ Hàng 1 (Tiêu đề ngoài độc lập, loại bỏ 100% đè chữ vào legend)
    c_chart1, c_chart2 = st.columns([6, 4])
    genre_data = get_genre_churn_stats(df_filtered)

    with c_chart1:
        with st.container(border=True):
            st.markdown("##### 📌 Tỷ Lệ Churn Thực Tế Theo Thể Loại")
            fig_genre = create_genre_churn_chart(genre_data, is_dark=is_dark)
            st.plotly_chart(fig_genre, use_container_width=True)

    with c_chart2:
        with st.container(border=True):
            st.markdown("##### 🎯 Phân Tầng Rủi Ro Người Chơi (AI Risk)")
            risk_data = get_risk_distribution(df_filtered)
            fig_donut = create_risk_donut_chart(risk_data, total_count=kpi_metrics["total_players"], is_dark=is_dark)
            st.plotly_chart(fig_donut, use_container_width=True)

    # 4. Hàng 2: Progress Bars (Weakest Retention Genres vs Strongest Retention Genres)
    c_weak, c_strong = st.columns(2)
    sorted_genres = genre_data.sort_values(by="Churn_Rate_Pct", ascending=False)
    
    with c_weak:
        st.markdown("""
        <div class="topic-container">
            <div class="topic-title">⚠️ Thể Loại Nguy Cơ Rời Bỏ Cao Nhất (Weakest Retention Genres)</div>
        """, unsafe_allow_html=True)

        for _, row in sorted_genres.head(3).iterrows():
            genre_name = row['GameGenre']
            churn_pct = row['Churn_Rate_Pct']
            icon = "⚔️" if genre_name == "Action" else ("🏹" if genre_name == "RPG" else "🧩")
            st.markdown(f"""
            <div class="topic-row">
                <div class="topic-icon">{icon}</div>
                <div class="topic-info">
                    <div class="topic-name">{genre_name}</div>
                    <div class="topic-bar-bg">
                        <div class="topic-bar-fill danger" style="width: {min(100, churn_pct * 2)}%;"></div>
                    </div>
                </div>
                <div class="topic-pct" style="color: #EF4444;">{churn_pct:.1f}% Churn</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with c_strong:
        st.markdown("""
        <div class="topic-container">
            <div class="topic-title">🛡️ Thể Loại Gắn Bó Tốt Nhất (Strongest Retention Genres)</div>
        """, unsafe_allow_html=True)

        for _, row in sorted_genres.tail(3).iloc[::-1].iterrows():
            genre_name = row['GameGenre']
            retention_pct = 100.0 - row['Churn_Rate_Pct']
            icon = "👑" if genre_name == "Strategy" else ("⚽" if genre_name == "Sports" else "🏙️")
            st.markdown(f"""
            <div class="topic-row">
                <div class="topic-icon">{icon}</div>
                <div class="topic-info">
                    <div class="topic-name">{genre_name}</div>
                    <div class="topic-bar-bg">
                        <div class="topic-bar-fill success" style="width: {min(100, retention_pct)}%;"></div>
                    </div>
                </div>
                <div class="topic-pct" style="color: #10B981;">{retention_pct:.1f}% Retained</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # 5. Hàng 3: Biểu đồ Spender vs F2P & Scatter Tương Quan (Tiêu đề ngoài độc lập)
    c_sub1, c_sub2 = st.columns(2)
    with c_sub1:
        with st.container(border=True):
            st.markdown("##### 💰 Tỷ Lệ Churn: Spender (Nạp) vs F2P (Miễn Phí)")
            spender_comp = get_spender_churn_comparison(df_filtered)
            fig_spender = create_spender_comparison_chart(spender_comp, is_dark=is_dark)
            st.plotly_chart(fig_spender, use_container_width=True)

    with c_sub2:
        with st.container(border=True):
            st.markdown("##### ⏱️ Tương Quan: Phút Chơi / Tuần vs Xác Suất Churn")
            fig_scatter = create_playtime_risk_scatter(df_filtered, is_dark=is_dark)
            st.plotly_chart(fig_scatter, use_container_width=True)
