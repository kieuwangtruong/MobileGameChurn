-- sql/03_player_segmentation.sql
WITH PlayerMetrics AS (
    SELECT 
        PlayerID,
        GameGenre,
        PlayerLevel,
        PlayTimeHours,
        InGamePurchases,
        SessionsPerWeek,
        Churn_Probability,
        -- Window Function: So sánh thời gian chơi với mức trung bình của cùng thể loại game
        ROUND(AVG(PlayTimeHours) OVER (PARTITION BY GameGenre), 2) AS Genre_Avg_Playtime,
        -- Window Function: Phân vị thời gian chơi thành 4 nhóm (Quartiles)
        NTILE(4) OVER (ORDER BY PlayTimeHours) AS Playtime_Quartile
    FROM players
),
PlayerPersonas AS (
    SELECT 
        PlayerID,
        GameGenre,
        PlayerLevel,
        PlayTimeHours,
        InGamePurchases,
        Churn_Probability,
        Genre_Avg_Playtime,
        CASE 
            WHEN InGamePurchases = 1 AND PlayTimeHours >= Genre_Avg_Playtime THEN 'Whale / High-Value'
            WHEN InGamePurchases = 1 AND PlayTimeHours < Genre_Avg_Playtime THEN 'Spender / Casual Buyer'
            WHEN InGamePurchases = 0 AND PlayTimeHours >= Genre_Avg_Playtime THEN 'Hardcore F2P'
            ELSE 'Casual F2P'
        END AS Player_Segment
    FROM PlayerMetrics
)
SELECT 
    Player_Segment,
    COUNT(*) AS Total_Players,
    ROUND(AVG(PlayTimeHours), 2) AS Avg_Hours,
    ROUND(AVG(Churn_Probability) * 100, 2) AS Avg_Churn_Risk_Pct
FROM PlayerPersonas
GROUP BY Player_Segment
ORDER BY Avg_Churn_Risk_Pct DESC;
