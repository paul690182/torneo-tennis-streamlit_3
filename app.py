
import streamlit as st
import sqlite3
import pandas as pd

st.title("Torneo Tennis - Tutti contro tutti")

conn = sqlite3.connect("torneo.db")
cursor = conn.cursor()

# Inserimento risultato
st.header("Inserisci Risultato")
giocatore1 = st.text_input("Giocatore 1")
giocatore2 = st.text_input("Giocatore 2")
punteggio = st.text_input("Punteggio (es. 6-4, 7-5)")
vincitore = st.text_input("Vincitore")

if st.button("Salva Risultato"):
    cursor.execute("INSERT INTO risultati (giocatore1, giocatore2, punteggio, vincitore) VALUES (?, ?, ?, ?)",
                   (giocatore1, giocatore2, punteggio, vincitore))
    conn.commit()
    st.success("Risultato salvato correttamente!")

# Visualizza classifica
st.header("Classifica")
df = pd.read_sql_query("SELECT vincitore, COUNT(*) as vittorie FROM risultati GROUP BY vincitore ORDER BY vittorie DESC", conn)
st.dataframe(df)

conn.close()
