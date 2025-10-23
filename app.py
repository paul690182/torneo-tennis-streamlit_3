
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.title("Torneo Tennis - Tutti contro tutti")

# Connessione al database
conn = sqlite3.connect("torneo.db")
cursor = conn.cursor()

# Inserimento partita
st.header("Inserisci risultato partita")
giocatori = ["Giocatore A", "Giocatore B", "Giocatore C", "Giocatore D"]
g1 = st.selectbox("Giocatore 1", giocatori)
g2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != g1])
set1 = st.text_input("Set 1 (es. 6-4)")
set2 = st.text_input("Set 2 (es. 0-6)")
set3 = st.text_input("Set 3 (facoltativo, es. 7-5)")
data = st.date_input("Data partita", value=datetime.today())

# Funzione per calcolare vincitore e punteggio
def calcola_vincitore(s1, s2, s3):
    sets = [s1, s2]
    if s3:
        sets.append(s3)
    punteggio = [0, 0]
    for s in sets:
        try:
            g1_games, g2_games = map(int, s.split("-"))
            if g1_games > g2_games:
                punteggio[0] += 1
            elif g2_games > g1_games:
                punteggio[1] += 1
        except:
            pass
    if punteggio[0] > punteggio[1]:
        vincitore = g1
    else:
        vincitore = g2
    return vincitore, f"{punteggio[0]}-{punteggio[1]}"

if st.button("Salva risultato"):
    vincitore, punteggio = calcola_vincitore(set1, set2, set3)
    cursor.execute("""
        INSERT INTO risultati (giocatore1, giocatore2, set1, set2, set3, vincitore, punteggio, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (g1, g2, set1, set2, set3, vincitore, punteggio, str(data)))
    conn.commit()
    st.success("Risultato salvato correttamente!")

# Storico partite
st.header("Storico partite")
df = pd.read_sql_query("SELECT * FROM risultati", conn)
st.dataframe(df)

# Classifica
st.header("Classifica")
classifica = {}
for _, row in df.iterrows():
    g1 = row['giocatore1']
    g2 = row['giocatore2']
    vincitore = row['vincitore']
    p1, p2 = map(int, row['punteggio'].split("-"))

    for g in [g1, g2]:
        if g not in classifica:
            classifica[g] = 0

    if vincitore == g1:
        if p2 == 0:
            classifica[g1] += 3
            classifica[g2] += 0
        else:
            classifica[g1] += 3
            classifica[g2] += 1
    elif vincitore == g2:
        if p1 == 0:
            classifica[g2] += 3
            classifica[g1] += 0
        else:
            classifica[g2] += 3
            classifica[g1] += 1

classifica_df = pd.DataFrame(list(classifica.items()), columns=["Giocatore", "Punti"])
classifica_df = classifica_df.sort_values(by="Punti", ascending=False)
st.dataframe(classifica_df)

conn.close()
