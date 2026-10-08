-- Bellabeat smart device analysis (SQLite)
-- Source table: daily_activity, imported from data/dailyActivity_merged.csv
--   sqlite3 bellabeat.db
--   .mode csv
--   .import data/dailyActivity_merged.csv daily_activity

-- 1. Data check: users, date range, duplicates, zero-step days
SELECT COUNT(DISTINCT Id)                                   AS users,
       COUNT(*)                                             AS user_days,
       SUM(CASE WHEN CAST(TotalSteps AS INTEGER) = 0 THEN 1 ELSE 0 END) AS zero_step_days
FROM daily_activity;

SELECT Id, ActivityDate, COUNT(*) AS n
FROM daily_activity
GROUP BY Id, ActivityDate
HAVING n > 1;                                               -- expect no rows

-- 2. Overall daily averages on worn days (0 steps = tracker not worn; those days are excluded)
SELECT ROUND(AVG(TotalSteps), 0)                            AS avg_daily_steps,
       ROUND(AVG(Calories), 0)                              AS avg_daily_calories,
       ROUND(AVG(SedentaryMinutes) / 60.0, 1)               AS sedentary_hours_per_day,
       ROUND(AVG(VeryActiveMinutes + FairlyActiveMinutes), 1) AS active_minutes_per_day,
       ROUND(100.0 * AVG(CASE WHEN CAST(TotalSteps AS INTEGER) >= 10000 THEN 1 ELSE 0 END), 1) AS pct_days_10k
FROM daily_activity
WHERE CAST(TotalSteps AS INTEGER) > 0;

-- 3. User segmentation by average daily steps on worn days
WITH user_avg AS (
    SELECT Id, AVG(CAST(TotalSteps AS INTEGER)) AS avg_steps
    FROM daily_activity
    WHERE CAST(TotalSteps AS INTEGER) > 0
    GROUP BY Id
)
SELECT CASE
           WHEN avg_steps < 5000  THEN '1 Sedentary'
           WHEN avg_steps < 7500  THEN '2 Lightly Active'
           WHEN avg_steps < 10000 THEN '3 Fairly Active'
           ELSE '4 Very Active'
       END                                                  AS segment,
       COUNT(*)                                             AS users,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM user_avg), 2) AS pct_users
FROM user_avg
GROUP BY segment
ORDER BY segment;

-- 4. Average steps by weekday on worn days (ActivityDate is M/D/YYYY text in the raw file)
WITH parsed AS (
    SELECT CAST(TotalSteps AS INTEGER) AS TotalSteps,
           printf('%04d-%02d-%02d',
                  CAST(substr(ActivityDate, instr(ActivityDate, '/') + instr(substr(ActivityDate, instr(ActivityDate, '/') + 1), '/') + 1) AS INTEGER),
                  CAST(substr(ActivityDate, 1, instr(ActivityDate, '/') - 1) AS INTEGER),
                  CAST(substr(substr(ActivityDate, instr(ActivityDate, '/') + 1), 1, instr(substr(ActivityDate, instr(ActivityDate, '/') + 1), '/') - 1) AS INTEGER)
           ) AS activity_date
    FROM daily_activity
    WHERE CAST(TotalSteps AS INTEGER) > 0
)
SELECT strftime('%w', activity_date)                        AS weekday_num,   -- 0 = Sunday
       ROUND(AVG(TotalSteps), 0)                            AS avg_steps
FROM parsed
GROUP BY weekday_num
ORDER BY weekday_num;

-- 5. Share of user-days by daily step band
SELECT CASE
           WHEN CAST(TotalSteps AS INTEGER) = 0     THEN '1 0 (not worn)'
           WHEN CAST(TotalSteps AS INTEGER) < 5000  THEN '2 < 5k'
           WHEN CAST(TotalSteps AS INTEGER) < 7500  THEN '3 5k-7.5k'
           WHEN CAST(TotalSteps AS INTEGER) < 10000 THEN '4 7.5k-10k'
           ELSE '5 10k+'
       END                                                  AS step_band,
       COUNT(*)                                             AS user_days,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM daily_activity), 1) AS pct_days
FROM daily_activity
GROUP BY step_band
ORDER BY step_band;
