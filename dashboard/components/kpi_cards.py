"""Tesla-Style Clean KPI Cards Component."""
from typing import Dict, Any
import streamlit as st


def render_tesla_kpi_card(
    label: str,
    value: str,
    subtext: str = "",
    pill_text: str = "",
    pill_type: str = "neutral"  # 'up', 'down', 'neutral'
) -> str:
    """Render 1 thẻ KPI nền trắng tối giản chuẩn Tesla Dashboard."""
    pill_html = ""
    if pill_text:
        arrow = "▲ " if pill_type == "up" else ("▼ " if pill_type == "down" else "")
        pill_html = f'<span class="tesla-pill {pill_type}">{arrow}{pill_text}</span>'

    return f"""
    <div class="tesla-card">
        <div class="tesla-card-label">
            <span>{label}</span>
            {pill_html}
        </div>
        <div class="tesla-card-val">
            {value}
        </div>
        <div class="tesla-card-sub">
            <span>{subtext}</span>
        </div>
    </div>
    """


def render_executive_kpis(kpi: Dict[str, Any]):
    """Hiển thị hàng thẻ KPI tối giản chuẩn Tesla Dashboard trong ảnh tham chiếu."""
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    total_players = kpi.get("total_players", 0)
    actual_churn_pct = kpi.get("actual_churn_pct", 0.0)
    churn_delta = kpi.get("churn_delta", 0.0)
    spender_conversion = kpi.get("spender_conversion_pct", 0.0)
    avg_playtime = kpi.get("avg_playtime_hours", 0.0)
    critical_risk = kpi.get("critical_risk_count", 0)
    rev_at_risk = kpi.get("revenue_at_risk_usd", 0.0)

    # 1. Active Users / Total Players
    with c1:
        st.markdown(
            render_tesla_kpi_card(
                label="Active Players",
                value=f"{total_players:,}",
                subtext="Quy mô mẫu phân tích",
                pill_text="All-time",
                pill_type="neutral"
            ),
            unsafe_allow_html=True
        )

    # 2. Actual Churn Rate
    with c2:
        churn_pill_type = "down" if churn_delta > 0 else "up"
        delta_str = f"{abs(churn_delta):.1f}%"
        st.markdown(
            render_tesla_kpi_card(
                label="Actual Churn Rate",
                value=f"{actual_churn_pct:.1f}%",
                subtext="vs 20% benchmark",
                pill_text=f"{delta_str}",
                pill_type=churn_pill_type
            ),
            unsafe_allow_html=True
        )

    # 3. Spender Conversion
    with c3:
        st.markdown(
            render_tesla_kpi_card(
                label="Spender Ratio",
                value=f"{spender_conversion:.1f}%",
                subtext="Tỷ lệ người chơi nạp",
                pill_text="+2.4%",
                pill_type="up"
            ),
            unsafe_allow_html=True
        )

    # 4. Avg Session / Playtime
    with c4:
        st.markdown(
            render_tesla_kpi_card(
                label="Av. Play Time",
                value=f"{avg_playtime:.1f}h",
                subtext="Thời lượng tích lũy",
                pill_text="Steady",
                pill_type="neutral"
            ),
            unsafe_allow_html=True
        )

    # 5. Critical Risk (AI Alert)
    with c5:
        st.markdown(
            render_tesla_kpi_card(
                label="Critical Risk (AI)",
                value=f"{critical_risk:,}",
                subtext="Xác suất churn ≥80%",
                pill_text="Alert",
                pill_type="down"
            ),
            unsafe_allow_html=True
        )

    # 6. Revenue at Risk (Financial Impact)
    with c6:
        st.markdown(
            render_tesla_kpi_card(
                label="Revenue At Risk",
                value=f"${rev_at_risk:,.0f}",
                subtext="Thất thu ước tính/tháng",
                pill_text="LiveOps",
                pill_type="down"
            ),
            unsafe_allow_html=True
        )
