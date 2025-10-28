import streamlit as st
from supabase import create_client, Client
import os
import pandas as pd

# --- Connessione a Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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

# --- Interfaccia Streamlit ---
st.title("Torneo Tennis - Inserimento Partita e Classifica")

with st.form("inserimento_partita"):
    giocatore1 = st.text_input("Giocatore 1")
    giocatore2 = st.text_input("Giocatore 2")
    set1 = st.text_input("Set 1 (es. 6-4)")
    set2 = st.text_input("Set 2 (es. 3-6)")
    set3 = st.text_input("Set 3 (opzionale, es. 6-3)", value="")
    submitted = st.form_submit_button("Inserisci Partita")

    if submitted:
        punti_g1, punti_g2 = calcola_punti(set1, set2, set3)
        data = {
            "giocatore1": giocatore1,
            "giocatore2": giocatore2,
            "set1": set1,
            "set2": set2,
            "set3": set3,
            "punti_g1": punti_g1,
            "punti_g2": punti_g2
        }
        supabase.table("partite_completo").insert(data).execute()
        st.success("Partita inserita correttamente!")

# --- Calcolo classifica ---
partite = supabase.table("partite_completo").select("*").execute().data

classifica = {}
for p in partite:
    g1 = p['giocatore1']
    g2 = p['giocatore2']
    classifica[g1] = classifica.get(g1, 0) + p['punti_g1']
    classifica[g2] = classifica.get(g2, 0) + p['punti_g2']

# --- Mostra classifica ---
st.subheader("Classifica aggiornata")
df_classifica = pd.DataFrame(list(classifica.items()), columns=["Giocatore", "Punti"])
df_classifica = df_classifica.sort_values(by="Punti", ascending=False)
st.table(df_classifica)
