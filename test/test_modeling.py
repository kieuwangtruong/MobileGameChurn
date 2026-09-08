"""Unit tests for Modeling Section and Artifact Integrity."""
import pytest
import pandas as pd
import numpy as np
import joblib
from pathlib import Path


def test_no_target_or_id_leakage_in_features():
    """Đảm bảo ma trận đặc trưng không chứa PlayerID hoặc nhãn rò rỉ từ target."""
    train_path = Path("data/processed/train_features.csv")
    if not train_path.exists():
        train_path = Path("../data/processed/train_features.csv")
    
    df = pd.read_csv(train_path, nrows=50)
    forbidden_columns = {"PlayerID", "EngagementLevel", "EngagementCode"}
    
    present_forbidden = forbidden_columns.intersection(set(df.columns))
    assert len(present_forbidden) == 0, f"Rò rỉ dữ liệu: phát hiện cột cấm trong features: {present_forbidden}"


def test_model_artifact_prediction_contract():
    """Kiểm tra mô hình đã lưu có thể load và trả ra output xác suất hợp lệ."""
    model_path = Path("models/best_model.joblib")
    if not model_path.exists():
        model_path = Path("../models/best_model.joblib")
    
    assert model_path.exists(), "Không tìm thấy file artifact models/best_model.joblib"
    
    model = joblib.load(model_path)
    # Tạo 5 dòng dữ liệu giả lập có đúng số lượng đặc trưng
    n_features = getattr(model, "n_features_in_", 20)
    dummy_input = np.random.randn(5, n_features)
    
    probabilities = model.predict_proba(dummy_input)[:, 1]
    assert len(probabilities) == 5, "Số lượng xác suất dự đoán không khớp kích thước mẫu test."
    assert np.all((probabilities >= 0.0) & (probabilities <= 1.0)), "Xác suất dự đoán nằm ngoài dải [0, 1]."
