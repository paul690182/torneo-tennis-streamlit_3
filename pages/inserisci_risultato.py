import streamlit as st
from datetime import datetime
from supabase import create_client

# Connessione a Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
client = create_client(url, key)

# Liste giocatori per le due sezioni (aggiornate)
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

# Selezione sezione
sezione = st.radio("Seleziona sezione", ["Top", "Advanced"])

if sezione == "Top":
    st.subheader("Inserisci risultato TOP")
    lista_giocatori = lista_top
else:
    st.subheader("Inserisci risultato ADVANCED")
    lista_giocatori = lista_advanced

# Selectbox con chiavi dinamiche basate sulla sezione
col1, col2 = st.columns(2)
with col1:
    giocatore1 = st.selectbox("Giocatore 1", lista_giocatori, key=f"{sezione}_player1")
with col2:
    giocatore2 = st.selectbox("Giocatore 2", lista_giocatori, key=f"{sezione}_player2")

# Controllo per evitare che siano uguali
if giocatore1 == giocatore2:
    st.error("⚠ Giocatore 1 e Giocatore 2 devono essere diversi!")
else:
    # Input dei set
    set1 = st.text_input("Set 1 (es. 6-4)", key=f"{sezione}_set1")
    set2 = st.text_input("Set 2 (es. 6-3)", key=f"{sezione}_set2")
    set3 = st.text_input("Set 3 (opzionale, es. 7-5)", key=f"{sezione}_set3")

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

    risultato, g1_vinti, g2_vinti = calcola_risultato(set1, set2, set3)

    # Logica punti
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

    # Salvataggio su Supabase
    if st.button("Salva Risultato"):
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
        try:
            client.table("partite").insert(data).execute()
            st.success(f"✅ Risultato salvato: {giocatore1} vs {giocatore2} ({risultato})")

            # Reset automatico dei campi
            st.session_state[f"{sezione}_player1"] = lista_giocatori[0]
            st.session_state[f"{sezione}_player2"] = lista_giocatori[0]
            st.session_state[f"{sezione}_set1"] = ""
            st.session_state[f"{sezione}_set2"] = ""
            st.session_state[f"{sezione}_set3"] = ""

        except Exception as e:
            st.error(f"Errore nel salvataggio: {e}")
