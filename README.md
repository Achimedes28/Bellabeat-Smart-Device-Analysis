# Bellabeat Smart Device Usage Analysis

How do people use their fitness trackers, and what should Bellabeat's marketing team do about it?
This case study analyses Fitbit activity data from 35 users to find usage patterns and turns them into three marketing recommendations.

![Power BI dashboard](images/dashboard_powerbi_preview.png)

**Tools:** SQL (SQLite) · Power BI (DAX, Power Query) · Tableau Public · PowerPoint

## Key insights

Days with 0 steps (61 of 457, 13%) mean the tracker was not worn, so averages and segments below use worn days only.
Counting those days as real activity would make users look less active than they are (the share of sedentary users rises from 35% to 40%).

| | Finding | What it means for Bellabeat |
|---|---|---|
| 1 | **About a third of users are sedentary**: 12 of 34 average under 5,000 steps on the days they wear the tracker. Average is 7,555 steps a day, and 32% of worn days reach 10,000 steps. | The biggest segment is people who move little, not athletes. |
| 2 | **Tuesday is the least active day** (5,980 steps on average vs 7,150–8,204 on other days). | A natural slot for reminders and step challenges. |
| 3 | **The tracker is often not worn.** 13% of days show zero steps, from 14 of 35 users, and sleep data exists for only 23 of 35 users. | Comfort and wearability limit how much data users collect. |

Fitbit logs 15.7 sedentary hours per worn day with about 32 minutes of moderate-to-vigorous activity. Sedentary time also includes sleep that was not logged, so it is not pure sitting time.

## Recommendations

1. **Sell micro-habits, not workouts.** Position products such as the *Spring* bottle as simple daily-habit tools (hydration, short walks).
2. **Use the quiet days.** Send reminders and step challenges on Tuesdays, when activity is lowest.
3. **Lead with comfort.** Promote the *Leaf* as a light clip-on that can be worn all day and overnight.

## Dashboards

- **Power BI:** [`powerbi/Bellabeat.pbip`](powerbi/) — one-page overview with KPIs, user segments, weekday pattern, activity intensity and step bands. See the [Power BI guide](docs/powerbi-guide.md) to open it.
- **Tableau Public:** [interactive dashboard](https://public.tableau.com/views/Bellabeat_Smart_Device_Analysis_17875472877500/Dashboard2) with the hourly activity curve ([snapshot](images/dashboard_tableau.png)).

## Repository structure

```
├── data/            dailyActivity_merged.csv (Fitbit daily activity, 457 user-days)
├── sql/             SQLite queries for cleaning checks, segmentation and aggregates
├── powerbi/         Power BI Project (semantic model in TMDL, report in PBIR, theme)
├── scripts/         build_presentation.py (deck + charts), render_powerbi_preview.py
├── docs/            Power BI guide: data model, DAX measures, layout
├── images/          dashboard previews
└── presentation/    executive deck (PDF and PPTX)
```

## Data

[FitBit Fitness Tracker Data](https://www.kaggle.com/datasets/arashnic/fitbit) (Möbius, CC0), Fitabase export for 12 March – 12 April 2016.
This repository includes the daily activity table. The sleep figure in insight 3 comes from the sleep table of the same dataset, which is not included here. An earlier version also recommended timing ads around 12:00 and 17:00–19:00 from the hourly steps table; that table is not in this repository, so the recommendation was removed until it can be re-checked.

**Limitations:** small sample (35 users, about 13 days each on average within a one-month window), no demographic information, and the users are not necessarily Bellabeat's target customers. Findings are directional.

## Method

Follows the Google Data Analytics case-study flow: **Ask** (business task) → **Prepare** (source and credibility) → **Process** (type casting, duplicate and zero-step checks in SQL) → **Analyse** (segmentation, weekday and intensity patterns) → **Share** (Tableau, Power BI) → **Act** (recommendations and deck).
