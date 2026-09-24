"""Adaptive Minimalist Chart Factory for Game Analytics (Supporting Dark & Light Modes)."""
from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def get_theme_palette(is_dark: bool = False):
    """Lấy bảng màu tương thích Dark/Light mode."""
    if is_dark:
        return {
            "bg": "rgba(0,0,0,0)",
            "text_primary": "#F8FAFC",
            "text_secondary": "#CBD5E1",
            "grid_color": "rgba(255, 255, 255, 0.08)",
            "hover_bg": "#1F2937",
            "hover_border": "rgba(255, 255, 255, 0.15)",
            "hover_text": "#FFFFFF",
            "gauge_bg": "rgba(255, 255, 255, 0.06)",
            "gauge_tick": "#94A3B8",
            "donut_border": "#111827",
            "risk_map": {
                "Low Risk": "#10B981",
                "Medium Risk": "#F59E0B",
                "Critical Risk": "#EF4444"
            }
        }
    else:
        return {
            "bg": "rgba(0,0,0,0)",
            "text_primary": "#0F172A",
            "text_secondary": "#64748B",
            "grid_color": "#F1F5F9",
            "hover_bg": "#FFFFFF",
            "hover_border": "#E2E8F0",
            "hover_text": "#0F172A",
            "gauge_bg": "#F1F5F9",
            "gauge_tick": "#64748B",
            "donut_border": "#FFFFFF",
            "risk_map": {
                "Low Risk": "#10B981",
                "Medium Risk": "#F59E0B",
                "Critical Risk": "#EF4444"
            }
        }


def apply_chart_theme(
    fig: go.Figure,
    height: int = 310,
    is_dark: bool = False
) -> go.Figure:
    """Áp dụng theme tương thích Dark/Light và loại bỏ hoàn toàn đè chữ tiêu đề."""
    palette = get_theme_palette(is_dark)

    fig.update_layout(
        paper_bgcolor=palette["bg"],
        plot_bgcolor=palette["bg"],
        height=height,
        margin=dict(l=15, r=15, t=25, b=20),
        font=dict(family="Plus Jakarta Sans", size=11, color=palette["text_secondary"]),
        hoverlabel=dict(
            bgcolor=palette["hover_bg"],
            bordercolor=palette["hover_border"],
            font=dict(family="Plus Jakarta Sans", size=12, color=palette["hover_text"])
        ),
        legend=dict(
            title_text="",  # Xóa bỏ tiêu đề Predicted_Risk_Tier gây đè chữ
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=palette["text_secondary"], size=10, family="Plus Jakarta Sans")
        )
    )
    fig.update_xaxes(
        gridcolor=palette["grid_color"],
        zerolinecolor=palette["grid_color"],
        tickfont=dict(color=palette["text_secondary"], family="Plus Jakarta Sans")
    )
    fig.update_yaxes(
        gridcolor=palette["grid_color"],
        zerolinecolor=palette["grid_color"],
        tickfont=dict(color=palette["text_secondary"], family="Plus Jakarta Sans")
    )
    return fig


def create_genre_churn_chart(genre_df: pd.DataFrame, is_dark: bool = False) -> go.Figure:
    """Biểu đồ thanh ngang tỷ lệ rời bỏ theo thể loại (loại bỏ title nội bộ để không đè chữ)."""
    palette = get_theme_palette(is_dark)
    color_scale = [[0, "#60A5FA"], [1, "#2563EB"]] if not is_dark else [[0, "#38BDF8"], [1, "#6366F1"]]

    fig = px.bar(
        genre_df,
        x='Churn_Rate_Pct',
        y='GameGenre',
        orientation='h',
        text='Churn_Rate_Pct',
        color='Churn_Rate_Pct',
        color_continuous_scale=color_scale,
        labels={'Churn_Rate_Pct': 'Tỷ lệ Churn (%)', 'GameGenre': 'Thể loại Game'}
    )
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside',
        textfont=dict(family="Plus Jakarta Sans", size=11, color=palette["text_primary"]),
        marker=dict(line=dict(width=0))
    )
    fig.update_coloraxes(showscale=False)
    return apply_chart_theme(fig, height=300, is_dark=is_dark)


