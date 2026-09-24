"""FastAPI Service for Game Churn Prediction & Retention Advisory."""
from typing import List, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
from src.model import get_predictor

app = FastAPI(
    title="Mobile Game Churn Prediction API",
    description="Production-ready REST API predicting player churn risk and recommending LiveOps retention actions.",
    version="1.0.0"
)

# Enable CORS for frontend / dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlayerProfile(BaseModel):
    Age: int = Field(..., ge=10, le=100, description="Tuổi của người chơi (10-100)", json_schema_extra={"example": 24})
    Gender: Literal["Male", "Female"] = Field(..., description="Giới tính", json_schema_extra={"example": "Male"})
    Location: Literal["USA", "Europe", "Asia", "Other"] = Field(..., description="Khu vực địa lý", json_schema_extra={"example": "USA"})
    GameGenre: Literal["Action", "RPG", "Simulation", "Sports", "Strategy"] = Field(..., description="Thể loại game", json_schema_extra={"example": "RPG"})
    GameDifficulty: Literal["Easy", "Medium", "Hard"] = Field(..., description="Độ khó đang chơi", json_schema_extra={"example": "Medium"})
    PlayTimeHours: float = Field(..., ge=0.0, le=500.0, description="Tổng số giờ chơi tích lũy", json_schema_extra={"example": 15.5})
    InGamePurchases: Literal[0, 1] = Field(..., description="Từng nạp tiền trong game (1: Có, 0: Không)", json_schema_extra={"example": 1})
    SessionsPerWeek: int = Field(..., ge=0, le=100, description="Số phiên chơi mỗi tuần", json_schema_extra={"example": 5})
    AvgSessionDurationMinutes: float = Field(..., ge=1.0, le=600.0, description="Thời lượng trung bình mỗi phiên (phút)", json_schema_extra={"example": 35.0})
    PlayerLevel: int = Field(..., ge=1, le=150, description="Cấp độ hiện tại của người chơi", json_schema_extra={"example": 18})
    AchievementsUnlocked: int = Field(..., ge=0, le=100, description="Số thành tựu đã mở khóa", json_schema_extra={"example": 12})


class PredictionResponse(BaseModel):
    churn_probability: float = Field(..., description="Xác suất rời bỏ (0.0 đến 1.0)")
    churn_probability_pct: float = Field(..., description="Xác suất rời bỏ tính theo %")
    prediction: str = Field(..., description="Nhãn phân loại (Churn hoặc Retained)")
    risk_tier: str = Field(..., description="Cấp độ rủi ro (Critical Risk / Medium Risk / Low Risk)")
    recommended_action: str = Field(..., description="Đề xuất hành động giữ chân LiveOps")


class BatchPredictionRequest(BaseModel):
    players: List[PlayerProfile]


class BatchPredictionResponse(BaseModel):
    total_processed: int
    critical_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    results: List[PredictionResponse]


@app.get("/", tags=["General"])
def root():
    """Trang thông tin tổng quan về API."""
    return {
        "service": "Mobile Game Churn Prediction Service",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health",
        "status": "Operational"
    }


@app.get("/health", tags=["General"])
def health_check():
    """Kiểm tra trạng thái hoạt động của mô hình và API."""
    try:
        predictor = get_predictor()
        return {
            "status": "healthy",
            "model_loaded": predictor.model is not None,
            "scaler_loaded": predictor.scaler is not None,
            "feature_count": len(predictor.feature_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_churn(player: PlayerProfile):
    """Dự đoán nguy cơ rời bỏ cho 1 người chơi cụ thể."""
    try:
        predictor = get_predictor()
        result = predictor.predict(player.model_dump())
        return PredictionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
def predict_batch_churn(batch: BatchPredictionRequest):
    """Dự đoán nguy cơ rời bỏ hàng loạt cho danh sách người chơi."""
    try:
        predictor = get_predictor()
        df = pd.DataFrame([p.model_dump() for p in batch.players])
        res_df = predictor.predict_batch(df)
        
        results = []
        for i, row in res_df.iterrows():
            prob = float(row['Churn_Probability'])
            tier = row['Predicted_Risk_Tier']
            pred = "Churn (At-Risk)" if prob >= 0.50 else "Retained (Active)"
            spender = int(batch.players[i].InGamePurchases)
            action = predictor.get_retention_action(prob, spender)
            results.append(PredictionResponse(
                churn_probability=prob,
                churn_probability_pct=round(prob * 100, 2),
                prediction=pred,
                risk_tier=tier,
                recommended_action=action
            ))
            
        tiers = [r.risk_tier for r in results]
        return BatchPredictionResponse(
            total_processed=len(results),
            critical_risk_count=tiers.count("Critical Risk"),
            medium_risk_count=tiers.count("Medium Risk"),
            low_risk_count=tiers.count("Low Risk"),
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")