
import os
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from postgrest.exceptions import APIError

# ==== Config & Connessione ====
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.stop()  # Blocca se mancano le variabili (su Render dovrebbero esserci già)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Mappa gironi -> tabelle
TABLE_MAP = {
    "Top": "partite_top",
    "Advanced": "partite_advanced",
}

# ==== Utilità ====
def parse_set(s: str):
    """Ritorna 1 se vince giocatore1, 2 se vince giocatore2, None se non valido."""
    try:
        s = (s or "").strip()
        if "-" not in s:
            return None
        a, b = s.split("-")
        a, b = int(a), int(b)
        if a > b:
            return 1
        elif b > a:
            return 2
        return None
    except Exception:
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
        g1, g2 = r.get("giocatore1", ""), r.get("giocatore2", "")
        p1, p2 = r.get("punteggio1", 0), r.get("punteggio2", 0)
        s1, s2, s3 = r.get("set1", ""), r.get("set2", ""), r.get("set3", "")
        if not g1 or not g2:
            continue

        ensure(g1); ensure(g2)
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
                cls[g1]["Punti"] += 3  # 2-0
            else:
                cls[g1]["Punti"] += 2  # 2-1
                cls[g2]["Punti"] += 1
        elif wins2 == 2 and wins1 <= 1:
            cls[g2]["Vittorie"] += 1
            cls[g1]["Sconfitte"] += 1
            if wins1 == 0:
                cls[g2]["Punti"] += 3  # 0-2
            else:
                cls[g2]["Punti"] += 2  # 1-2
                cls[g1]["Punti"] += 1
        else:
            # Fallback: punteggio globale
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

# ==== UI ====
st.title("🏆 Torneo Tennis - Classifica & Storico")

# Selettore Girone
girone = st.sidebar.selectbox("Girone", ["Top", "Advanced"])
TABLE_NAME = TABLE_MAP.get(girone, "partite_top")

@st.cache_data(ttl=60)
def carica_partite(table_name: str) -> pd.DataFrame:
    try:
        res = supabase.table(table_name).select("*").execute()
        data = res.data or []
        df = pd.DataFrame(data)
        # Fix: aggiunta colonne mancanti con lunghezza coerente
        for col in ["giocatore1", "giocatore2", "punteggio1", "punteggio2", "set1", "set2", "set3"]:
            if col not in df.columns:
                df[col] = pd.Series([None] * len(df))
        return df
    except APIError as e:
        st.error(f"Errore Supabase ({getattr(e, 'code', 'PGRST')}): {getattr(e, 'message', e)}")
        st.info("Controlla che la tabella esista e il nome sia corretto.")
        return pd.DataFrame(columns=["giocatore1", "giocatore2", "punteggio1", "punteggio2", "set1", "set2", "set3"])

matches_df = carica_partite(TABLE_NAME)

st.subheader(f"Inserisci risultato partita – Girone {girone}")
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
        new_row = {
            "giocatore1": g1, "giocatore2": g2,
            "punteggio1": int(p1), "punteggio2": int(p2),
            "set1": set1, "set2": set2, "set3": set3
        }
        try:
            supabase.table(TABLE_NAME).insert(new_row).execute()
            st.success("✅ Partita aggiunta!")
            st.cache_data.clear()   # invalida la cache
            st.rerun()              # ricarica la pagina per aggiornare classifica/storico
        except APIError as e:
            st.error(f"Errore inserimento Supabase ({getattr(e, 'code', 'PGRST')}): {getattr(e, 'message', e)}")

st.subheader(f"Classifica – Girone {girone}")
classifica = calcola_punti_e_stats(matches_df)
st.dataframe(classifica, use_container_width=True)

st.subheader(f"Storico Partite – Girone {girone}")
st.dataframe(matches_df, use_container_width=True)

# Download CSV
st.download_button("Scarica Storico", matches_df.to_csv(index=False), "storico_partite.csv")
st.download_button("Scarica Classifica", classifica.to_csv(), "classifica.csv")

