
import streamlit as st
import pandas as pd
from datetime import date
import uuid

@st.cache_data
def carica_partite():
    return pd.read_csv("partite_classifica_rows.csv")

df = carica_partite()

giocatori = sorted(set(df['giocatore1']).union(set(df['giocatore2'])))

st.title("Torneo Tennis - Inserimento Risultati")

g1 = st.selectbox("Giocatore 1", giocatori)
g2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != g1])

set1 = st.text_input("Set 1 (es. 6-4)")
set2 = st.text_input("Set 2 (es. 3-6)")
set3 = st.text_input("Set 3 (opzionale)", "")

def calcola_punteggi(s1, s2, s3):
    g1_vinti = g2_vinti = 0
    for s in [s1, s2, s3]:
        if "-" in s:
            try:
                a, b = map(int, s.strip().split("-"))
                if a > b:
                    g1_vinti += 1
                elif b > a:
                    g2_vinti += 1
            except:
                pass
    return g1_vinti, g2_vinti

def partita_duplicata(df, g1, g2):
    return not df[((df['giocatore1'] == g1) & (df['giocatore2'] == g2)) |
                  ((df['giocatore1'] == g2) & (df['giocatore2'] == g1))].empty

if st.button("Salva partita"):
    if g1 == g2:
        st.error("I due giocatori devono essere diversi.")
    elif partita_duplicata(df, g1, g2):
        st.warning("Partita già inserita tra questi due giocatori.")
    else:
        p1, p2 = calcola_punteggi(set1, set2, set3)
        vincitore = g1 if p1 > p2 else g2
        nuova_riga = {
            "id": str(uuid.uuid4()),
            "giocatore1": g1,
            "giocatore2": g2,
            "set1": set1,
            "set2": set2,
            "set3": set3,
            "punteggio_g1": p1,
            "punteggio_g2": p2,
            "vincitore": vincitore,
            "data_partita": str(date.today())
        }
        df = pd.concat([df, pd.DataFrame([nuova_riga])], ignore_index=True)
        df.to_csv("partite_classifica_rows.csv", index=False)
        st.success(f"Partita salvata! Vincitore: {vincitore}")
