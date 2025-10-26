
import streamlit as st
import pandas as pd
from datetime import date
import os

st.title("Torneo Tennis - Inserimento Partite e Classifica")

# Funzione per calcolare i punteggi dai set

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

# Simulazione dati Supabase
# In produzione, sostituire con chiamata a supabase.table(...)
df = pd.DataFrame(columns=[
    "giocatore1", "giocatore2", "set1", "set2", "set3",
    "punteggio_g1", "punteggio_g2", "vincitore", "data_partita"
])

# Selezione giocatori
giocatori = ["Paolo R.", "Francesco M.", "Davide P.", "Sara T.", "Elisa N.", "Maura B."]

# Form inserimento partita
with st.form("inserimento_partita"):
    st.subheader("Inserisci una nuova partita")
    g1 = st.selectbox("Giocatore 1", giocatori)
    g2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != g1])
    set1 = st.text_input("Set 1 (es. 6-4)")
    set2 = st.text_input("Set 2 (es. 4-6)")
    set3 = st.text_input("Set 3 (opzionale)")
    data_partita = st.date_input("Data della partita", value=date.today())
    salva = st.form_submit_button("Salva Partita")

    if salva:
        pg1, pg2 = calcola_punteggi(set1, set2, set3)
        if pg1 == pg2:
            st.error("I punteggi non possono essere uguali. Deve esserci un vincitore.")
        else:
            vincitore = g1 if pg1 > pg2 else g2
            nuova_partita = {
                "giocatore1": g1,
                "giocatore2": g2,
                "set1": set1,
                "set2": set2,
                "set3": set3 if set3 else None,
                "punteggio_g1": pg1,
                "punteggio_g2": pg2,
                "vincitore": vincitore,
                "data_partita": str(data_partita)
            }
            df = pd.concat([df, pd.DataFrame([nuova_partita])], ignore_index=True)
            st.success("Partita inserita correttamente!")

# Visualizzazione partite tramite menu a tendina
st.subheader("Visualizza Partita")
if not df.empty:
    partite = df.apply(lambda row: f"{row['giocatore1']} vs {row['giocatore2']} ({row['data_partita']})", axis=1)
    selezione = st.selectbox("Seleziona una partita", partite)
    partita = df.iloc[partite[partite == selezione].index[0]]
    st.markdown(f"**{partita['giocatore1']} vs {partita['giocatore2']}**")
    punteggi = [partita['set1'], partita['set2'], partita['set3']]
    punteggi = [s for s in punteggi if s]
    st.write("Set giocati:", ", ".join(punteggi))
    st.write(f"Punteggio: {partita['punteggio_g1']} - {partita['punteggio_g2']}")
    st.write(f"Vincitore: {partita['vincitore']}")
    st.write(f"Data: {partita['data_partita']}")

# Calcolo classifica
st.subheader("Classifica")
if not df.empty:
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
