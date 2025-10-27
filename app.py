import streamlit as st
from datetime import date
import uuid
from supabase import create_client, Client

# Inserisci qui le tue credenziali Supabase
SUPABASE_URL = "https://<TUO_PROJECT_ID>.supabase.co"
SUPABASE_KEY = "<TUO_ANON_KEY>"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🎾 Torneo Tennis - Inserimento Risultati")

@st.cache_data
def carica_giocatori():
    response = supabase.table("partite").select("giocatore1", "giocatore2").execute()
    rows = response.data
    g1_list = [r["giocatore1"] for r in rows if r["giocatore1"]]
    g2_list = [r["giocatore2"] for r in rows if r["giocatore2"]]
    return sorted(set(g1_list + g2_list))

giocatori = carica_giocatori()

if giocatori:
    g1 = st.selectbox("Giocatore 1", giocatori)
    g2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != g1])
else:
    g1 = st.text_input("Inserisci nome Giocatore 1")
    g2 = st.text_input("Inserisci nome Giocatore 2")

set1 = st.text_input("Set 1 (es. 6-4)")
set2 = st.text_input("Set 2 (es. 3-6)")
set3 = st.text_input("Set 3 (opzionale)", "")

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

def partita_duplicata(g1, g2):
    response = supabase.table("partite").select("giocatore1", "giocatore2").execute()
    rows = response.data
    for r in rows:
        if (r["giocatore1"] == g1 and r["giocatore2"] == g2) or (r["giocatore1"] == g2 and r["giocatore2"] == g1):
            return True
    return False

if st.button("💾 Salva partita"):
    if g1 == g2:
        st.error("❌ I due giocatori devono essere diversi.")
    elif not g1 or not g2:
        st.error("❌ Inserisci entrambi i nomi dei giocatori.")
    elif partita_duplicata(g1, g2):
        st.warning("⚠️ Partita già inserita tra questi due giocatori.")
    else:
        p1, p2 = calcola_punteggi(set1, set2, set3)
        vincitore = g1 if p1 > p2 else g2
        nuova_riga = {
            "id": str(uuid.uuid4()),
            "giocatore1": g1,
            "giocatore2": g2,
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
