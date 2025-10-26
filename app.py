
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date
from superbase import SUPABASE_URL, SUPABASE_KEY

# Connessione a Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Torneo Tennis - Inserimento Partite e Classifica")

# Recupera i dati esistenti
data_response = supabase.table("partite_classifica").select("*").execute()
df = pd.DataFrame(data_response.data)

# Selezione giocatori
giocatori = pd.unique(df[['giocatore1', 'giocatore2']].values.ravel('K'))

with st.form("inserimento_partita"):
    st.subheader("Inserisci una nuova partita")
    g1 = st.selectbox("Giocatore 1", giocatori)
    g2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != g1])
    set1 = st.text_input("Set 1 (es. 6-4)")
    set2 = st.text_input("Set 2 (es. 4-6)")
    set3 = st.text_input("Set 3 (opzionale)")
    punteggio_g1 = st.number_input("Punteggio Giocatore 1", min_value=0, max_value=3, step=1)
    punteggio_g2 = st.number_input("Punteggio Giocatore 2", min_value=0, max_value=3, step=1)
    vincitore = st.selectbox("Vincitore", [g1, g2])
    data_partita = st.date_input("Data della partita", value=date.today())
    submitted = st.form_submit_button("Inserisci Partita")

    if submitted:
        supabase.table("partite_classifica").insert({
            "giocatore1": g1,
            "giocatore2": g2,
            "set1": set1,
            "set2": set2,
            "set3": set3 if set3 else None,
            "punteggio_g1": punteggio_g1,
            "punteggio_g2": punteggio_g2,
            "vincitore": vincitore,
            "data_partita": str(data_partita)
        }).execute()
        st.success("Partita inserita correttamente!")

# Visualizza lo storico partite
st.subheader("Storico Partite")
if df.empty:
    st.info("Nessuna partita registrata.")
else:
    for _, row in df.iterrows():
        st.markdown(f"**{row['giocatore1']} vs {row['giocatore2']}**")
        punteggi = [row['set1'], row['set2'], row['set3']]
        punteggi = [s for s in punteggi if s]
        st.write("Set giocati:", ", ".join(punteggi))
        st.write(f"Punteggio: {row['punteggio_g1']} - {row['punteggio_g2']}")
        st.write(f"Vincitore: {row['vincitore']}")
        st.write(f"Data: {row['data_partita']}")
        st.markdown("---")

# Calcola classifica
st.subheader("Classifica")
if not df.empty:
    classifica = df['vincitore'].value_counts().reset_index()
    classifica.columns = ['Giocatore', 'Partite Vinte']
    st.table(classifica.sort_values(by='Partite Vinte', ascending=False))
