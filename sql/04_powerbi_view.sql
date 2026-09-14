-- sql/04_powerbi_view.sql
DROP VIEW IF EXISTS view_powerbi_churn_analytics;
CREATE VIEW view_powerbi_churn_analytics AS
SELECT 
    PlayerID,
    Age,
    Gender,
    Location,
    GameGenre,
    GameDifficulty,
    PlayTimeHours,
    PlayerLevel,
    SessionsPerWeek,
    AvgSessionDurationMinutes,
    InGamePurchases,
    AchievementsUnlocked,
    IsChurn,
    Churn_Probability,
    Predicted_Risk_Tier,
    -- Đặc trưng tính toán trực tiếp bằng SQL
    ROUND(SessionsPerWeek * AvgSessionDurationMinutes, 2) AS TotalWeeklyMinutes,
    CASE 
        WHEN PlayerLevel = 0 THEN PlayTimeHours
        ELSE ROUND(PlayTimeHours / PlayerLevel, 4)
    END AS PlayTimePerLevel,
    CASE 
        WHEN PlayerLevel = 0 THEN AchievementsUnlocked
        ELSE ROUND(CAST(AchievementsUnlocked AS REAL) / PlayerLevel, 4)
    END AS AchievementsPerLevel,
    -- Đề xuất hành động cho đội vận hành game
    CASE 
        WHEN Churn_Probability >= 0.80 AND InGamePurchases = 1 THEN 'Action: Send VIP Giftcode & Exclusive Quest'
        WHEN Churn_Probability >= 0.80 AND InGamePurchases = 0 THEN 'Action: Send Comeback Energy / Free Gems'
        WHEN Churn_Probability >= 0.50 THEN 'Action: Push Notification for Daily Login'
        ELSE 'Status: Healthy / Active'
    END AS Retention_Action_Plan
FROM players;
