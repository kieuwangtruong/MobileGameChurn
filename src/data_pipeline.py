import sqlite3
from pathlib import Path
import joblib, numpy as np, pandas as pd

def run_database_pipeline():
    base_dir = Path(__file__).resolve().parent.parent
    raw_path = base_dir / 'data' / 'raw' / 'online_gaming_behavior_dataset.csv'
    model_path = base_dir / 'models' / 'best_model.joblib'
    feature_names_path = base_dir / 'models' / 'model_features.joblib'
    db_path = base_dir / 'data' / 'game_analytics.db'

    df = pd.read_csv(raw_path)
    model = joblib.load(model_path)
    feature_names = joblib.load(feature_names_path)

    # Biến đổi đặc trưng để đưa qua mô hình
    df_feat = df.copy()
    df_feat['TotalWeeklyMinutes'] = df_feat['SessionsPerWeek'] * df_feat['AvgSessionDurationMinutes']
    df_feat['AvgWeeklyPlayHours'] = df_feat['TotalWeeklyMinutes'] / 60.0
    df_feat['PlayTimePerLevel'] = np.where(df_feat['PlayerLevel'] == 0, df_feat['PlayTimeHours'], df_feat['PlayTimeHours'] / df_feat['PlayerLevel'])
    df_feat['AchievementsPerLevel'] = np.where(df_feat['PlayerLevel'] == 0, df_feat['AchievementsUnlocked'], df_feat['AchievementsUnlocked'] / df_feat['PlayerLevel'])
    df_feat['AchievementsPerHour'] = np.where(df_feat['PlayTimeHours'] == 0, 0.0, df_feat['AchievementsUnlocked'] / df_feat['PlayTimeHours'])
    df_feat['EngagementIntensity'] = df_feat['AvgSessionDurationMinutes'] / (df_feat['PlayTimeHours'] + 1.0)
    df_feat['GameDifficulty'] = df_feat['GameDifficulty'].map({'Easy': 1, 'Medium': 2, 'Hard': 3})
    df_feat['IsMale'] = (df_feat['Gender'] == 'Male').astype(int)
    df_encoded = pd.get_dummies(df_feat, columns=['GameGenre', 'Location'], drop_first=True, dtype=int)

    X = df_encoded[feature_names]
    proba = model.predict_proba(X)[:, 1]

    df['IsChurn'] = (df['EngagementLevel'] == 'Low').astype(int)
    df['Churn_Probability'] = np.round(proba, 4)
    df['Predicted_Risk_Tier'] = np.where(proba >= 0.8, 'Critical Risk', np.where(proba >= 0.5, 'Medium Risk', 'Low Risk'))

    conn = sqlite3.connect(db_path)
    df.to_sql('players', conn, if_exists='replace', index=False)
    
    # Tạo View phục vụ Power BI
    view_sql = Path(base_dir / 'sql' / '04_powerbi_view.sql').read_text(encoding='utf-8')
    conn.executescript(view_sql)
    conn.close()

    # Xuất file CSV sạch sẵn sàng cho Power BI
    powerbi_csv = base_dir / 'data' / 'processed' / 'powerbi_game_churn_dataset.csv'
    df.to_csv(powerbi_csv, index=False)
    print(f"✅ Pipeline hoàn tất: Đã nạp {len(df):,} bản ghi vào {db_path} và xuất {powerbi_csv}!")

if __name__ == '__main__':
    run_database_pipeline()
