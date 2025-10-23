
import streamlit as st
import sqlite3
import pandas as pd

st.title("Torneo Tennis - Tutti contro tutti")

giocatori = [f"Giocatore {i}" for i in range(1, 13)]

def get_connection():
    return sqlite3.connect("torneo.db")

st.header("Inserisci Risultato")
with st.form("inserimento"):
    g1 = st.selectbox("Giocatore 1", giocatori)
    g2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != g1])
    punteggio = st.text_input("Punteggio (es. 6-4, 3-6, 7-5)")
    vincitore = st.selectbox("Vincitore", [g1, g2])
    submitted = st.form_submit_button("Salva Risultato")

    if submitted:
        conn = get_connection()
        conn.execute("INSERT INTO risultati (giocatore1, giocatore2, punteggio, vincitore) VALUES (?, ?, ?, ?)",
                     (g1, g2, punteggio, vincitore))
        conn.commit()
        conn.close()
        st.success("Risultato salvato correttamente!")

st.header("Classifica")
conn = get_connection()
df = pd.read_sql_query("SELECT * FROM risultati", conn)
conn.close()

classifica = pd.DataFrame({
    "Giocatore": giocatori,
    "Partite Giocate": [0]*12,
    "Vittorie": [0]*12,
    "Set Vinti": [0]*12,
    "Set Persi": [0]*12
})

for _, row in df.iterrows():
    g1, g2, punteggio, vincitore = row["giocatore1"], row["giocatore2"], row["punteggio"], row["vincitore"]
    sets = punteggio.split(',')
    sets_g1, sets_g2 = 0, 0
    for s in sets:
        try:
            p1, p2 = map(int, s.strip().split('-'))
            if p1 > p2:
                sets_g1 += 1
            else:
                sets_g2 += 1
        except:
            continue
    for g in [g1, g2]:
        idx = classifica[classifica["Giocatore"] == g].index[0]
        classifica.at[idx, "Partite Giocate"] += 1
    idx1 = classifica[classifica["Giocatore"] == g1].index[0]
    idx2 = classifica[classifica["Giocatore"] == g2].index[0]
    classifica.at[idx1, "Set Vinti"] += sets_g1
    classifica.at[idx1, "Set Persi"] += sets_g2
    classifica.at[idx2, "Set Vinti"] += sets_g2
    classifica.at[idx2, "Set Persi"] += sets_g1
    idx_v = classifica[classifica["Giocatore"] == vincitore].index[0]
    classifica.at[idx_v, "Vittorie"] += 1

st.dataframe(classifica.sort_values(by=["Vittorie", "Set Vinti"], ascending=False))
