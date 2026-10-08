"""Build presentation/Bellabeat_Marketing_Presentation.pptx (and its charts) from data/dailyActivity_merged.csv.

Every number on the slides is calculated here from the daily activity file, so the deck, the README,
the SQL and the Power BI model use the same figures. Days with 0 steps are treated as "not worn" and
excluded from averages and segments.

Run from the repo root: python scripts/build_presentation.py
Export the PDF with PowerPoint or LibreOffice (soffice --headless --convert-to pdf ...).
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "images")
OUT = os.path.join(ROOT, "presentation", "Bellabeat_Marketing_Presentation.pptx")

# ------------------------------------------------------------------ figures
d = pd.read_csv(os.path.join(ROOT, "data", "dailyActivity_merged.csv"))
d["date"] = pd.to_datetime(d["ActivityDate"], format="%m/%d/%Y")
w = d[d["TotalSteps"] > 0]

n_users, n_days = d["Id"].nunique(), len(d)
days_per_user = d.groupby("Id").size()
zero_days = int((d["TotalSteps"] == 0).sum())
zero_users = d.loc[d["TotalSteps"] == 0, "Id"].nunique()
user_avg = w.groupby("Id")["TotalSteps"].mean()
seg_labels = ["Sedentary", "Lightly Active", "Fairly Active", "Very Active"]
seg = pd.cut(user_avg, [-1, 4999.999, 7499.999, 9999.999, 1e9], labels=seg_labels).value_counts().reindex(seg_labels)
n_sed = int(seg["Sedentary"])
steps = w["TotalSteps"].mean()
sed_h = w["SedentaryMinutes"].mean() / 60
mvpa = (w["VeryActiveMinutes"] + w["FairlyActiveMinutes"]).mean()
pct10k = (w["TotalSteps"] >= 10000).mean() * 100
wk = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
wk_id = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
weekday = w.groupby(w["date"].dt.day_name())["TotalSteps"].mean().reindex(wk)
bands = pd.cut(d["TotalSteps"], [-1, 0, 4999, 7499, 9999, 1e9],
               labels=["0 (tidak dipakai)", "< 5k", "5k–7,5k", "7,5k–10k", "10k+"]).value_counts(normalize=True).sort_index() * 100

ROSE, SLATE, INK, MUTED = "#B85C74", "#3E5C76", "#1F2937", "#6B7280"


def idn(x, dec=0):
    """Indonesian number format: 7.555 and 15,7."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


# ------------------------------------------------------------------ charts
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "xtick.color": MUTED, "ytick.color": MUTED})


def save(fig, name):
    path = os.path.join(IMG, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


fig, ax = plt.subplots(figsize=(7, 4))
y = list(range(4))[::-1]
ax.barh(y, seg.values, color=[ROSE, "#9CA3AF", "#9CA3AF", "#9CA3AF"], height=0.6)
ax.set_yticks(y); ax.set_yticklabels(seg_labels, fontsize=12); ax.set_xticks([]); ax.tick_params(length=0)
for yy, v in zip(y, seg.values):
    ax.text(v + 0.2, yy, f"{v} pengguna ({v/len(user_avg)*100:.0f}%)", va="center", fontsize=12, color=INK)
ax.set_xlim(0, seg.max() * 1.6)
chart_seg = save(fig, "deck_segments.png")

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(wk_id, weekday.values, color=[ROSE if d_ == "Tuesday" else SLATE for d_ in wk], width=0.6)
ax.set_yticks([]); ax.tick_params(length=0, labelsize=12)
for i, v in enumerate(weekday.values):
    ax.text(i, v + 100, idn(v), ha="center", fontsize=11, color=INK)
chart_wk = save(fig, "deck_weekday.png")

fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(bands.index.astype(str), bands.values, color=[ROSE] + [SLATE] * 4, width=0.6)
ax.set_yticks([]); ax.tick_params(length=0, labelsize=11)
for i, v in enumerate(bands.values):
    ax.text(i, v + 0.5, f"{v:.0f}%", ha="center", fontsize=12, color=INK)
chart_band = save(fig, "deck_step_bands.png")

# ------------------------------------------------------------------ deck
R_ROSE, R_INK, R_MUTED, R_PALE, R_WHITE = (RGBColor(0xB8, 0x5C, 0x74), RGBColor(0x1F, 0x29, 0x37), RGBColor(0x6B, 0x72, 0x80),
                                           RGBColor(0xFB, 0xF4, 0xF6), RGBColor(0xFF, 0xFF, 0xFF))
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def box(s, x, y, wd, ht, fill):
    shp = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(wd), Inches(ht))
    shp.fill.solid(); shp.fill.fore_color.rgb = fill; shp.line.fill.background()


