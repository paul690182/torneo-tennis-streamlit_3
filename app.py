
import streamlit as st
import pandas as pd
from datetime import date
import os
from supabase import create_client, Client

# Configura Supabase tramite variabili d'ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Torneo Tennis - Inserimento Partite e Classifica")

def calcola_punteggi(set1, set2, set3):
    punteggi_g1 = 0
    punteggi_g2 = 0
    for s in [set1, set2, set3]:
        if s and '-' in s:
            try:
                g1, g2 = map(int, s.split('-'))
                if g1 > g2:
                    punteggi_g1 += 1
                elif g2 > g1:
                    punteggi_g2 += 1
            except:
                continue
    return punteggi_g1, punteggi_g2

giocatori = ["Paolo R.", "Paola C.", "Francesco M.", "Massimo B.", "Daniele T.", "Simone V.",
             "Gianni F.", "Leo S.", "Maura F.", "Giovanni D.", "Andrea P.", "Maurizio P."]

st.subheader("Inserisci una nuova partita")
with st.form("inserimento_partita"):
    giocatore1 = st.selectbox("Giocatore 1", giocatori)
    giocatore2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != giocatore1])
    set1 = st.text_input("Set 1 (es. 6-3)")
    set2 = st.text_input("Set 2 (es. 3-6)")
    set3 = st.text_input("Set 3 (opzionale, es. 6-4)")
    data_partita = st.date_input("Data della partita", value=date.today())
    submit = st.form_submit_button("Salva partita")

    if submit:
        pg1, pg2 = calcola_punteggi(set1, set2, set3)
        vincitore = giocatore1 if pg1 > pg2 else giocatore2
        nuova_partita = {
            "giocatore1": giocatore1,
            "giocatore2": giocatore2,
            "set1": set1,
            "set2": set2,
            "set3": set3,
            "data_partita": str(data_partita),
            "punteggio_g1": pg1,
            "punteggio_g2": pg2,
            "vincitore": vincitore
        }
        supabase.table("partite_classifica").insert(nuova_partita).execute()
        st.success("Partita inserita con successo!")

# Rilettura dei dati da Supabase
response = supabase.table("partite_classifica").select("*").execute()
partite = response.data if response.data else []

if partite:
    df = pd.DataFrame(partite)

    st.subheader("Storico Partite")
    partite_label = df.apply(lambda row: f"{row['giocatore1']} vs {row['giocatore2']} ({row['data_partita']})", axis=1)
    selezione = st.selectbox("Seleziona una partita", partite_label)
    partita = df.iloc[partite_label[partite_label == selezione].index[0]]
    st.markdown(f"**{partita['giocatore1']} vs {partita['giocatore2']}**")
    punteggi = [partita['set1'], partita['set2'], partita['set3']]
    punteggi = [s for s in punteggi if s]
    st.write("Set giocati:", ", ".join(punteggi))
    st.write(f"Punteggio: {partita['punteggio_g1']} - {partita['punteggio_g2']}")
    st.write(f"Vincitore: {partita['vincitore']}")
    st.write(f"Data: {partita['data_partita']}")

    st.subheader("Classifica")
    punti = {}
    for _, row in df.iterrows():
        g1 = row['giocatore1']
        g2 = row['giocatore2']
        pg1 = row['punteggio_g1']
        pg2 = row['punteggio_g2']

        punti[g1] = punti.get(g1, 0)
        punti[g2] = punti.get(g2, 0)

        if pg1 == 2 and pg2 == 0:
            punti[g1] += 3
        elif pg1 == 0 and pg2 == 2:
            punti[g2] += 3
        elif pg1 == 2 and pg2 == 1:
            punti[g1] += 3
            punti[g2] += 1
        elif pg1 == 1 and pg2 == 2:
            punti[g2] += 3
            punti[g1] += 1

    classifica_df = pd.DataFrame(list(punti.items()), columns=["Giocatore", "Punti"])
    st.table(classifica_df.sort_values(by="Punti", ascending=False))
else:
    st.info("Nessuna partita registrata.")
