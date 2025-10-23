
import streamlit as st
import sqlite3
import pandas as pd

st.title("Torneo Tennis - Classifica")

conn = sqlite3.connect("torneo.db")
df = pd.read_sql_query("SELECT * FROM risultati", conn)

# Funzione per calcolare i punti in base al punteggio
def calcola_punti(punteggio, vincitore, g1, g2):
    set_g1 = 0
    set_g2 = 0
    for set_score in punteggio.split(','):
        s1, s2 = map(int, set_score.strip().split('-'))
        if s1 > s2:
            set_g1 += 1
        else:
            set_g2 += 1
    if vincitore == g1:
        if set_g2 == 1:
            return 3, 1
        else:
            return 3, 0
    elif vincitore == g2:
        if set_g1 == 1:
            return 3, 1
        else:
            return 3, 0
    return 0, 0

# Calcola la classifica
classifica = {}
for _, row in df.iterrows():
    g1, g2, punteggio, vincitore = row['giocatore1'], row['giocatore2'], row['punteggio'], row['vincitore']
    punti_v, punti_p = calcola_punti(punteggio, vincitore, g1, g2)

    if vincitore not in classifica:
        classifica[vincitore] = {'Punti': 0}
    classifica[vincitore]['Punti'] += punti_v

    perdente = g2 if vincitore == g1 else g1
    if perdente not in classifica:
        classifica[perdente] = {'Punti': 0}
    classifica[perdente]['Punti'] += punti_p

# Visualizza la classifica
st.subheader("Classifica")
df_classifica = pd.DataFrame.from_dict(classifica, orient='index').reset_index()
df_classifica.columns = ['Giocatore', 'Punti']
st.dataframe(df_classifica)
