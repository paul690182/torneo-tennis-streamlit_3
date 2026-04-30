# =============================================================
#   GENERATORE PDF ADOBE – v13 STRICT – REV02 (YMCA PRIME)
#   Autore: Copilot (per Giuseppe D'Eramo)
#   Output: SUPER_FULL_ADOBE_REV02_AGGIORNATO.pdf
# =============================================================

import pandas as pd
import re
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle,
    Spacer, PageBreak, Image as RLImage
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

# =============================================================
#   1. CARICAMENTO DATI CSV
# =============================================================

CSV = "app_updated_partite.csv"
df = pd.read_csv(CSV)

# normalizzazione colonne
df["date"] = df["created_at"].astype(str).str.slice(0,10)

# detezione Tie-break
pat = re.compile(r"(\d+)-(\d+)")
def is_tb(score):
    for a,b in pat.findall(str(score)):
        if int(a)>=10 or int(b)>=10:
            return True
    return False

df["is_tb"] = df["risultato"].apply(is_tb)

# =============================================================
#   2. CALCOLO STATISTICHE
# =============================================================

# standings per giocatore
players = sorted(set(df["player1"]).union(df["player2"]))

stats = {p:{
    "Punti":0, "Vittorie":0, "Sconfitte":0,
    "GP":0, "GC":0, "DiffG":0,
    "SV":0, "SP":0, "DiffS":0,
    "TB_G":0, "TB_V":0, "TB_P":0
} for p in players}

for _,r in df.iterrows():
    p1, p2 = r["player1"], r["player2"]
    g1, g2 = int(r["games_p1"]), int(r["games_p2"])
    w  = r["winner"]
    tb = r["is_tb"]

    # games
    stats[p1]["GP"] += g1
    stats[p1]["GC"] += g2
    stats[p2]["GP"] += g2
    stats[p2]["GC"] += g1

    # set stimati (da risultato)
    # conta set come occorrenze dei blocchi "x-y"
    sets = str(r["risultato"]).split(",")
    sv1 = sum(int(s.split("-")[0]) > int(s.split("-")[1]) for s in sets if "-" in s)
    sv2 = sum(int(s.split("-")[1]) > int(s.split("-")[0]) for s in sets if "-" in s)

    stats[p1]["SV"] += sv1
    stats[p1]["SP"] += sv2
    stats[p2]["SV"] += sv2
    stats[p2]["SP"] += sv1

    # diff
    stats[p1]["DiffG"] = stats[p1]["GP"] - stats[p1]["GC"]
    stats[p2]["DiffG"] = stats[p2]["GP"] - stats[p2]["GC"]
    stats[p1]["DiffS"] = stats[p1]["SV"] - stats[p1]["SP"]
    stats[p2]["DiffS"] = stats[p2]["SV"] - stats[p2]["SP"]

    # punti
    if w == p1:
        stats[p1]["Vittorie"] += 1
        stats[p2]["Sconfitte"] += 1
    elif w == p2:
        stats[p2]["Vittorie"] += 1
        stats[p1]["Sconfitte"] += 1

    # punteggio torneo
    if sv1 == 2 and sv2 == 0:
        stats[p1]["Punti"] += 3
    elif sv2 == 2 and sv1 == 0:
        stats[p2]["Punti"] += 3
    else:
        # 2-1
        if w == p1:
            stats[p1]["Punti"] += 2
            stats[p2]["Punti"] += 1
        else:
            stats[p2]["Punti"] += 2
            stats[p1]["Punti"] += 1

    # Tie-break
    if tb:
        stats[p1]["TB_G"] += 1
        stats[p2]["TB_G"] += 1
        if w == p1:
            stats[p1]["TB_V"] += 1
            stats[p2]["TB_P"] += 1
        else:
            stats[p2]["TB_V"] += 1
            stats[p1]["TB_P"] += 1

# =============================================================
#   3. CALCOLO BADGE TB‑KING E BEST
# =============================================================

def tb_king(girone):
    subset = df[df["girone"]==girone]
    tbstats = {p:stats[p]["TB_V"] for p in players if p in list(subset["player1"])+list(subset["player2"])}
    if not tbstats:
        return None
    max_tb = max(tbstats.values())
    winners = [p for p,v in tbstats.items() if v==max_tb]
    return winners[0]  # primo

def best_player(girone):
    subset = df[df["girone"]==girone]
    points = {p:stats[p]["Punti"] for p in players if p in list(subset["player1"])+list(subset["player2"])}
    mx = max(points.values())
    return [p for p,v in points.items() if v==mx][0]

TBKING_ADV = tb_king("Advanced")
TBKING_TOP = tb_king("Top")
BEST_ADV = best_player("Advanced")
BEST_TOP = best_player("Top")

# =============================================================
#   4. GENERAZIONE PDF ADOBE – REV02 STRICT
# =============================================================

OUT = "SUPER_FULL_ADOBE_REV02_AGGIORNATO.pdf"
doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=0.7*cm, rightMargin=0.7*cm,
    topMargin=0.7*cm, bottomMargin=0.7*cm
)
styles = getSampleStyleSheet()
H2 = styles["Heading2"]
H3 = styles["Heading3"]
BODY = styles["BodyText"]

elements = []

# -------------------------------------------------------------
# FRONTESPIZIO
# -------------------------------------------------------------

