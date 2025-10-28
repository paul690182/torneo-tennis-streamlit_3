
import streamlit as st
import pandas as pd
import os
import uuid
from datetime import date
from supabase import create_client

# --- Configurazione Supabase ---
SUPABASE_URL = os.getenv https://urrkxfohjpsdxlzicsye.supabase.co
SUPABASE_KEY = os.getenv eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVycmt4Zm9oanBzZHhsemljc3llIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMjY4OTcsImV4cCI6MjA3NjkwMjg5N30.7kn4pX-sunIYkeP35lzK57nCvI4HoSqwjGu8j0ZOvRk
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🏆 Torneo Tennis - Inserimento Risultati & Classifica")

# --- Lista fissa dei 12 giocatori ---
giocatori = [
    "Federico", "Giuseppe", "Marco", "Luca", "Alessandro", "Davide",
    "Simone", "Francesco", "Matteo", "Andrea", "Stefano", "Paolo"
]

# --- Form inserimento partita ---
st.subheader("Inserisci nuova partita")

giocatore1 = st.selectbox("Giocatore 1", giocatori)
giocatore2 = st.selectbox("Giocatore 2", giocatori)
set1 = st.text_input("Set 1 (es. 6-4)")
set2 = st.text_input("Set 2 (es. 3-6)")
set3 = st.text_input("Set 3 (opzionale)", "")

# --- Calcolo punteggi ---
def calcola_punteggi(s1, s2, s3):
    g1_vinti = g2_vinti = 0
    for s in [s1, s2, s3]:
        if "-" in s:
            try:
                a, b = map(int, s.strip().split("-"))
                if a > b:
                    g1_vinti += 1
                elif b > a:
                    g2_vinti += 1
            except:
                pass
    return g1_vinti, g2_vinti

# --- Controllo duplicati ---
def partita_duplicata(g1, g2):
    response = supabase.table("partite").select("giocatore1", "giocatore2").execute()
    rows = response.data
    for r in rows:
        if (r["giocatore1"] == g1 and r["giocatore2"] == g2) or (r["giocatore1"] == g2 and r["giocatore2"] == g1):
            return True
    return False

# --- Salvataggio partita ---
if st.button("💾 Salva partita"):
    if giocatore1 == giocatore2:
        st.error("❌ I due giocatori devono essere diversi.")
    elif partita_duplicata(giocatore1, giocatore2):
        st.warning("⚠️ Partita già inserita tra questi due giocatori.")
    else:
        p1, p2 = calcola_punteggi(set1, set2, set3)
        vincitore = giocatore1 if p1 > p2 else giocatore2
        nuova_riga = {
            "id": str(uuid.uuid4()),
            "giocatore1": giocatore1,
            "giocatore2": giocatore2,
            "set1": set1,
            "set2": set2,
            "set3": set3,
            "punteggio_g1": p1,
            "punteggio_g2": p2,
            "vincitore": vincitore,
            "data_partita": str(date.today())
        }
        supabase.table("partite").insert(nuova_riga).execute()
        st.success(f"✅ Partita salvata! Vincitore: {vincitore}")

# --- Classifica aggregata ---
st.subheader("Classifica aggiornata")
response = supabase.table("partite").select("giocatore1", "giocatore2", "punteggio_g1", "punteggio_g2").execute()
if response.data:
    df = pd.DataFrame(response.data)
    punti = {}
    for _, row in df.iterrows():
        punti[row["giocatore1"]] = punti.get(row["giocatore1"], 0) + row["punteggio_g1"]
        punti[row["giocatore2"]] = punti.get(row["giocatore2"], 0) + row["punteggio_g2"]
    classifica = pd.DataFrame(list(punti.items()), columns=["Giocatore", "Punti"]).sort_values(by="Punti", ascending=False)
    st.dataframe(classifica)
else:
    st.info("Nessuna partita registrata ancora.")
