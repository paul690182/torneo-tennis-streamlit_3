import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# --- FILE ---
CSV = "app_updated_partite.csv"
PDF_FILE = "SUPER_FULL_ADOBE_REV02_AGGIORNATO.pdf"

# --- LETTURA CSV ---
df = pd.read_csv(CSV, sep=None, engine="python")

# --- NORMALIZZA COLONNE ---
df.columns = df.columns.str.strip().str.lower()

# --- DEBUG MINIMO (solo per capire) ---
print("COLONNE REALI:", df.columns.tolist())
# --- USA SEMPRE LE PRIME DUE COLONNE DEL CSV ---
col1 = df.columns[0]
col2 = df.columns[1]



# --- TROVA EVENTUALE WINNER ---
winner_col = None

styles = getSampleStyleSheet()

# --- LISTA GIOCATORI ---
# --- PLAYERS (FIX DEFINITIVO) ---
# PRENDE LE PRIME DUE COLONNE DEL CSV (SOLUZIONE DEFINITIVA)


players = list(df[col1].dropna().astype(str)) + list(df[col2].dropna().astype(str))
players = list(set([p.strip() for p in players if p.strip() != ""]))
# --- STATS ---
stats = []

for p in players:
    giocate = len(df[(df[col1] == p) | (df[col2] == p)])
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