def create_risk_donut_chart(risk_df: pd.DataFrame, total_count: int, is_dark: bool = False) -> go.Figure:
    """Biểu đồ Donut phân tầng rủi ro (đã sửa triệt để lỗi đè chữ tiêu đề và legend)."""
    palette = get_theme_palette(is_dark)

    fig = px.pie(
        risk_df,
        names='Risk_Tier',
        values='Count',
        color='Risk_Tier',
        color_discrete_map=palette["risk_map"],
        hole=0.62
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent',
        textfont=dict(family="Plus Jakarta Sans", size=12, color="#FFFFFF"),
        marker=dict(line=dict(color=palette["donut_border"], width=3))
    )
    fig.add_annotation(
        text=f"<b>{total_count:,}</b><br><span style='font-size:10px; color:{palette['text_secondary']};'>PLAYERS</span>",
        showarrow=False,
        font=dict(family="Plus Jakarta Sans", size=15, color=palette["text_primary"]),
        x=0.5, y=0.5
    )
    # Tăng margin trên để legend không bao giờ chạm vào đồ thị
    return apply_chart_theme(fig, height=300, is_dark=is_dark)


def create_playtime_risk_scatter(df: pd.DataFrame, sample_size: int = 1500, is_dark: bool = False) -> go.Figure:
    """Biểu đồ phân tán tương quan (đã xóa legend_title_text để legend không đè lên góc trên)."""
    palette = get_theme_palette(is_dark)
    sample_df = df.sample(min(sample_size, len(df)), random_state=42) if len(df) > 0 else df

    fig = px.scatter(
        sample_df,
        x='TotalWeeklyMinutes',
        y='Churn_Probability',
        color='Predicted_Risk_Tier',
        color_discrete_map=palette["risk_map"],
        opacity=0.65,
        labels={'TotalWeeklyMinutes': 'Số phút chơi/tuần', 'Churn_Probability': 'Xác suất Churn'}
    )
    fig.update_traces(marker=dict(size=5))
    return apply_chart_theme(fig, height=310, is_dark=is_dark)


def create_spender_comparison_chart(spender_df: pd.DataFrame, is_dark: bool = False) -> go.Figure:
    """Biểu đồ cột so sánh tỷ lệ Churn Spender vs F2P."""
    palette = get_theme_palette(is_dark)
    colors = ["#2563EB", "#93C5FD"] if not is_dark else ["#6366F1", "#38BDF8"]

    fig = px.bar(
        spender_df,
        x='Group',
        y='Churn_Pct',
        color='Group',
        color_discrete_sequence=colors,
        text='Churn_Pct',
        labels={'Group': 'Phân khúc', 'Churn_Pct': 'Tỷ lệ Churn (%)'}
    )
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside',
        textfont=dict(family="Plus Jakarta Sans", size=12, color=palette["text_primary"]),
        width=0.35
    )
    fig.update_layout(showlegend=False)
    return apply_chart_theme(fig, height=300, is_dark=is_dark)


def create_gauge_meter(churn_prob_pct: float, risk_tier: str, is_dark: bool = False) -> go.Figure:
    """Đồng hồ đo xác suất Churn (xóa title nội bộ của Plotly để loại bỏ hoàn toàn đè chữ)."""
    palette = get_theme_palette(is_dark)
    bar_color = palette["risk_map"]["Critical Risk"] if risk_tier == "Critical Risk" else (
        palette["risk_map"]["Medium Risk"] if risk_tier == "Medium Risk" else palette["risk_map"]["Low Risk"]
    )

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=churn_prob_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'suffix': "%", 'font': {'family': 'Plus Jakarta Sans', 'size': 38, 'color': bar_color}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': palette["gauge_tick"], 'tickfont': {'color': palette["gauge_tick"], 'size': 11}},
            'bar': {'color': bar_color, 'thickness': 0.28},
            'bgcolor': palette["gauge_bg"],
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': "rgba(16, 185, 129, 0.15)"},
                {'range': [50, 80], 'color': "rgba(245, 158, 11, 0.15)"},
                {'range': [80, 100], 'color': "rgba(239, 68, 68, 0.15)"}
            ],
            'threshold': {
                'line': {'color': palette["risk_map"]["Critical Risk"], 'width': 3},
                'thickness': 0.8,
                'value': 80
            }
        }
    ))

    # Tối ưu margin để không bị cắt số và vòng cung
    fig.update_layout(
        paper_bgcolor=palette["bg"],
        plot_bgcolor=palette["bg"],
        height=270,
        margin=dict(l=25, r=25, t=15, b=15)
    )
    return fig
