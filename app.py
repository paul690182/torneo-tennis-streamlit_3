import os
import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- Configurazione porta per Render ---
port = int(os.environ.get("PORT", 8501))

# --- Connessione a Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Variabili d'ambiente mancanti: SUPABASE_URL o SUPABASE_KEY")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Lista giocatori ---
giocatori = [
    "Paolo R.", "Paola C.", "Francesco M.", "Massimo B.", "Daniele T.",
    "Simone V.", "Gianni F.", "Leo S.", "Maura F.", "Giovanni D.",
    "Andrea P.", "Maurizio P."
]

# --- Funzione per calcolare i punti ---
def calcola_punti(set1, set2, set3):
    g1_vinti = sum([int(s.split('-')[0]) > int(s.split('-')[1]) for s in [set1, set2, set3] if s])
    g2_vinti = sum([int(s.split('-')[1]) > int(s.split('-')[0]) for s in [set1, set2, set3] if s])

    if g1_vinti == 2 and g2_vinti == 0:
        return (3, 0)
    elif g2_vinti == 2 and g1_vinti == 0:
        return (0, 3)
    elif g1_vinti == 2 and g2_vinti == 1:
        return (3, 1)
    elif g2_vinti == 2 and g1_vinti == 1:
        return (1, 3)
    else:
        return (0, 0)

# --- UI Streamlit ---
st.title("🏆 Torneo Tennis - Inserisci Risultati e Classifica")

# --- Form inserimento partita ---
st.subheader("Inserisci risultato partita")
with st.form("inserisci_partita"):
    g1 = st.selectbox("Giocatore 1", giocatori, key="giocatore1")
    g2 = st.selectbox("Giocatore 2", giocatori, key="giocatore2")  # NON filtrato
    set1 = st.text_input("Set 1 (es. 6-4)", key="set1")
    set2 = st.text_input("Set 2 (es. 3-6)", key="set2")
    set3 = st.text_input("Set 3 (opzionale, es. 6-4)", key="set3")
    submit = st.form_submit_button("Salva risultato")

if submit:
    if g1 == g2:
        st.error("❌ Giocatore 1 e Giocatore 2 non possono essere uguali!")
    else:
        punti_g1, punti_g2 = calcola_punti(set1, set2, set3)
        data = {
            "giocatore1": g1,
            "giocatore2": g2,
            "set1": set1,
            "set2": set2,
            "set3": set3,
            "punti_g1": punti_g1,
            "punti_g2": punti_g2
        }
        supabase.table("partite_completo").insert(data).execute()
        st.success(f"✅ Risultato salvato: {g1} vs {g2}")

# --- Storico partite ---
st.subheader("📜 Storico partite")
response = supabase.table("partite_completo").select("*").execute()
partite = response.data
if partite:
    df = pd.DataFrame(partite)
    st.dataframe(df)
else:
    st.info("Nessuna partita registrata.")

# --- Classifica ---
st.subheader("🏅 Classifica")
if partite:
    classifica = {}
    for p in partite:
        punti_g1 = p.get("punti_g1") or 0
        punti_g2 = p.get("punti_g2") or 0
        classifica[p["giocatore1"]] = classifica.get(p["giocatore1"], 0) + punti_g1
        classifica[p["giocatore2"]] = classifica.get(p["giocatore2"], 0) + punti_g2

    df_classifica = pd.DataFrame(list(classifica.items()), columns=["Giocatore", "Punti"])
    df_classifica = df_classifica.sort_values(by="Punti", ascending=False)
    st.table(df_classifica)
