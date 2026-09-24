"""Feature engineering and transformation pipeline for inference."""
from pathlib import Path
from typing import Dict, Any, List, Union
import numpy as np
import pandas as pd
import joblib

FEATURE_NAMES: List[str] = [
    'Age', 'PlayTimeHours', 'InGamePurchases', 'GameDifficulty',
    'SessionsPerWeek', 'AvgSessionDurationMinutes', 'PlayerLevel',
    'AchievementsUnlocked', 'TotalWeeklyMinutes', 'AvgWeeklyPlayHours',
    'PlayTimePerLevel', 'AchievementsPerLevel', 'AchievementsPerHour',
    'EngagementIntensity', 'IsMale', 'GameGenre_RPG',
    'GameGenre_Simulation', 'GameGenre_Sports', 'GameGenre_Strategy',
    'Location_Europe', 'Location_Other', 'Location_USA'
]

DIFFICULTY_MAPPING = {'Easy': 1, 'Medium': 2, 'Hard': 3}


def prepare_features(data: Union[Dict[str, Any], pd.DataFrame]) -> pd.DataFrame:
    """Chuyển đổi dữ liệu thô (raw profile) thành ma trận đặc trưng chuẩn hóa 22 cột."""
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        df = data.copy()

    # 1. Feature Engineering (Domain Metrics)
    total_weekly_min = df['SessionsPerWeek'] * df['AvgSessionDurationMinutes']
    df_feat = pd.DataFrame()
    
    df_feat['Age'] = df['Age'].astype(float)
    df_feat['PlayTimeHours'] = df['PlayTimeHours'].astype(float)
    df_feat['InGamePurchases'] = df['InGamePurchases'].astype(int)
    
    # Map GameDifficulty
    if df['GameDifficulty'].dtype == object or isinstance(df['GameDifficulty'].iloc[0], str):
        df_feat['GameDifficulty'] = df['GameDifficulty'].map(DIFFICULTY_MAPPING).fillna(2).astype(int)
    else:
        df_feat['GameDifficulty'] = df['GameDifficulty'].astype(int)

    df_feat['SessionsPerWeek'] = df['SessionsPerWeek'].astype(float)
    df_feat['AvgSessionDurationMinutes'] = df['AvgSessionDurationMinutes'].astype(float)
    df_feat['PlayerLevel'] = df['PlayerLevel'].astype(float)
    df_feat['AchievementsUnlocked'] = df['AchievementsUnlocked'].astype(float)
    
    df_feat['TotalWeeklyMinutes'] = total_weekly_min.astype(float)
    df_feat['AvgWeeklyPlayHours'] = (total_weekly_min / 60.0).astype(float)
    
    # Safe division for Level & Hours
    df_feat['PlayTimePerLevel'] = np.where(
        df_feat['PlayerLevel'] == 0,
        df_feat['PlayTimeHours'],
        df_feat['PlayTimeHours'] / df_feat['PlayerLevel']
    )
    df_feat['AchievementsPerLevel'] = np.where(
        df_feat['PlayerLevel'] == 0,
        df_feat['AchievementsUnlocked'],
        df_feat['AchievementsUnlocked'] / df_feat['PlayerLevel']
    )
    df_feat['AchievementsPerHour'] = np.where(
        df_feat['PlayTimeHours'] == 0,
        0.0,
        df_feat['AchievementsUnlocked'] / df_feat['PlayTimeHours']
    )
    df_feat['EngagementIntensity'] = df_feat['AvgSessionDurationMinutes'] / (df_feat['PlayTimeHours'] + 1.0)
    
    # Binary Gender (Male = 1, Female = 0)
    df_feat['IsMale'] = (df['Gender'].astype(str).str.strip().str.capitalize() == 'Male').astype(int)
    
    # One-hot GameGenre (Reference: Action)
    genre_series = df['GameGenre'].astype(str).str.strip()
    df_feat['GameGenre_RPG'] = (genre_series == 'RPG').astype(int)
    df_feat['GameGenre_Simulation'] = (genre_series == 'Simulation').astype(int)
    df_feat['GameGenre_Sports'] = (genre_series == 'Sports').astype(int)
    df_feat['GameGenre_Strategy'] = (genre_series == 'Strategy').astype(int)
    
    # One-hot Location (Reference: Asia)
    loc_series = df['Location'].astype(str).str.strip()
    df_feat['Location_Europe'] = (loc_series == 'Europe').astype(int)
    df_feat['Location_Other'] = (loc_series == 'Other').astype(int)
    df_feat['Location_USA'] = (loc_series == 'USA').astype(int)
    
    # Đảm bảo đúng thứ tự 22 cột đã huấn luyện
    return df_feat[FEATURE_NAMES]
