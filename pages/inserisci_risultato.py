

import streamlit as st
from validazione_torneo import TorneoTennis
from supabase import create_client
import os

# Configurazione Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Inserisci Risultato - Torneo Tennis (Girone Advanced)")

# Inizializza lo stato
if "torneo" not in st.session_state:
    st.session_state["torneo"] = TorneoTennis()

torneo = st.session_state["torneo"]

# Form per inserimento risultato
with st.form("form_risultato"):
    st.subheader("Dati del Match")
    giocatore1 = st.text_input("Giocatore 1")
    giocatore2 = st.text_input("Giocatore 2")

    st.markdown("Punteggi dei set")
    col1, col2 = st.columns(2)
    with col1:
        set1_g1 = st.number_input("Set1 G1", min_value=0, max_value=7, value=6)
        set2_g1 = st.number_input("Set2 G1", min_value=0, max_value=7, value=4)
        set3_g1 = st.number_input("Set3 G1", min_value=0, max_value=20, value=10)
    with col2:
        set1_g2 = st.number_input("Set1 G2", min_value=0, max_value=7, value=4)
        set2_g2 = st.number_input("Set2 G2", min_value=0, max_value=7, value=6)
        set3_g2 = st.number_input("Set3 G2", min_value=0, max_value=20, value=4)

    submit = st.form_submit_button("Salva risultato")

# Logica inserimento
if submit:
    if not giocatore1 or not giocatore2:
        st.error("Inserisci entrambi i nomi dei giocatori.")
    else:
        try:
            match = torneo.inserisci_risultato(
                giocatore1.strip(), giocatore2.strip(),
                (set1_g1, set1_g2),
                (set2_g1, set2_g2),
                (set3_g1, set3_g2)
            )
            st.success(f"Risultato inserito. Vincitore: {match.vincitore}")

            # ✅ Inserimento su Supabase
            data = {
                "giocatore1": giocatore1.strip(),
                "giocatore2": giocatore2.strip(),
                "set1_g1": set1_g1,
                "set1_g2": set1_g2,
                "set2_g1": set2_g1,
                "set2_g2": set2_g2,
                "set3_g1": set3_g1,
                "set3_g2": set3_g2,
                "vincitore": match.vincitore
            }
            response = supabase.table("risultati_advanced").insert(data).execute()

            if response.get("status_code") == 200:
                st.success("Dati salvati su Supabase!")
            else:
                st.warning(f"Attenzione: {response}")

        except Exception as e:
            st.error(f"Errore: {e}")

# Mostra classifica dinamica
st.subheader("Classifica Dinamica")
if torneo.classifica:
    for pos, (player, pts) in enumerate(torneo.classifica_ordinata(), start=1):
        st.write(f"{pos}. {player} — {pts} punti")
else:
    st.info("Nessun risultato inserito.")

# Storico risultati
st.subheader("Storico Risultati")
if torneo.risultati:
    for m in torneo.risultati:
        st.write(f"{m.giocatore1} vs {m.giocatore2} → {m.set1}, {m.set2}, {m.set3} | Vincitore: {m.vincitore}")
else:
    st.info("Ancora nessun match registrato.")

