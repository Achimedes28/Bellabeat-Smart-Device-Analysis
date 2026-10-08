"""Render images/dashboard_powerbi_preview.png from data/dailyActivity_merged.csv.

The .pbip report is the real deliverable; this static image lets the README show the page
without Power BI Desktop. It uses the same rules as the semantic model: averages and segments
use worn days only (days with 0 steps mean the tracker was not worn).

Run from the repo root: python scripts/render_powerbi_preview.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = pd.read_csv(os.path.join(ROOT, "data", "dailyActivity_merged.csv"))
d["date"] = pd.to_datetime(d["ActivityDate"], format="%m/%d/%Y")
w = d[d["TotalSteps"] > 0]

INK, MUTED, GRID, ROSE, SLATE = "#1F2937", "#6B7280", "#E5E7EB", "#B85C74", "#3E5C76"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": GRID})

user_avg = w.groupby("Id")["TotalSteps"].mean()
seg = pd.cut(user_avg, [-1, 4999.999, 7499.999, 9999.999, 1e9],
             labels=["Sedentary", "Lightly Active", "Fairly Active", "Very Active"]).value_counts(normalize=True).sort_index() * 100
wk_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday = w.groupby(w["date"].dt.day_name())["TotalSteps"].mean().reindex(wk_order)
intensity = w[["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes", "SedentaryMinutes"]].mean()
bands = pd.cut(d["TotalSteps"], [-1, 0, 4999, 7499, 9999, 1e9],
               labels=["0 (not worn)", "< 5k", "5k–7.5k", "7.5k–10k", "10k+"]).value_counts(normalize=True).sort_index() * 100

fig = plt.figure(figsize=(25.6, 14.4), dpi=100, facecolor="#F7F7F7")


def card(x, y, wd, ht):
    fig.patches.append(FancyBboxPatch((x, y), wd, ht, boxstyle="round,pad=0,rounding_size=0.006",
                                      transform=fig.transFigure, fc="white", ec=GRID, lw=1.2, zorder=-5))


def panel(x, y, wd, ht, title):
    card(x, y, wd, ht)
    fig.text(x + 0.012, y + ht - 0.04, title, fontsize=13, weight="bold", color=INK)


fig.text(0.019, 0.945, "Bellabeat  ·  Smart Device Usage", fontsize=26, weight="bold", color=INK)
fig.text(0.019, 0.91, "Fitbit daily activity of 35 users, 12 Mar – 12 Apr 2016. Averages and segments use worn days only "
         "(days with 0 steps excluded).", fontsize=12.5, color=MUTED)
card(0.81, 0.885, 0.171, 0.088)
fig.text(0.82, 0.945, "Segment", fontsize=11, color=MUTED)
fig.text(0.82, 0.905, "All", fontsize=15, color=INK)

kpis = [("Total users", f"{d['Id'].nunique()}"), ("Avg daily steps", f"{w['TotalSteps'].mean():,.0f}"),
        ("Sedentary hours / day", f"{w['SedentaryMinutes'].mean()/60:.1f}"),
        ("Very + fairly active min / day", f"{(w['VeryActiveMinutes'] + w['FairlyActiveMinutes']).mean():.0f}"),
        ("Worn days reaching 10k steps", f"{(w['TotalSteps'] >= 10000).mean()*100:.1f}%")]
for i, (lab, v) in enumerate(kpis):
    x = 0.019 + i * 0.1955
    card(x, 0.735, 0.183, 0.132)
    fig.text(x + 0.012, 0.825, lab, fontsize=13, weight="bold", color=INK)
    fig.text(x + 0.012, 0.76, v, fontsize=36, weight="bold", color=INK)

panel(0.019, 0.37, 0.312, 0.345, "Users by activity segment (worn days)")
ax = fig.add_axes([0.1, 0.4, 0.2, 0.24]); y = list(range(len(seg)))[::-1]
ax.barh(y, seg.values, color=ROSE, height=0.6); ax.set_yticks(y); ax.set_yticklabels(seg.index, fontsize=11)
ax.set_xticks([]); ax.tick_params(length=0)
for yy, v in zip(y, seg.values):
    ax.text(v + 0.8, yy, f"{v:.0f}%", va="center", fontsize=11, color=INK)

panel(0.344, 0.37, 0.312, 0.345, "Average daily steps by weekday")
ax = fig.add_axes([0.36, 0.4, 0.28, 0.24])
ax.bar([s[:3] for s in weekday.index], weekday.values, color=SLATE, width=0.6)
ax.set_yticks([]); ax.tick_params(length=0, labelsize=11)
for i, v in enumerate(weekday.values):
    ax.text(i, v + 100, f"{v/1000:.1f}K", ha="center", fontsize=11, color=INK)

panel(0.669, 0.37, 0.312, 0.345, "Average minutes per day by intensity")
ax = fig.add_axes([0.75, 0.4, 0.2, 0.24]); labels = ["Very Active", "Fairly Active", "Lightly Active", "Sedentary"]
y = list(range(4))[::-1]
ax.barh(y, intensity.values, color=SLATE, height=0.45); ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=11)
ax.set_xticks([]); ax.tick_params(length=0)
for yy, v in zip(y, intensity.values):
    ax.text(v + 10, yy, f"{v:.0f}", va="center", fontsize=11, color=INK)

panel(0.019, 0.025, 0.637, 0.33, "Share of tracked days by daily step band")
ax = fig.add_axes([0.04, 0.06, 0.6, 0.22])
ax.bar(bands.index.astype(str), bands.values, color=SLATE, width=0.6)
ax.set_yticks([]); ax.tick_params(length=0, labelsize=11)
for i, v in enumerate(bands.values):
    ax.text(i, v + 0.5, f"{v:.0f}%", ha="center", fontsize=11, color=INK)

panel(0.669, 0.025, 0.312, 0.33, "Key insights")
n_sed = int((user_avg < 5000).sum())
tue = weekday["Tuesday"]
insights = [
    (f"About a third of users are sedentary ({n_sed} of {len(user_avg)}).", "Position Bellabeat as a micro-habit coach, not workout gear."),
    (f"{w['SedentaryMinutes'].mean()/60:.1f} sedentary hours per worn day.",
     f"Includes unlogged sleep; about {(w['VeryActiveMinutes'] + w['FairlyActiveMinutes']).mean():.0f} minutes of moderate-to-vigorous activity."),
    (f"{(d['TotalSteps'] == 0).mean()*100:.0f}% of days show zero steps.", "The device is often not worn; lead with comfort (Leaf)."),
    (f"Tuesday is the low point ({tue/1000:.1f}k steps).", "Use it for reminders and step challenges."),
]
for i, (h, t) in enumerate(insights):
    yy = 0.27 - i * 0.058
    fig.text(0.681, yy, h, fontsize=11.5, weight="bold", color=INK)
    fig.text(0.681, yy - 0.022, t, fontsize=10.5, color=MUTED)

out = os.path.join(ROOT, "images", "dashboard_powerbi_preview.png")
fig.savefig(out, facecolor=fig.get_facecolor())
print("Saved", out)
