
import streamlit as st
import sqlite3
import pandas as pd

st.title("Torneo Tennis - Tutti contro tutti")

conn = sqlite3.connect("torneo.db")
c = conn.cursor()

# Inserimento punteggi
st.header("Inserisci Risultato")
giocatore1 = st.text_input("Giocatore 1")
giocatore2 = st.text_input("Giocatore 2")
punteggio = st.text_input("Punteggio (es. 6-4, 7-5)")

if st.button("Salva Risultato"):
    c.execute("INSERT INTO risultati (giocatore1, giocatore2, punteggio) VALUES (?, ?, ?)",
              (giocatore1, giocatore2, punteggio))
    conn.commit()
    st.success("Risultato salvato!")

# Visualizza classifica
st.header("Classifica")
df = pd.read_sql_query("SELECT * FROM risultati", conn)
st.dataframe(df)

conn.close()