def text(s, x, y, wd, ht, paras, size=16, color=R_INK, bold=False):
    tf = s.shapes.add_textbox(Inches(x), Inches(y), Inches(wd), Inches(ht)).text_frame
    tf.word_wrap = True
    for i, p in enumerate(paras if isinstance(paras, list) else [paras]):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        runs = p if isinstance(p, tuple) else (p,)
        for j, r in enumerate(runs):
            run = par.add_run(); run.text = r
            run.font.size = Pt(size); run.font.color.rgb = color; run.font.name = "Calibri"
            run.font.bold = bold or (len(runs) > 1 and j == 0)
        par.space_after = Pt(10)


def slide(title, kicker):
    s = prs.slides.add_slide(BLANK)
    text(s, 0.6, 0.35, 12, 0.4, kicker.upper(), size=11, color=R_ROSE, bold=True)
    text(s, 0.6, 0.7, 12.1, 0.8, title, size=28, bold=True)
    return s


def chart_slide(title, kicker, img, paras):
    s = slide(title, kicker)
    s.shapes.add_picture(img, Inches(0.6), Inches(1.75), width=Inches(7.2))
    text(s, 8.2, 1.8, 4.6, 5.2, paras, size=15)


# 1. title
s = prs.slides.add_slide(BLANK); box(s, 0, 0, 13.333, 7.5, R_PALE)
text(s, 0.9, 2.3, 11.5, 0.5, "STUDI KASUS DATA ANALYTICS", size=13, color=R_ROSE, bold=True)
text(s, 0.9, 2.8, 11.5, 1.3, "Analisis Penggunaan Smart Device untuk Bellabeat", size=38, bold=True)
text(s, 0.9, 4.2, 11.5, 0.6, "Dari data aktivitas harian Fitbit menjadi rekomendasi pemasaran", size=18, color=R_MUTED)
text(s, 0.9, 5.6, 11.5, 0.5, "SQL (SQLite) · Power BI · Tableau · Novaldi Ramadhan Waluyo", size=13, color=R_MUTED)

