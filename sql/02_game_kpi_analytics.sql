-- sql/02_game_kpi_analytics.sql
-- 1. Tổng quan KPIs toàn game
SELECT 
    COUNT(*) AS Total_Players,
    ROUND(AVG(IsChurn) * 100, 2) AS Actual_Churn_Rate_Pct,
    ROUND(AVG(Churn_Probability) * 100, 2) AS Predicted_Avg_Churn_Risk_Pct,
    ROUND(AVG(InGamePurchases) * 100, 2) AS Spender_Conversion_Rate_Pct,
    ROUND(AVG(PlayTimeHours), 2) AS Avg_PlayTime_Hours,
    ROUND(AVG(PlayerLevel), 1) AS Avg_Player_Level
FROM players;

-- 2. Tỷ lệ rời bỏ và hành vi theo từng Thể loại Game (GameGenre)
SELECT 
    GameGenre,
    COUNT(*) AS Player_Count,
    ROUND(SUM(InGamePurchases) * 100.0 / COUNT(*), 2) AS Pct_Spenders,
    ROUND(AVG(PlayTimeHours), 2) AS Avg_Playtime,
    ROUND(AVG(IsChurn) * 100, 2) AS Actual_Churn_Rate_Pct,
    ROUND(AVG(Churn_Probability) * 100, 2) AS AI_Predicted_Churn_Rate_Pct
FROM players
GROUP BY GameGenre
ORDER BY Actual_Churn_Rate_Pct DESC;
