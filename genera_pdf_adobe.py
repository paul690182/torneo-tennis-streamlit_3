import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# --- FILE ---
CSV = "app_updated_partite.csv"
PDF_FILE = "SUPER_FULL_ADOBE_REV02_AGGIORNATO.pdf"

# --- LETTURA CSV ---
df = pd.read_csv(CSV, sep=";")

# --- NORMALIZZA COLONNE ---
df.columns = df.columns.str.strip().str.lower()

# --- DEBUG MINIMO (solo per capire) ---
print("COLONNE REALI:", df.columns.tolist())

# --- MAPPATURA AUTOMATICA ---
cols = list(df.columns)
# --- TROVA AUTOMATICO LE COLONNE GIOCATORI ---
player1_col = "player1"
player2_col = "player2"

# --- TROVA EVENTUALE WINNER ---
winner_candidates = [c for c in cols if "win" in c.lower()]
winner_col = winner_candidates[0] if winner_candidates else None

styles = getSampleStyleSheet()

# --- LISTA GIOCATORI ---
# --- PLAYERS (FIX DEFINITIVO) ---
players = list(df[player1_col].dropna().astype(str)) + list(df[player2_col].dropna().astype(str))
players = list(set([p.strip() for p in players if p.strip() != ""]))

# --- STATS ---
stats = []

for p in players:
    giocate = len(df[(df[player1_col] == p) | (df[player2_col] == p)])

    if winner_col and winner_col in df.columns:
        vinte = len(df[df[winner_col] == p])
    else:
        vinte = 0

    stats.append([p, giocate, vinte])

# --- CLASSIFICA ---
df_classifica = pd.DataFrame(stats, columns=["Giocatore", "Giocate", "Vinte"])
df_classifica = df_classifica.sort_values(by="Giocate", ascending=False)


# --- PDF ---
doc = SimpleDocTemplate(PDF_FILE, pagesize=A4)
elements = []

# Titolo
elements.append(Paragraph("TORNEO TENNIS – V13 MASTER", styles["Title"]))
elements.append(Spacer(1, 20))

# Classifica
elements.append(Paragraph("Classifica Generale", styles["Heading2"]))

table_data = [df_classifica.columns.tolist()] + df_classifica.values.tolist()

table = Table(table_data)
table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey)
]))

elements.append(table)
elements.append(Spacer(1,20))

# Storico (prime 30 righe)
elements.append(Paragraph("Storico Partite", styles["Heading2"]))

storico = df[[player1_col, player2_col]].values.tolist()
storico = [["P1", "P2"]] + storico[:30]

table2 = Table(storico)
table2.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("GRID", (0,0), (-1,-1), 0.25, colors.grey)
]))

elements.append(table2)

# Build
doc.build(elements)

print("✅ PDF GENERATO:", PDF_FILE)
