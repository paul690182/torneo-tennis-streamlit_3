
import os
import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

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

# --- Punteggi possibili ---
punteggi_possibili = [
    "6-0", "6-1", "6-2", "6-3", "6-4", "7-5", "7-6",
    "0-6", "1-6", "2-6", "3-6", "4-6", "5-7", "6-7"
]

# --- Funzione per calcolare i punti ---
def calcola_punti(set1, set2, set3):
    sets = [s for s in [set1, set2, set3] if s]
    g1_vinti = sum(int(s.split('-')[0]) > int(s.split('-')[1]) for s in sets)
    g2_vinti = sum(int(s.split('-')[1]) > int(s.split('-')[0]) for s in sets)

    if g1_vinti == 2 and g2_vinti == 0:
        return (3, 0, "Giocatore 1", "2-0")
    elif g2_vinti == 2 and g1_vinti == 0:
        return (0, 3, "Giocatore 2", "0-2")
    elif g1_vinti == 2 and g2_vinti == 1:
        return (3, 1, "Giocatore 1", "2-1")
    elif g2_vinti == 2 and g1_vinti == 1:
        return (1, 3, "Giocatore 2", "1-2")
    else:
        return (0, 0, None, "")

# --- UI Streamlit ---
st.title("🏆 Torneo Tennis - Inserisci Risultati e Classifica")

# --- Form inserimento partita ---
st.subheader("Inserisci risultato partita")
with st.form("inserisci_partita"):
    g1 = st.selectbox("Giocatore 1", giocatori, key="giocatore1")
    g2 = st.selectbox("Giocatore 2", giocatori, key="giocatore2")
    set1 = st.selectbox("Set 1", punteggi_possibili, key="set1")
    set2 = st.selectbox("Set 2", punteggi_possibili, key="set2")
    set3 = st.selectbox("Set 3 (opzionale)", [""] + punteggi_possibili, key="set3")
    submit = st.form_submit_button("Salva risultato")

if submit:
    if g1 == g2:
        st.error("❌ Giocatore 1 e Giocatore 2 non possono essere uguali!")
    else:
        punti_g1, punti_g2, vincitore, tipo_vittoria = calcola_punti(set1, set2, set3)
        data = {
            "giocatore1": g1,
            "giocatore2": g2,
            "set1": set1,
            "set2": set2,
            "set3": set3,
            "punti_g1": punti_g1,
            "punti_g2": punti_g2,
            "vincitore": vincitore,
            "tipo_vittoria": tipo_vittoria,
            "created_at": datetime.now().isoformat()
        }
        supabase.table("partite_completo").insert(data).execute()
        st.success(f"✅ Risultato salvato: {g1} vs {g2}")

# --- Storico partite ---
st.subheader("📜 Storico partite")
response = supabase.table("partite_completo").select("*").execute()
partite = response.data

if partite:
    df = pd.DataFrame(partite)

    # Gestione colonna created_at
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    else:
        df["created_at"] = datetime.now()

    df = df.sort_values(by="created_at", ascending=False)

    # Filtri
    giocatore_filtro = st.selectbox("Filtra per giocatore", ["Tutti"] + giocatori)
    tipo_filtro = st.selectbox("Filtra per tipo di vittoria", ["Tutti", "2-0", "2-1", "0-2", "1-2"])
    data_da = st.date_input("Da data", value=df["created_at"].min().date())
    data_a = st.date_input("A data", value=df["created_at"].max().date())

    # Applica filtri
    if giocatore_filtro != "Tutti":
        df = df[(df["giocatore1"] == giocatore_filtro) | (df["giocatore2"] == giocatore_filtro)]
    if tipo_filtro != "Tutti":
        df = df[df["tipo_vittoria"] == tipo_filtro]
    df = df[(df["created_at"].dt.date >= data_da) & (df["created_at"].dt.date <= data_a)]

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
