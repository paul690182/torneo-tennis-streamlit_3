
import os
import streamlit as st
import pandas as pd
from supabase_config import supabase  # usa env vars da Render/.env

# -------------------------------
# Config pagina e stile
# -------------------------------
st.set_page_config(page_title="Torneo Tennis", layout="wide")

# Nascondi sidebar
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

st.title("🏆 Torneo Tennis - Inserisci Risultato")

# -------------------------------
# Dati giocatori
# -------------------------------
giocatori_top = [
    "Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo",
    "Cris Cosso", "Giovanni", "Andrea P.", "Giuseppe", "Salvatore",
    "Leonardino", "Federico", "Luca", "Adriano"
]

giocatori_advanced = [
    "Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.",
    "Roberto A.", "Susanna", "Paolo Mattioli", "Paolo Rosi", "Michele",
    "Daniele M.", "Stefano D. R.", "Pino", "Gianni", "Leonardo", "Francesco M."
]

gironi = ["Top", "Advanced"]
scelta_girone = st.selectbox("Seleziona il girone", gironi)

if scelta_girone == "Top":
    giocatori = giocatori_top
    tabella = "risultati_top"
else:
    giocatori = giocatori_advanced
    tabella = "risultati_advanced"

# -------------------------------
# Input risultato
# -------------------------------
col1, col2 = st.columns(2)
with col1:
    giocatore1 = st.selectbox("Giocatore 1", giocatori, key="g1")
with col2:
    giocatore2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != giocatore1], key="g2")

punteggio1 = st.number_input("Punteggio Giocatore 1 (0–20)", min_value=0, max_value=20, step=1)
punteggio2 = st.number_input("Punteggio Giocatore 2 (0–20)", min_value=0, max_value=20, step=1)

set1 = st.text_input("Set 1 (es. 6-4)")
set2 = st.text_input("Set 2 (es. 3-6)")
set3 = st.text_input("Set 3 (es. 6-4)")

# -------------------------------
# Funzioni di supporto
# -------------------------------
def parse_set(s: str):
    if not s or "-" not in s:
        return None
    try:
        a, b = s.replace(" ", "").split("-", 1)
        a, b = int(a), int(b)
        if a == b:
            return None
        return 1 if a > b else 2
    except Exception:
        return None

def calcola_punti_e_stats(rows_df: pd.DataFrame) -> pd.DataFrame:
    # Sanifica i campi prima di usarli
    df = rows_df.copy()

    for col in ["punteggio1", "punteggio2"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        else:
            df[col] = 0

    for col in ["set1", "set2", "set3"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)
        else:
            df[col] = ""

    cls = {}
    def ensure(g):
        if g not in cls:
            cls[g] = {"Punti": 0, "Vittorie": 0, "Sconfitte": 0, "Partite giocate": 0}

    for _, r in df.iterrows():
        g1, g2 = r.get("giocatore1"), r.get("giocatore2")
        p1, p2 = r["punteggio1"], r["punteggio2"]
        s1, s2, s3 = r["set1"], r["set2"], r["set3"]

        if not g1 or not g2:
            continue

        ensure(g1); ensure(g2)
        cls[g1]["Partite giocate"] += 1
        cls[g2]["Partite giocate"] += 1

        wins1 = wins2 = 0
        for sv in (s1, s2, s3):
            w = parse_set(sv)
            if w == 1: wins1 += 1
            elif w == 2: wins2 += 1

        if wins1 == 2 and wins2 <= 1:
            cls[g1]["Vittorie"] += 1
            cls[g2]["Sconfitte"] += 1
            cls[g1]["Punti"] += 3
            if wins2 == 1: cls[g2]["Punti"] += 1
        elif wins2 == 2 and wins1 <= 1:
            cls[g2]["Vittorie"] += 1
            cls[g1]["Sconfitte"] += 1
            cls[g2]["Punti"] += 3
            if wins1 == 1: cls[g1]["Punti"] += 1
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

# -------------------------------
# Salvataggio risultato
# -------------------------------
if st.button("Salva Risultato"):
    if giocatore1 == giocatore2:
        st.error("❌ I due giocatori devono essere diversi.")
    else:
        try:
            payload = {
                "giocatore1": giocatore1,
                "giocatore2": giocatore2,
                "punteggio1": int(punteggio1),
                "punteggio2": int(punteggio2),
                "set1": set1.strip() or None,
                "set2": set2.strip() or None,
                "set3": set3.strip() or None,
            }
            supabase.table(tabella).insert(payload).execute()
            st.success(f"✅ Salvato: {giocatore1} vs {giocatore2} | Set: {set1 or '-'}, {set2 or '-'}, {set3 or '-'}")
        except Exception as e:
            st.error(f"❌ Errore durante l'inserimento: {e}")

# -------------------------------
# Storico + Classifica
# -------------------------------
st.subheader("📊 Storico Risultati")
try:
    res = supabase.table(tabella).select("*").order("created_at", desc=True).execute()
    df = pd.DataFrame(res.data or [])

    if not df.empty:
        # Sanifica subito per evitare NaN
        for col in ["punteggio1", "punteggio2"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        for col in ["set1", "set2", "set3"]:
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str)

        st.dataframe(df, use_container_width=True)
        st.subheader("🏅 Classifica")
        df_classifica = calcola_punti_e_stats(df)
        st.dataframe(df_classifica, use_container_width=True)
    else:
        st.info("Nessun risultato inserito ancora.")
except Exception as e:
    st.error(f"❌ Errore nel caricamento dati: {e}")

# -------------------------------
# Diagnostica (facoltativa)
# -------------------------------
with st.expander("🛠️ Diagnostica (env vars)", expanded=False):
    url_ok = bool(os.getenv("SUPABASE_URL"))
    key_ok = bool(os.getenv("SUPABASE_KEY"))
    st.write(f"SUPABASE_URL presente: {'✅' if url_ok else '❌'}")
    st.write(f"SUPABASE_KEY presente: {'✅' if key_ok else '❌'}")
    st.caption("Le chiavi non vengono mostrate per sicurezza.")

