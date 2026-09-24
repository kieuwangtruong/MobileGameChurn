"""Data loading, caching and aggregation service for Game LiveOps Dashboard."""
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / 'data' / 'game_analytics.db'
FALLBACK_CSV = BASE_DIR / 'data' / 'processed' / 'powerbi_game_churn_dataset.csv'

# Giả định chuẩn ngành Game Mobile: Chi tiêu trung bình của 1 Spender (ARPU/Month)
ASSUMED_SPENDER_MONTHLY_ARPU = 25.0


@st.cache_data(ttl=3600, show_spinner="⚡ Đang tải dữ liệu Game Analytics...")
def load_game_dataset() -> pd.DataFrame:
    """Tải tập dữ liệu người chơi từ SQLite Database (hoặc CSV fallback) kèm xử lý chuẩn hóa."""
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            # Truy vấn từ View tối ưu cho analytics
            query = "SELECT * FROM view_powerbi_churn_analytics"
            df = pd.read_sql_query(query, conn)
            conn.close()
        except Exception:
            # Fallback sang bảng players nếu view chưa được tạo
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query("SELECT * FROM players", conn)
            conn.close()
    elif FALLBACK_CSV.exists():
        df = pd.read_csv(FALLBACK_CSV)
    else:
        raise FileNotFoundError(
            f"Không tìm thấy dữ liệu tại {DB_PATH} hoặc {FALLBACK_CSV}. "
            "Vui lòng chạy `python src/data_pipeline.py` để khởi tạo cơ sở dữ liệu."
        )

    # Đảm bảo các trường phái sinh cần thiết luôn sẵn sàng
    if 'TotalWeeklyMinutes' not in df.columns:
        df['TotalWeeklyMinutes'] = df['SessionsPerWeek'] * df['AvgSessionDurationMinutes']
    if 'PlayTimePerLevel' not in df.columns:
        df['PlayTimePerLevel'] = np.where(
            df['PlayerLevel'] == 0,
            df['PlayTimeHours'],
            df['PlayTimeHours'] / df['PlayerLevel']
        )
    if 'AchievementsPerLevel' not in df.columns:
        df['AchievementsPerLevel'] = np.where(
            df['PlayerLevel'] == 0,
            df['AchievementsUnlocked'],
            df['AchievementsUnlocked'] / df['PlayerLevel']
        )
    if 'Retention_Action_Plan' not in df.columns:
        df['Retention_Action_Plan'] = np.where(
            (df['Churn_Probability'] >= 0.80) & (df['InGamePurchases'] == 1),
            'VIP Giftcode & Exclusive Quest',
            np.where(
                (df['Churn_Probability'] >= 0.80) & (df['InGamePurchases'] == 0),
                'Comeback Energy / Free Gacha',
                np.where(
                    df['Churn_Probability'] >= 0.50,
                    'Daily Push Notification & 2x EXP',
                    'Guild Invitation & Event Update'
                )
            )
        )

    return df


def get_filter_options(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Trích xuất các danh mục bộ lọc duy nhất cho Sidebar."""
    return {
        "genres": sorted(df['GameGenre'].dropna().unique().tolist()),
        "locations": sorted(df['Location'].dropna().unique().tolist()),
    }


def filter_players_data(
    df: pd.DataFrame,
    genres: Optional[List[str]] = None,
    locations: Optional[List[str]] = None,
    spender_choice: str = "Tất cả"
) -> pd.DataFrame:
    """Áp dụng các điều kiện lọc từ Sidebar lên tập dữ liệu."""
    filtered = df.copy()

    if genres:
        filtered = filtered[filtered['GameGenre'].isin(genres)]

    if locations:
        filtered = filtered[filtered['Location'].isin(locations)]

    if spender_choice == "Chỉ Spender (Có Nạp)":
        filtered = filtered[filtered['InGamePurchases'] == 1]
    elif spender_choice == "Chỉ F2P (Miễn Phí)":
        filtered = filtered[filtered['InGamePurchases'] == 0]

    return filtered


def compute_executive_kpis(df: pd.DataFrame, benchmark_churn_rate: float = 20.0) -> Dict[str, Any]:
    """Tính toán bộ chỉ số KPI cấp điều hành (Executive & LiveOps)."""
    total_players = len(df)
    if total_players == 0:
        return {
            "total_players": 0,
            "actual_churn_pct": 0.0,
            "churn_delta": 0.0,
            "spender_conversion_pct": 0.0,
            "avg_playtime_hours": 0.0,
            "critical_risk_count": 0,
            "revenue_at_risk_usd": 0.0
        }

    actual_churn_pct = float(df['IsChurn'].mean() * 100)
    churn_delta = actual_churn_pct - benchmark_churn_rate
    spender_conversion_pct = float(df['InGamePurchases'].mean() * 100)
    avg_playtime_hours = float(df['PlayTimeHours'].mean())
    critical_risk_count = int((df['Predicted_Risk_Tier'] == 'Critical Risk').sum())

    # Tính doanh thu có nguy cơ mất (Revenue at Risk) từ Spenders rơi vào Critical Risk
    critical_spenders = len(df[(df['Predicted_Risk_Tier'] == 'Critical Risk') & (df['InGamePurchases'] == 1)])
    revenue_at_risk_usd = float(critical_spenders * ASSUMED_SPENDER_MONTHLY_ARPU)

    return {
        "total_players": total_players,
        "actual_churn_pct": round(actual_churn_pct, 2),
        "churn_delta": round(churn_delta, 2),
        "spender_conversion_pct": round(spender_conversion_pct, 2),
        "avg_playtime_hours": round(avg_playtime_hours, 1),
        "critical_risk_count": critical_risk_count,
        "critical_spenders": critical_spenders,
        "revenue_at_risk_usd": revenue_at_risk_usd
    }


def get_genre_churn_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Thống kê tỷ lệ Churn theo Thể loại game."""
    if df.empty:
        return pd.DataFrame(columns=['GameGenre', 'Churn_Rate_Pct', 'Total_Players'])
    stats = df.groupby('GameGenre').agg(
        Churn_Rate_Pct=('IsChurn', lambda x: round(x.mean() * 100, 2)),
        Total_Players=('PlayerID', 'count')
    ).reset_index()
    return stats.sort_values(by='Churn_Rate_Pct', ascending=True)


def get_risk_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Phân bố người chơi theo 3 phân tầng rủi ro AI."""
    if df.empty:
        return pd.DataFrame(columns=['Risk_Tier', 'Count', 'Percentage'])
    counts = df['Predicted_Risk_Tier'].value_counts().reset_index()
    counts.columns = ['Risk_Tier', 'Count']
    counts['Percentage'] = (counts['Count'] / len(df) * 100).round(1)
    return counts


def get_spender_churn_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """So sánh tỷ lệ rời bỏ giữa Spender (Trả phí) và F2P (Miễn phí)."""
    if df.empty:
        return pd.DataFrame(columns=['Group', 'Churn_Pct', 'Player_Count'])
    comp = df.groupby('InGamePurchases').agg(
        Churn_Pct=('IsChurn', lambda x: round(x.mean() * 100, 2)),
        Player_Count=('PlayerID', 'count')
    ).reset_index()
    comp['Group'] = comp['InGamePurchases'].map({1: 'Spender (Có nạp)', 0: 'F2P (Miễn phí)'})
    return comp