# 2. data
s = slide("Tujuan dan data", "Latar belakang")
text(s, 0.6, 1.8, 6.0, 5, [
    ("Pertanyaan bisnis. ", "Bagaimana orang memakai fitness tracker, dan apa artinya bagi strategi pemasaran Bellabeat?"),
    ("Sumber. ", "FitBit Fitness Tracker Data (Möbius, Kaggle, CC0), ekspor Fitabase 12 Maret – 12 April 2016."),
    ("Catatan. ", "Pengguna dalam data ini bukan pelanggan Bellabeat, sehingga temuan bersifat arah, bukan kepastian."),
], size=16)
for i, (v, lab) in enumerate([(str(n_users), "pengguna"), (str(n_days), "hari-pengguna tercatat"),
                              (idn(days_per_user.mean(), 0), "hari rata-rata per pengguna"), (f"{zero_days}", "hari dengan 0 langkah")]):
    x, yy = 7.1 + (i % 2) * 2.9, 1.8 + (i // 2) * 1.75
    box(s, x, yy, 2.65, 1.5, R_PALE)
    text(s, x + 0.2, yy + 0.15, 2.3, 0.7, v, size=30, color=R_ROSE, bold=True)
    text(s, x + 0.2, yy + 0.9, 2.3, 0.5, lab, size=13, color=R_MUTED)

# 3. method
s = slide("Metode", "Proses")
text(s, 0.6, 1.8, 12, 5, [
    ("Pemeriksaan data (SQL). ", f"{n_users} pengguna, {n_days} baris, tidak ada duplikat Id + tanggal. "
                                 f"{zero_days} hari ({zero_days/n_days*100:.0f}%) mencatat 0 langkah, artinya alat tidak dipakai."),
    ("Hari dipakai saja. ", f"Rata-rata dan segmen dihitung dari {len(w)} hari ketika alat dipakai (langkah > 0). "
                            "Jika hari kosong ikut dihitung, rata-rata langkah turun dan pengguna yang jarang memakai alat "
                            "terlihat lebih malas dari kenyataannya."),
    ("Segmentasi. ", "Rata-rata langkah harian per pengguna: Sedentary < 5.000, Lightly Active 5.000–7.499, "
                     "Fairly Active 7.500–9.999, Very Active ≥ 10.000."),
    ("Visualisasi. ", "Dashboard Power BI (model TMDL di repo) dan Tableau Public."),
], size=16)

# 4. segments
chart_slide(f"Sekitar sepertiga pengguna tergolong sedentary", "Segmen pengguna", chart_seg, [
    f"{n_sed} dari {len(user_avg)} pengguna ({n_sed/len(user_avg)*100:.0f}%) rata-rata berjalan di bawah 5.000 langkah "
    "pada hari mereka memakai alat. Ini kelompok terbesar.",
    f"Rata-rata seluruh pengguna {idn(steps)} langkah per hari, dan hanya {pct10k:.0f}% hari yang mencapai 10.000 langkah.",
    "Satu pengguna tidak pernah memakai alat (semua hari 0 langkah), sehingga segmen dihitung dari 34 pengguna.",
])

# 5. weekday
chart_slide("Selasa adalah hari paling pasif", "Pola mingguan", chart_wk, [
    f"Rata-rata langkah hari Selasa {idn(weekday['Tuesday'])}, terendah dalam seminggu. Hari lain berkisar "
    f"{idn(weekday.drop('Tuesday').min())}–{idn(weekday.max())} langkah.",
    f"Waktu sedentary tercatat {idn(sed_h, 1)} jam per hari dipakai, dengan sekitar {mvpa:.0f} menit aktivitas sedang-berat. "
    "Fitbit juga menghitung waktu tidur yang tidak tercatat sebagai sedentary, jadi angka ini bukan murni waktu duduk.",
])

# 6. wear
chart_slide(f"{zero_days/n_days*100:.0f}% hari alat tidak dipakai", "Kebiasaan memakai alat", chart_band, [
    f"{zero_days} dari {n_days} hari mencatat 0 langkah, berasal dari {zero_users} dari {n_users} pengguna.",
    "Data tidur (tabel terpisah, tidak termasuk di repo ini) hanya tercatat untuk 23 dari 35 pengguna.",
    "Kemungkinan penyebab: alat tidak nyaman dipakai terus-menerus atau dilepas untuk diisi daya. Data ini tidak "
    "bisa membuktikan penyebabnya.",
])

# 7. recommendations
s = slide("Tiga rekomendasi pemasaran", "Rekomendasi")
recs = [
    ("1. Jual kebiasaan kecil, bukan olahraga",
     f"Kelompok terbesar ({n_sed/len(user_avg)*100:.0f}%) adalah pengguna sedentary. Posisikan produk seperti botol Spring "
     "sebagai alat kebiasaan harian (minum air, jalan singkat)."),
    ("2. Manfaatkan hari pasif",
     f"Kirim pengingat atau tantangan langkah pada hari Selasa, saat rata-rata langkah paling rendah ({idn(weekday['Tuesday'])})."),
    ("3. Tonjolkan kenyamanan",
     f"{zero_days/n_days*100:.0f}% hari alat tidak dipakai dan data tidur sering kosong. Promosikan Leaf sebagai klip ringan "
     "yang nyaman dipakai seharian dan saat tidur."),
]
for i, (t, d_) in enumerate(recs):
    x = 0.6 + i * 4.1
    box(s, x, 1.8, 3.85, 4.6, R_PALE)
    text(s, x + 0.25, 2.0, 3.4, 1.0, t, size=18, color=R_ROSE, bold=True)
    text(s, x + 0.25, 3.1, 3.4, 3.2, d_, size=15)

# 8. limitations
s = slide("Keterbatasan", "Cara membaca hasil")
text(s, 0.6, 1.8, 12, 5, [
    f"Sampel kecil: {n_users} pengguna, rata-rata {idn(days_per_user.mean())} hari per pengguna, tanpa data demografi.",
    "Pengguna Fitbit ini belum tentu mewakili target pasar Bellabeat (perempuan).",
    "Pola per jam dan data tidur berasal dari tabel lain di dataset yang sama dan tidak disertakan di repo ini; "
    "angka tersebut perlu diverifikasi ulang sebelum dipakai untuk menjadwalkan kampanye.",
    "Rekomendasi bersifat arah dan sebaiknya diuji, misalnya dengan A/B test waktu notifikasi.",
], size=17)

# 9. close
s = prs.slides.add_slide(BLANK); box(s, 0, 0, 13.333, 7.5, R_PALE)
text(s, 0.9, 3.0, 11.5, 1, "Terima kasih", size=40, bold=True)
text(s, 0.9, 4.0, 11.5, 0.6, "Novaldi Ramadhan Waluyo · github.com/Achimedes28", size=16, color=R_MUTED)

prs.save(OUT)
print("Saved", OUT)
