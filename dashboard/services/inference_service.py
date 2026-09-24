"""Inference service wrapping XGBoost Churn Model with Streamlit Resource Caching."""
import sys
from pathlib import Path
from typing import Dict, Any
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.model import get_predictor, ChurnPredictor


@st.cache_resource(show_spinner="🧠 Đang nạp mô hình AI XGBoost Classifier...")
def load_ml_predictor() -> ChurnPredictor:
    """Nạp và cache instance của ChurnPredictor trong bộ nhớ ứng dụng."""
    return get_predictor()


def get_simulation_presets() -> Dict[str, Dict[str, Any]]:
    """Cung cấp các Persona game thủ điển hình cho LiveOps Simulator."""
    return {
        "newbie_risk": {
            "label": "🚨 Tân Thủ Nguy Cơ (Newbie Drop-off)",
            "description": "Người chơi mới cài đặt, gặp độ khó cao và thời lượng chơi thấp.",
            "data": {
                "Age": 19, "Gender": "Male", "Location": "USA", "GameGenre": "Action",
                "GameDifficulty": "Hard", "PlayTimeHours": 1.5, "InGamePurchases": 0,
                "SessionsPerWeek": 1, "AvgSessionDurationMinutes": 15.0,
                "PlayerLevel": 2, "AchievementsUnlocked": 1
            }
        },
        "whale_risk": {
            "label": "💎 Whale Sắp Rời Bỏ (High-Value Spender At-Risk)",
            "description": "Đại gia từng nạp nhiều nhưng thời gian và tần suất chơi giảm mạnh gần đây.",
            "data": {
                "Age": 28, "Gender": "Female", "Location": "Europe", "GameGenre": "RPG",
                "GameDifficulty": "Medium", "PlayTimeHours": 8.0, "InGamePurchases": 1,
                "SessionsPerWeek": 2, "AvgSessionDurationMinutes": 20.0,
                "PlayerLevel": 15, "AchievementsUnlocked": 6
            }
        },
        "hardcore_f2p": {
            "label": "⚔️ Game Thủ Cày Cuốc (Hardcore F2P Grinder)",
            "description": "Chưa nạp tiền nhưng có thời lượng chơi và cấp độ vượt trội.",
            "data": {
                "Age": 22, "Gender": "Male", "Location": "Asia", "GameGenre": "Strategy",
                "GameDifficulty": "Medium", "PlayTimeHours": 22.0, "InGamePurchases": 0,
                "SessionsPerWeek": 12, "AvgSessionDurationMinutes": 60.0,
                "PlayerLevel": 45, "AchievementsUnlocked": 35
            }
        },
        "loyal_vip": {
            "label": "👑 VIP Trung Thành (Loyal VIP Core)",
            "description": "Game thủ nạp thẻ, tần suất chơi cao và gắn bó lâu dài.",
            "data": {
                "Age": 30, "Gender": "Male", "Location": "USA", "GameGenre": "Simulation",
                "GameDifficulty": "Easy", "PlayTimeHours": 24.0, "InGamePurchases": 1,
                "SessionsPerWeek": 15, "AvgSessionDurationMinutes": 80.0,
                "PlayerLevel": 60, "AchievementsUnlocked": 45
            }
        }
    }
