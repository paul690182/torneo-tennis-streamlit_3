
import streamlit as st
import sqlite3
import pandas as pd

st.title("Torneo Tennis - Tutti contro tutti")

# Connessione al database
conn = sqlite3.connect("torneo.db")
c = conn.cursor()

# Lista giocatori
giocatori = [f"Giocatore {i}" for i in range(1, 13)]

# Inserimento risultato
st.header("Inserisci Risultato")
g1 = st.selectbox("Giocatore 1", giocatori)
g2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != g1])
punteggio = st.text_input("Punteggio (es. 6-4, 3-6, 7-5)")
vincitore = st.selectbox("Vincitore", [g1, g2])

if st.button("Salva Risultato"):
    c.execute("INSERT INTO risultati (giocatore1, giocatore2, punteggio, vincitore) VALUES (?, ?, ?, ?)",
              (g1, g2, punteggio, vincitore))
    conn.commit()
    st.success("Risultato salvato correttamente!")

# Classifica
st.header("Classifica")
df = pd.read_sql_query("SELECT * FROM risultati", conn)

classifica = {g: {"Partite": 0, "Vittorie": 0, "Set Vinti": 0, "Set Persi": 0, "Punti": 0} for g in giocatori}

for _, row in df.iterrows():
    g1, g2, punteggio, vincitore = row["giocatore1"], row["giocatore2"], row["punteggio"], row["vincitore"]
    set_g1, set_g2 = 0, 0
    for s in punteggio.split(","):
        p1, p2 = map(int, s.strip().split("-"))
        if p1 > p2:
            set_g1 += 1
        else:
            set_g2 += 1
    classifica[g1]["Partite"] += 1
    classifica[g2]["Partite"] += 1
    classifica[g1]["Set Vinti"] += set_g1
    classifica[g1]["Set Persi"] += set_g2
    classifica[g2]["Set Vinti"] += set_g2
    classifica[g2]["Set Persi"] += set_g1
    classifica[vincitore]["Vittorie"] += 1
    perdente = g2 if vincitore == g1 else g1
    classifica[vincitore]["Punti"] += 3
    if (set_g1, set_g2) in [(2,1), (1,2)]:
        classifica[perdente]["Punti"] += 1

df_classifica = pd.DataFrame.from_dict(classifica, orient="index")
st.dataframe(df_classifica.sort_values(by=["Punti", "Vittorie"], ascending=False))
conn.close()
