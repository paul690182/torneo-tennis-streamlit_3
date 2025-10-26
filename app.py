
import streamlit as st
import pandas as pd
from datetime import date

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

# Simulazione dati partite
partite = [
    {"giocatore1": "Paolo R.", "giocatore2": "Francesco M.", "set1": "6-4", "set2": "6-3", "set3": "", "data_partita": "2025-10-25"},
    {"giocatore1": "Davide P.", "giocatore2": "Sara T.", "set1": "6-0", "set2": "0-6", "set3": "6-3", "data_partita": "2025-10-26"}
]

# Calcolo punteggi e vincitori
for p in partite:
    pg1, pg2 = calcola_punteggi(p['set1'], p['set2'], p['set3'])
    p['punteggio_g1'] = pg1
    p['punteggio_g2'] = pg2
    p['vincitore'] = p['giocatore1'] if pg1 > pg2 else p['giocatore2']

# Costruzione DataFrame
df = pd.DataFrame(partite)

# Visualizzazione dello storico tramite menu a tendina
st.subheader("Storico Partite")
if df.empty:
    st.info("Nessuna partita registrata.")
else:
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

# Calcolo classifica
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
