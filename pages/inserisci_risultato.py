import streamlit as st
from datetime import datetime
from supabase import create_client

# Connessione a Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
client = create_client(url, key)

# Liste giocatori aggiornate
lista_top = [
    "Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo", "Cris Cosso", "Giovanni", "Andrea P.",
    "Giuseppe", "Salvatore", "Leonardino", "Federico", "Luca", "Adriano"
]

lista_advanced = [
    "Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.", "Roberto A.", "Susanna", "Maura",
    "Paolo Mattioli", "Paola Colonna", "Paolo Rosi", "Michele", "Daniele M.", "Stefano D. R.", "Pino",
    "Gianni", "Leonardo", "Francesco M."
]

st.title("Inserisci Risultato Partita")

# Funzione per calcolare risultato e punti
def calcola_risultato(set1, set2, set3):
    sets = [set1, set2] + ([set3] if set3 else [])
    g1_vinti = 0
    g2_vinti = 0
    for s in sets:
        if "-" in s:
            try:
                p1, p2 = map(int, s.split("-"))
                if p1 > p2:
                    g1_vinti += 1
                else:
                    g2_vinti += 1
            except ValueError:
                pass
    return f"{g1_vinti}-{g2_vinti}", g1_vinti, g2_vinti

# Funzione per salvataggio su Supabase
def salva_risultato(sezione, giocatore1, giocatore2, set1, set2, set3):
    risultato, g1_vinti, g2_vinti = calcola_risultato(set1, set2, set3)
    punti_g1 = 0
    punti_g2 = 0
    if risultato == "2-0":
        punti_g1 = 3
    elif risultato == "0-2":
        punti_g2 = 3
    elif risultato == "2-1":
        punti_g1 = 3
        punti_g2 = 1
    elif risultato == "1-2":
        punti_g1 = 1
        punti_g2 = 3

    data = {
        "sezione": sezione,
        "giocatore1": giocatore1,
        "giocatore2": giocatore2,
        "set1": set1,
        "set2": set2,
        "set3": set3,
        "risultato": risultato,
        "punti_g1": punti_g1,
        "punti_g2": punti_g2,
        "timestamp": datetime.now().isoformat()
    }
    client.table("partite").insert(data).execute()

# Form separato per TOP
with st.form("form_top"):
    st.subheader("Inserisci risultato TOP")
    giocatore1_top = st.selectbox("Giocatore 1 (Top)", lista_top, key="top_player1")
    giocatore2_top = st.selectbox("Giocatore 2 (Top)", lista_top, key="top_player2")
    set1_top = st.text_input("Set 1", key="top_set1")
    set2_top = st.text_input("Set 2", key="top_set2")
    set3_top = st.text_input("Set 3", key="top_set3")
    st.write(f"**Riepilogo:** {giocatore1_top} vs {giocatore2_top} | {set1_top}, {set2_top}, {set3_top}")
    salva_top = st.form_submit_button("Salva TOP")
    reset_top = st.form_submit_button("Reset TOP")

if reset_top:
    st.session_state.clear()
    st.experimental_rerun()

if salva_top:
    if giocatore1_top == giocatore2_top:
        st.error("⚠ Giocatore 1 e Giocatore 2 devono essere diversi!")
    else:
        st.warning(f"Confermi il salvataggio di {giocatore1_top} vs {giocatore2_top}?")
        salva_risultato("Top", giocatore1_top, giocatore2_top, set1_top, set2_top, set3_top)
        st.success("✅ Risultato TOP salvato!")
        st.experimental_rerun()

# Form separato per ADVANCED
with st.form("form_advanced"):
    st.subheader("Inserisci risultato ADVANCED")
    giocatore1_adv = st.selectbox("Giocatore 1 (Advanced)", lista_advanced, key="adv_player1")
    giocatore2_adv = st.selectbox("Giocatore 2 (Advanced)", lista_advanced, key="adv_player2")
    set1_adv = st.text_input("Set 1", key="adv_set1")
    set2_adv = st.text_input("Set 2", key="adv_set2")
    set3_adv = st.text_input("Set 3", key="adv_set3")
    st.write(f"**Riepilogo:** {giocatore1_adv} vs {giocatore2_adv} | {set1_adv}, {set2_adv}, {set3_adv}")
    salva_adv = st.form_submit_button("Salva ADVANCED")
    reset_adv = st.form_submit_button("Reset ADVANCED")

if reset_adv:
    st.session_state.clear()
    st.experimental_rerun()

if salva_adv:
    if giocatore1_adv == giocatore2_adv:
        st.error("⚠ Giocatore 1 e Giocatore 2 devono essere diversi!")
    else:
        st.warning(f"Confermi il salvataggio di {giocatore1_adv} vs {giocatore2_adv}?")
        salva_risultato("Advanced", giocatore1_adv, giocatore2_adv, set1_adv, set2_adv, set3_adv)
        st.success("✅ Risultato ADVANCED salvato!")
        st.experimental_rerun()

