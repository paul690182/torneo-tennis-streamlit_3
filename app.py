
import streamlit as st
import sqlite3
import pandas as pd

st.title("Torneo Tennis - Tutti contro tutti")

# Connessione al database
conn = sqlite3.connect("torneo.db")
cursor = conn.cursor()

# Lista giocatori
giocatori = [f"Giocatore {i}" for i in range(1, 13)]

# Form inserimento risultato
st.subheader("Inserisci Risultato")
g1 = st.selectbox("Giocatore 1", giocatori)
g2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != g1])
punteggio = st.text_input("Punteggio (es. 6-4, 3-6, 7-5)")
vincitore = st.selectbox("Vincitore", [g1, g2])

if st.button("Salva Risultato"):
    conn.execute("INSERT INTO risultati (giocatore1, giocatore2, punteggio, vincitore) VALUES (?, ?, ?, ?)",
                 (g1, g2, punteggio, vincitore))
    conn.commit()
    st.success("Risultato salvato correttamente!")

# Visualizza classifica
st.subheader("Classifica")
df = pd.read_sql_query("SELECT * FROM risultati", conn)

if not df.empty:
    classifica = pd.DataFrame({"Giocatore": giocatori,
                               "Partite giocate": [0]*12,
                               "Vittorie": [0]*12,
                               "Set vinti": [0]*12,
                               "Set persi": [0]*12})

    for _, row in df.iterrows():
        g1 = row["giocatore1"]
        g2 = row["giocatore2"]
        vincitore = row["vincitore"]
        punteggi = row["punteggio"].split(',')

        idx1 = giocatori.index(g1)
        idx2 = giocatori.index(g2)

        classifica.at[idx1, "Partite giocate"] += 1
        classifica.at[idx2, "Partite giocate"] += 1

        if vincitore == g1:
            classifica.at[idx1, "Vittorie"] += 1
        else:
            classifica.at[idx2, "Vittorie"] += 1

        for set_score in punteggi:
            try:
                s1, s2 = map(int, set_score.strip().split('-'))
                classifica.at[idx1, "Set vinti"] += int(s1 > s2)
                classifica.at[idx2, "Set vinti"] += int(s2 > s1)
                classifica.at[idx1, "Set persi"] += int(s1 < s2)
                classifica.at[idx2, "Set persi"] += int(s2 < s1)
            except:
                continue

    st.dataframe(classifica.sort_values(by=["Vittorie", "Set vinti"], ascending=False))
else:
    st.info("Nessun risultato inserito.")

conn.close()