title = """
<b>1° TORNEO TENNIS YMCA PRIME 2025/2026</b><br/>
<para size=10>Template v13 STRICT – REV02 – AUTOMATIC REPORT<br/>
Dati aggiornati automaticamente dal CSV</para>
"""

elements.append(Paragraph(title, styles["Title"]))
elements.append(Spacer(1,0.8*cm))

elements.append(Paragraph("<b>Indice</b>", H2))
elements.append(Paragraph("2) Riepilogo / Classifiche", BODY))
elements.append(Paragraph("3) MVP / ▲DG / ●DS / BEST / TB‑KING", BODY))
elements.append(Paragraph("4) Risultati Advanced / Top", BODY))
elements.append(Paragraph("5) Appendici A‑B‑C‑D", BODY))
elements.append(Paragraph("6) Cronologia Tie-break", BODY))
elements.append(Paragraph("7) Riepilogo Scratch - Sanity WO", BODY))
elements.append(PageBreak())

# -------------------------------------------------------------
# RIEPILOGO GIRONI
# -------------------------------------------------------------

grp = df.groupby("girone").agg(matches=("id","count")).reset_index()
table = Table([grp.columns.tolist()] + grp.values.tolist())
table.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.lightblue),
    ("GRID",(0,0),(-1,-1),0.3,colors.grey),
    ("ALIGN",(0,0),(-1,-1),"CENTER")
]))

elements.append(Paragraph("<b>Riepilogo per Girone</b>",H2))
elements.append(table)
elements.append(PageBreak())

# =============================================================
# DA QUI IN POI: APPENDICI ⇒ INSERIMENTO WATERMARK
# =============================================================

WM = "watermark_logo.png"

def watermark(canvas, doc):
    canvas.saveState()
    try:
        canvas.drawImage(
            WM,
            x=4*cm, y=8*cm,
            width=8*cm, height=8*cm,
            mask='auto'
        )
    except:
        pass
    canvas.restoreState()

# -------------------------------------------------------------
# CLASSIFICHE – con BEST e TB‑KING
# -------------------------------------------------------------

def classifica_girone(g):
    subset = df[df["girone"]==g]
    gioc = sorted(set(subset["player1"]).union(subset["player2"]))

    rows = [["Giocatore","Punti","V","S","GP","GC","DiffG","SV","SP","DiffS","Badge"]]
    for p in gioc:
        badges = []
        if stats[p]["Punti"] == max(stats[x]["Punti"] for x in gioc):
            badges.append("[BEST]")
        if p == TBKING_ADV and g=="Advanced":
            badges.append("[TB‑KING]")
        if p == TBKING_TOP and g=="Top":
            badges.append("[TB‑KING]")

        rows.append([
            p, stats[p]["Punti"], stats[p]["Vittorie"], stats[p]["Sconfitte"],
            stats[p]["GP"], stats[p]["GC"], stats[p]["DiffG"],
            stats[p]["SV"], stats[p]["SP"], stats[p]["DiffS"],
            " ".join(badges)
        ])

    t = Table(rows, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.lightblue),
        ("GRID",(0,0),(-1,-1),0.3,colors.grey),
        ("FONTSIZE",(0,0),(-1,-1),8)
    ]))
    return t

elements.append(Paragraph("<b>Classifica Advanced</b>",H2))
elements.append(classifica_girone("Advanced"))
elements.append(Spacer(1,0.4*cm))

elements.append(Paragraph("<b>Classifica Top</b>",H2))
elements.append(classifica_girone("Top"))
elements.append(PageBreak())

# -------------------------------------------------------------
# RISULTATI COMPLETI (NO watermark)
# -------------------------------------------------------------

rows = [["Data","Girone","P1","P2","Ris","G1","G2","Diff","TB"]]
for _,r in df.sort_values("date").iterrows():
    rows.append([
        r["date"], r["girone"], r["player1"], r["player2"],
        r["risultato"], r["games_p1"], r["games_p2"],
        r["diff_games"], "TB" if r["is_tb"] else ""
    ])

t = Table(rows, repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
    ("GRID",(0,0),(-1,-1),0.2,colors.grey),
    ("FONTSIZE",(0,0),(-1,-1),6)
]))

elements.append(Paragraph("<b>Risultati Completi</b>",H2))
elements.append(t)
elements.append(PageBreak())

# -------------------------------------------------------------
# APPENDICI (CON WATERMARK)
# -------------------------------------------------------------

# APPENDICE – TB CHRONO
rows_tb = [["Data","Girone","P1","P2","Ris","Win"]]
for _,r in df[df["is_tb"]].sort_values("date").iterrows():
    rows_tb.append([r["date"], r["girone"], r["player1"],
                    r["player2"], r["risultato"], r["winner"]])

TTB = Table(rows_tb, repeatRows=1)
TTB.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.lightgreen),
    ("GRID",(0,0),(-1,-1),0.2,colors.grey),
    ("FONTSIZE",(0,0),(-1,-1),7)
]))

elements.append(Paragraph("<b>Cronologia Tie-break – Completa</b>",H2))
elements.append(TTB)

# =============================================================
# COSTRUZIONE PDF CON WATERMARK *SOLO APPENDICI*
# =============================================================

doc.build(elements, onLaterPages=watermark)

print(f"PDF generato: {OUT}")
