import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from supabase import create_client
import os

# --- FILE ---
CSV = "app_updated_partite.csv"
PDF_FILE = "SUPER_FULL_ADOBE_REV02_AGGIORNATO.pdf"

# --- LETTURA DATI DA SUPABASE ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

response = supabase.table("matches").select("*").execute()
df = pd.DataFrame(response.data)

# --- NORMALIZZA COLONNE ---
df.columns = df.columns.str.strip().str.lower()


# --- DEBUG MINIMO (solo per capire) ---
print("COLONNE REALI:", df.columns.tolist())
# --- USA SEMPRE LE PRIME DUE COLONNE DEL CSV ---
col1 = "player1"
col2 = "player2"




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

    giocate = len(df[(df["player1"] == p) | (df["player2"] == p)])

    vinte = len(df[df["winner"] == p])

    sconfitte = giocate - vinte

    punti = (
        df.loc[df["player1"] == p, "points_p1"].sum() +
        df.loc[df["player2"] == p, "points_p2"].sum()
    )

    gf = (
        df.loc[df["player1"] == p, ["set1_p1","set2_p1","set3_p1"]].fillna(0).sum().sum()
        +
        df.loc[df["player2"] == p, ["set1_p2","set2_p2","set3_p2"]].fillna(0).sum().sum()
    )

    gs = (
        df.loc[df["player1"] == p, ["set1_p2","set2_p2","set3_p2"]].fillna(0).sum().sum()
        +
        df.loc[df["player2"] == p, ["set1_p1","set2_p1","set3_p1"]].fillna(0).sum().sum()
    )

    dg = gf - gs

    sv = 0
    sp = 0

    for _, row in df.iterrows():

        if row["player1"] == p:
            if pd.notna(row["set1_p1"]) and pd.notna(row["set1_p2"]):
                if row["set1_p1"] > row["set1_p2"]:
                    sv += 1
                elif row["set1_p2"] > row["set1_p1"]:
                    sp += 1

            if pd.notna(row["set2_p1"]) and pd.notna(row["set2_p2"]):
                if row["set2_p1"] > row["set2_p2"]:
                    sv += 1
                elif row["set2_p2"] > row["set2_p1"]:
                    sp += 1

            if pd.notna(row["set3_p1"]) and pd.notna(row["set3_p2"]):
                if row["set3_p1"] > row["set3_p2"]:
                    sv += 1
                elif row["set3_p2"] > row["set3_p1"]:
                    sp += 1

        if row["player2"] == p:
            if pd.notna(row["set1_p2"]) and pd.notna(row["set1_p1"]):
                if row["set1_p2"] > row["set1_p1"]:
                    sv += 1
                elif row["set1_p1"] > row["set1_p2"]:
                    sp += 1

            if pd.notna(row["set2_p2"]) and pd.notna(row["set2_p1"]):
                if row["set2_p2"] > row["set2_p1"]:
                    sv += 1
                elif row["set2_p1"] > row["set2_p2"]:
                    sp += 1

            if pd.notna(row["set3_p2"]) and pd.notna(row["set3_p1"]):
                if row["set3_p2"] > row["set3_p1"]:
                    sv += 1
                elif row["set3_p1"] > row["set3_p2"]:
                    sp += 1

    stats.append([p, giocate, vinte, sconfitte, punti, gf, gs, dg, sv, sp])

   


# --- CLASSIFICA ---
df_classifica = pd.DataFrame(
    stats,
   columns=[
    "Giocatore", "Giocate", "Vinte", "Sconfitte",
    "Punti", "GF", "GS", "DG", "SV", "SP"
]

)

df_classifica = df_classifica.sort_values(
    by=["Punti", "DG", "Vinte"],
    ascending=[False, False, False]
)
# MVP (primo classificato)
mvp = df_classifica.iloc[0]["Giocatore"]
# badge podio
df_classifica = df_classifica.reset_index(drop=True)

df_classifica.loc[0, "Giocatore"] = "🥇 " + df_classifica.loc[0, "Giocatore"]
df_classifica.loc[1, "Giocatore"] = "🥈 " + df_classifica.loc[1, "Giocatore"]
df_classifica.loc[2, "Giocatore"] = "🥉 " + df_classifica.loc[2, "Giocatore"]
# --- PDF ---
doc = SimpleDocTemplate(PDF_FILE, pagesize=A4)
elements = []

# Titolo
elements.append(Paragraph("TORNEO TENNIS – V13 MASTER", styles["Title"]))
elements.append(Spacer(1, 20))

# Classifica
elements.append(Paragraph("Classifica Generale", styles["Heading2"]))

elements.append(Paragraph(f"🏆 MVP TORNEO: {mvp}", styles["Heading2"]))
elements.append(Spacer(1, 10))

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

storico = df[[col1, col2]].values.tolist()
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
