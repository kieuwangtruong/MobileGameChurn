DROP TABLE IF EXISTS players;
CREATE TABLE players (
    PlayerID INTEGER PRIMARY KEY,
    Age INTEGER,
    Gender TEXT,
    Location TEXT,
    GameGenre TEXT,
    PlayTimeHours REAL,
    InGamePurchases INTEGER,
    GameDifficulty TEXT,
    SessionsPerWeek INTEGER,
    AvgSessionDurationMinutes REAL,
    PlayerLevel INTEGER,
    AchievementsUnlocked INTEGER,
    EngagementLevel TEXT,
    IsChurn INTEGER,
    Churn_Probability REAL,
    Predicted_Risk_Tier TEXT
);