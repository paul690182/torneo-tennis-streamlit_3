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
with st.form("form_top", clear_on_submit=True):
    st.subheader("Inserisci risultato TOP")
    giocatore1_top = st.selectbox("Giocatore 1 (Top)", ["Seleziona..."] + lista_top, index=0)
    giocatore2_top = st.selectbox("Giocatore 2 (Top)", ["Seleziona..."] + lista_top, index=0)
    set1_top = st.text_input("Set 1")
    set2_top = st.text_input("Set 2")
    set3_top = st.text_input("Set 3 (opzionale)")
    salva_top = st.form_submit_button("Salva TOP")

if salva_top:
    if giocatore1_top == "Seleziona..." or giocatore2_top == "Seleziona...":
        st.error("⚠ Devi selezionare entrambi i giocatori!")
    elif giocatore1_top == giocatore2_top:
        st.error("⚠ Giocatore 1 e Giocatore 2 devono essere diversi!")
    else:
        st.warning(f"Confermi il salvataggio di {giocatore1_top} vs {giocatore2_top}?")
        salva_risultato("Top", giocatore1_top, giocatore2_top, set1_top, set2_top, set3_top)
        st.success("✅ Risultato TOP salvato!")

# Form separato per ADVANCED
with st.form("form_advanced", clear_on_submit=True):
    st.subheader("Inserisci risultato ADVANCED")
    giocatore1_adv = st.selectbox("Giocatore 1 (Advanced)", ["Seleziona..."] + lista_advanced, index=0)
    giocatore2_adv = st.selectbox("Giocatore 2 (Advanced)", ["Seleziona..."] + lista_advanced, index=0)
    set1_adv = st.text_input("Set 1")
    set2_adv = st.text_input("Set 2")
    set3_adv = st.text_input("Set 3 (opzionale)")
    salva_adv = st.form_submit_button("Salva ADVANCED")

if salva_adv:
    if giocatore1_adv == "Seleziona..." or giocatore2_adv == "Seleziona...":
        st.error("⚠ Devi selezionare entrambi i giocatori!")
    elif giocatore1_adv == giocatore2_adv:
        st.error("⚠ Giocatore 1 e Giocatore 2 devono essere diversi!")
    else:
        st.warning(f"Confermi il salvataggio di {giocatore1_adv} vs {giocatore2_adv}?")
        salva_risultato("Advanced", giocatore1_adv, giocatore2_adv, set1_adv, set2_adv, set3_adv)
        st.success("✅ Risultato ADVANCED salvato!")
