-- sql/05_powerbi_star_schema.sql
-- Tách cấu trúc phẳng thành chuẩn Star Schema phục vụ Power BI Desktop

-- 1. Dim_Genre: Chi tiết thể loại game
DROP TABLE IF EXISTS Dim_Genre;
CREATE TABLE Dim_Genre AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY GameGenre) AS GenreKey,
    GameGenre,
    CASE 
        WHEN GameGenre IN ('Strategy', 'RPG') THEN 'Hardcore / Midcore'
        WHEN GameGenre IN ('Action', 'Sports') THEN 'Action & Competitive'
        ELSE 'Casual / Simulation'
    END AS GenreCategory
FROM (SELECT DISTINCT GameGenre FROM players);

-- 2. Dim_Location: Thị trường địa lý & Phân tầng Market Tier
DROP TABLE IF EXISTS Dim_Location;
CREATE TABLE Dim_Location AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY Location) AS LocationKey,
    Location,
    CASE 
        WHEN Location = 'USA' THEN 'Tier 1 (High ARPU)'
        WHEN Location = 'Europe' THEN 'Tier 1 (Mature)'
        WHEN Location = 'Asia' THEN 'Growth Market (High Volume)'
        ELSE 'Rest of World'
    END AS MarketTier
FROM (SELECT DISTINCT Location FROM players);

-- 3. Dim_GameDifficulty: Độ khó game & Thứ tự sắp xếp
DROP TABLE IF EXISTS Dim_GameDifficulty;
CREATE TABLE Dim_GameDifficulty AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY 
        CASE GameDifficulty 
            WHEN 'Easy' THEN 1 
            WHEN 'Medium' THEN 2 
            WHEN 'Hard' THEN 3 
        END
    ) AS DifficultyKey,
    GameDifficulty,
    CASE GameDifficulty 
        WHEN 'Easy' THEN 1 
        WHEN 'Medium' THEN 2 
        WHEN 'Hard' THEN 3 
    END AS DifficultyOrder
FROM (SELECT DISTINCT GameDifficulty FROM players);

-- 4. Dim_RiskTier: Phân tầng rủi ro & Chiến dịch giữ chân chuẩn LiveOps
DROP TABLE IF EXISTS Dim_RiskTier;
CREATE TABLE Dim_RiskTier (
    RiskTierKey INTEGER PRIMARY KEY,
    RiskTierName TEXT,
    RiskLevelRange TEXT,
    PriorityOrder INTEGER,
    DefaultActionPlan TEXT
);

INSERT INTO Dim_RiskTier VALUES
(1, 'Critical Risk', '>= 80%', 1, 'Emergency Retention (VIP Giftcode / Comeback Energy)'),
(2, 'Medium Risk', '50% - 79%', 2, 'Engagement Push (Daily Login Boost / Double EXP)'),
(3, 'Low Risk', '< 50%', 3, 'Community & Social (Guild Invites / New Feature Previews)');

-- 5. Fact_PlayerActivity: Bảng Fact trung tâm chuẩn hóa các khóa ngoại
DROP TABLE IF EXISTS Fact_PlayerActivity;
CREATE TABLE Fact_PlayerActivity AS
SELECT 
    p.PlayerID,
    p.Age,
    p.Gender,
    g.GenreKey,
    l.LocationKey,
    d.DifficultyKey,
    CASE 
        WHEN p.Churn_Probability >= 0.80 THEN 1
        WHEN p.Churn_Probability >= 0.50 THEN 2
        ELSE 3
    END AS RiskTierKey,
    p.PlayTimeHours,
    p.InGamePurchases,
    p.SessionsPerWeek,
    p.AvgSessionDurationMinutes,
    p.PlayerLevel,
    p.AchievementsUnlocked,
    p.IsChurn,
    p.Churn_Probability,
    ROUND(p.SessionsPerWeek * p.AvgSessionDurationMinutes, 2) AS TotalWeeklyMinutes,
    CASE WHEN p.PlayerLevel = 0 THEN p.PlayTimeHours ELSE ROUND(p.PlayTimeHours / p.PlayerLevel, 4) END AS PlayTimePerLevel,
    CASE WHEN p.PlayerLevel = 0 THEN p.AchievementsUnlocked ELSE ROUND(CAST(p.AchievementsUnlocked AS REAL) / p.PlayerLevel, 4) END AS AchievementsPerLevel
FROM players p
LEFT JOIN Dim_Genre g ON p.GameGenre = g.GameGenre
LEFT JOIN Dim_Location l ON p.Location = l.Location
LEFT JOIN Dim_GameDifficulty d ON p.GameDifficulty = d.GameDifficulty;
