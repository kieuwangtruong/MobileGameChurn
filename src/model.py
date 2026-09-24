"""Model inference wrapper for Game Churn Prediction."""
from pathlib import Path
from typing import Dict, Any, List, Union
import joblib
import numpy as np
import pandas as pd
from src.features import prepare_features, FEATURE_NAMES

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'models' / 'best_model.joblib'
SCALER_PATH = BASE_DIR / 'models' / 'scaler.joblib'


class ChurnPredictor:
    """Predictor service encapsulating XGBoost model, Scaler, and Business Rules."""
    
    def __init__(self, model_path: Path = MODEL_PATH, scaler_path: Path = SCALER_PATH):
        if not model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {model_path}")
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler artifact not found at {scaler_path}")
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_names = FEATURE_NAMES

    @staticmethod
    def get_risk_tier(prob: float) -> str:
        """Phân loại cấp độ rủi ro rời bỏ game."""
        if prob >= 0.80:
            return "Critical Risk"
        elif prob >= 0.50:
            return "Medium Risk"
        else:
            return "Low Risk"

    @staticmethod
    def get_retention_action(prob: float, is_spender: int) -> str:
        """Đề xuất hành động giữ chân người chơi (LiveOps Action Plan)."""
        if prob >= 0.80:
            if is_spender == 1:
                return "Tặng VIP Giftcode, gói vật phẩm độc quyền & mở chuỗi nhiệm vụ trở lại game (Comeback Quest)."
            else:
                return "Gửi thông báo Push tặng Năng lượng / Vé quay miễn phí (Comeback Energy / Free Gacha)."
        elif prob >= 0.50:
            return "Kích hoạt thông báo đẩy nhắc điểm danh hàng ngày & thưởng x2 kinh nghiệm (Double EXP)."
        else:
            return "Trạng thái gắn bó tốt: Giới thiệu sự kiện Bang hội (Guild) & tính năng mới."

    def predict(self, raw_data: Union[Dict[str, Any], pd.DataFrame]) -> Dict[str, Any]:
        """Dự đoán xác suất rời bỏ cho 1 người chơi."""
        X = prepare_features(raw_data)
        X_scaled = self.scaler.transform(X)
        
        prob = float(self.model.predict_proba(X_scaled)[0, 1])
        is_churn = int(prob >= 0.50)
        risk_tier = self.get_risk_tier(prob)
        
        # Check spender status
        if isinstance(raw_data, dict):
            spender = int(raw_data.get('InGamePurchases', 0))
        else:
            spender = int(raw_data['InGamePurchases'].iloc[0])
            
        action = self.get_retention_action(prob, spender)
        
        return {
            "churn_probability": round(prob, 4),
            "churn_probability_pct": round(prob * 100, 2),
            "prediction": "Churn (At-Risk)" if is_churn else "Retained (Active)",
            "risk_tier": risk_tier,
            "recommended_action": action
        }

    def predict_batch(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Dự đoán cho tập dữ liệu nhiều người chơi."""
        X = prepare_features(raw_df)
        X_scaled = self.scaler.transform(X)
        probs = self.model.predict_proba(X_scaled)[:, 1]
        
        result_df = raw_df.copy()
        result_df['Churn_Probability'] = np.round(probs, 4)
        result_df['Predicted_Risk_Tier'] = [self.get_risk_tier(p) for p in probs]
        result_df['Prediction'] = np.where(probs >= 0.50, 'Churn', 'Retained')
        return result_df


# Singleton instance
_predictor_instance = None

def get_predictor() -> ChurnPredictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = ChurnPredictor()
    return _predictor_instance
