
import os
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Connessione a Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "partite_torneo"

# Funzione per interpretare il set (es. "6-4") e determinare il vincitore
def parse_set(s):
    try:
        if "-" not in s:
            return None
        a, b = s.split("-")
        a, b = int(a), int(b)
        if a > b:
            return 1
        elif b > a:
            return 2
        else:
            return None
    except:
        return None

# Logica punteggi aggiornata:
# 2–0 → 3 punti vincitore, 0 sconfitto
# 2–1 → 2 punti vincitore, 1 sconfitto
# Fallback: punteggio globale → 3 punti vincitore
def calcola_punti_e_stats(rows_df: pd.DataFrame) -> pd.DataFrame:
    df = rows_df.copy()
    df["punteggio1"] = pd.to_numeric(df.get("punteggio1", 0), errors="coerce").fillna(0).astype(int)
    df["punteggio2"] = pd.to_numeric(df.get("punteggio2", 0), errors="coerce").fillna(0).astype(int)
    for col in ["set1", "set2", "set3"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)

    cls = {}

    def ensure(g):
        if g not in cls:
            cls[g] = {"Punti": 0, "Vittorie": 0, "Sconfitte": 0, "Partite giocate": 0}

    for _, r in df.iterrows():
        g1, g2 = r["giocatore1"], r["giocatore2"]
        p1, p2 = r["punteggio1"], r["punteggio2"]
        s1, s2, s3 = r.get("set1", ""), r.get("set2", ""), r.get("set3", "")
        ensure(g1)
        ensure(g2)
        cls[g1]["Partite giocate"] += 1
        cls[g2]["Partite giocate"] += 1

        wins1 = wins2 = 0
        for sv in (s1, s2, s3):
            w = parse_set(sv)
            if w == 1:
                wins1 += 1
            elif w == 2:
                wins2 += 1

        if wins1 == 2 and wins2 <= 1:
            cls[g1]["Vittorie"] += 1
            cls[g2]["Sconfitte"] += 1
            if wins2 == 0:
                cls[g1]["Punti"] += 3
            else:
                cls[g1]["Punti"] += 2
                cls[g2]["Punti"] += 1
        elif wins2 == 2 and wins1 <= 1:
            cls[g2]["Vittorie"] += 1
            cls[g1]["Sconfitte"] += 1
            if wins1 == 0:
                cls[g2]["Punti"] += 3
            else:
                cls[g2]["Punti"] += 2
                cls[g1]["Punti"] += 1
        else:
            if p1 > p2:
                cls[g1]["Vittorie"] += 1
                cls[g2]["Sconfitte"] += 1
                cls[g1]["Punti"] += 3
            elif p2 > p1:
                cls[g2]["Vittorie"] += 1
                cls[g1]["Sconfitte"] += 1
                cls[g2]["Punti"] += 3

    dfc = pd.DataFrame.from_dict(cls, orient="index")
    if not dfc.empty:
        dfc = dfc.sort_values(by=["Punti", "Vittorie"], ascending=[False, False])
    return dfc

# --- Streamlit App ---
st.title("🏆 Torneo Tennis - Gestione Classifica")

# Caricamento dati da Supabase
@st.cache_data(ttl=60)
def carica_partite():
    res = supabase.table(TABLE_NAME).select("*").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["giocatore1", "giocatore2", "punteggio1", "punteggio2", "set1", "set2", "set3"])

matches_df = carica_partite()

st.subheader("Inserisci risultato partita")
with st.form("nuova_partita"):
    g1 = st.text_input("Giocatore 1")
    g2 = st.text_input("Giocatore 2")
    p1 = st.number_input("Punteggio Giocatore 1", min_value=0, step=1)
    p2 = st.number_input("Punteggio Giocatore 2", min_value=0, step=1)
    set1 = st.text_input("Set 1 (es. 6-4)")
    set2 = st.text_input("Set 2 (es. 6-4)")
    set3 = st.text_input("Set 3 (opzionale)")
    submitted = st.form_submit_button("Aggiungi Partita")
    if submitted and g1 and g2:
        new_row = {"giocatore1": g1, "giocatore2": g2, "punteggio1": p1, "punteggio2": p2, "set1": set1, "set2": set2, "set3": set3}
        supabase.table(TABLE_NAME).insert(new_row).execute()
        st.success("✅ Partita aggiunta! Aggiorna la pagina per vedere la classifica aggiornata.")

st.subheader("Classifica")
classifica = calcola_punti_e_stats(matches_df)
st.dataframe(classifica)

st.subheader("Storico Partite")
st.dataframe(matches_df)

# Download CSV
st.download_button("Scarica Storico", matches_df.to_csv(index=False), "storico_partite.csv")
st.download_button("Scarica Classifica", classifica.to_csv(), "classifica.csv")

