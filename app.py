
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date
import os

# Configurazione Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Torneo Tennis - Inserimento Partite e Classifica")

# Recupera i dati esistenti
data_response = supabase.table("partite_classifica").select("*").execute()
df = pd.DataFrame(data_response.data)

# Selezione giocatori
if df.empty:
    giocatori = []
else:
    giocatori = pd.unique(df[['giocatore1', 'giocatore2']].values.ravel('K'))

# Funzione per calcolare punteggi dai set
def calcola_punteggi(set1, set2, set3):
    punteggi_g1 = 0
    punteggi_g2 = 0
    set_list = [set1, set2, set3]
    for s in set_list:
        if s:
            try:
                g1_score, g2_score = map(int, s.split("-"))
                if g1_score > g2_score:
                    punteggi_g1 += 1
                elif g2_score > g1_score:
                    punteggi_g2 += 1
            except:
                pass
    return punteggi_g1, punteggi_g2

# Form inserimento partita
if len(giocatori) == 0:
    st.warning("Nessun giocatore disponibile. Inserisci almeno una partita manualmente nel database.")
else:
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
                supabase.table("partite_classifica").insert({
                    "giocatore1": g1,
                    "giocatore2": g2,
                    "set1": set1,
                    "set2": set2,
                    "set3": set3 if set3 else None,
                    "punteggio_g1": pg1,
                    "punteggio_g2": pg2,
                    "vincitore": vincitore,
                    "data_partita": str(data_partita)
                }).execute()
                st.success("Partita inserita correttamente!")

# Visualizza lo storico partite
st.subheader("Storico Partite")
if df.empty:
    st.info("Nessuna partita registrata.")
else:
    for _, row in df.iterrows():
        st.markdown(f"**{row['giocatore1']} vs {row['giocatore2']}**")
        punteggi = [row['set1'], row['set2'], row['set3']]
        punteggi = [s for s in punteggi if s]
        st.write("Set giocati:", ", ".join(punteggi))
        st.write(f"Punteggio: {row['punteggio_g1']} - {row['punteggio_g2']}")
        st.write(f"Vincitore: {row['vincitore']}")
        st.write(f"Data: {row['data_partita']}")
        st.markdown("---")

# Calcola classifica con punteggio personalizzato
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
