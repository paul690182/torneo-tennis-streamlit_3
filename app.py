import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Configurazione Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🏆 Torneo Tennis - Gestione Risultati")

# --- Funzione per calcolare punti ---
def calcola_punti(set_g1, set_g2):
    if set_g1 == 2 and set_g2 == 0:
        return 3, 0
    elif set_g1 == 2 and set_g2 == 1:
        return 3, 1
    elif set_g2 == 2 and set_g1 == 0:
        return 0, 3
    elif set_g2 == 2 and set_g1 == 1:
        return 1, 3
    else:
        return 0, 0  # Caso non valido

# --- Form inserimento partita ---
st.subheader("Inserisci Nuova Partita")
with st.form("inserimento_partita"):
    giocatore1 = st.selectbox("Giocatore 1", ["Paolo R.", "Francesco M.", "Daniele T.", "Simone V.", "Leo S.", "Maurizio P.", "Andrea P."])
    giocatore2 = st.selectbox("Giocatore 2", ["Paolo R.", "Francesco M.", "Daniele T.", "Simone V.", "Leo S.", "Maurizio P.", "Andrea P."])
    set1 = st.text_input("Set 1 (es. 7-5)")
    set2 = st.text_input("Set 2 (es. 1-6)")
    set3 = st.text_input("Set 3 (opzionale, es. 6-4)")
    submit = st.form_submit_button("Salva Risultato")

if submit:
    # Conta set vinti
    set_g1 = 0
    set_g2 = 0
    for s in [set1, set2, set3]:
        if s:
            g1_score, g2_score = map(int, s.split("-"))
            if g1_score > g2_score:
                set_g1 += 1
            else:
                set_g2 += 1

    punti_g1, punti_g2 = calcola_punti(set_g1, set_g2)

    # Salva su Supabase
    supabase.table("risultati").insert({
        "giocatore1": giocatore1,
        "giocatore2": giocatore2,
        "set1": set1,
        "set2": set2,
        "set3": set3,
        "punti_g1": punti_g1,
        "punti_g2": punti_g2,
        "created_at": datetime.now().isoformat()
    }).execute()

    st.success("✅ Partita salvata con successo!")

# --- Recupera dati dal DB ---
res = supabase.table("risultati").select("*").order("created_at", desc=True).execute()
data = res.data
df = pd.DataFrame(data)

# --- Mostra storico ---
st.subheader("Storico Partite")
st.dataframe(df)

# --- Calcola classifica ---
punteggi = pd.concat([
    df[['giocatore1', 'punti_g1']].rename(columns={'giocatore1': 'giocatore', 'punti_g1': 'punti'}),
    df[['giocatore2', 'punti_g2']].rename(columns={'giocatore2': 'giocatore', 'punti_g2': 'punti'})
])
classifica = punteggi.groupby('giocatore').sum().sort_values(by='punti', ascending=False).reset_index()

st.subheader("Classifica Torneo")
st.dataframe(classifica)
