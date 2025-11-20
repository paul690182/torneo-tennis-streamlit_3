import streamlit as st
from supabase import create_client
from supabase_config import SUPABASE_URL, SUPABASE_KEY

# Connessione a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Liste giocatori
TOP_PLAYERS = [
    "Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo", "Cris Cosso", "Giovanni", "Andrea P.",
    "Giuseppe", "Salvatore", "Leonardino", "Federico", "Luca", "Adriano"
]

ADVANCED_PLAYERS = [
    "Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.", "Roberto A.", "Susanna", "Maura",
    "Paolo Mattioli", "Paola Colonna", "Paolo Rosi", "Michele", "Daniele M.", "Stefano D. R.", "Pino",
    "Gianni", "Leonardo", "Francesco M."
]

# Funzione per calcolare i punti

def calcola_punti(set_list):
    giocatore1_sets = 0
    giocatore2_sets = 0
    for s in set_list:
        g1, g2 = map(int, s.split('-'))
        if g1 > g2:
            giocatore1_sets += 1
        else:
            giocatore2_sets += 1

    if giocatore1_sets == 2:
        vincitore = "giocatore1"
        sconfitto = "giocatore2"
        if giocatore2_sets == 0:
            return vincitore, sconfitto, 3, 0
        else:
            return vincitore, sconfitto, 2, 1
    else:
        vincitore = "giocatore2"
        sconfitto = "giocatore1"
        if giocatore1_sets == 0:
            return vincitore, sconfitto, 3, 0
        else:
            return vincitore, sconfitto, 2, 1

# Funzione per aggiornare la classifica senza RPC

def aggiorna_classifica(torneo, vincitore, sconfitto, punti_vincitore, punti_sconfitto):
    tabella = "classifica_top" if torneo == "Top" else "classifica_advanced"

    # Aggiorna vincitore
    vincitore_row = supabase.table(tabella).select("*").eq("giocatore", vincitore).execute().data[0]
    nuovo_punteggio_vincitore = vincitore_row["punti"] + punti_vincitore
    nuove_vinte = vincitore_row["vinte"] + 1
    supabase.table(tabella).update({"punti": nuovo_punteggio_vincitore, "vinte": nuove_vinte}).eq("giocatore", vincitore).execute()

    # Aggiorna sconfitto
    sconfitto_row = supabase.table(tabella).select("*").eq("giocatore", sconfitto).execute().data[0]
    nuovo_punteggio_sconfitto = sconfitto_row["punti"] + punti_sconfitto
    nuove_perse = sconfitto_row["perse"] + 1
    supabase.table(tabella).update({"punti": nuovo_punteggio_sconfitto, "perse": nuove_perse}).eq("giocatore", sconfitto).execute()

# Funzione per inserire la partita con controllo duplicati

def inserisci_partita(torneo, giocatore1, giocatore2, set_list):
    tabella = "partite_top" if torneo == "Top" else "partite_advanced"

    # Controllo duplicati (anche inverso)
    existing_match = supabase.table(tabella).select("*").or_(f"giocatore1.eq.{giocatore1},giocatore2.eq.{giocatore2}").execute().data
    inverse_match = supabase.table(tabella).select("*").or_(f"giocatore1.eq.{giocatore2},giocatore2.eq.{giocatore1}").execute().data

    if existing_match or inverse_match:
        st.error("Questa partita è già stata inserita!")
        return

    # Inserisci partita
    supabase.table(tabella).insert({"giocatore1": giocatore1, "giocatore2": giocatore2, "risultato": ", ".join(set_list)}).execute()

    # Calcola punti e aggiorna classifica
    vincitore, sconfitto, punti_vincitore, punti_sconfitto = calcola_punti(set_list)
    if vincitore == "giocatore1":
        aggiorna_classifica(torneo, giocatore1, giocatore2, punti_vincitore, punti_sconfitto)
    else:
        aggiorna_classifica(torneo, giocatore2, giocatore1, punti_vincitore, punti_sconfitto)

# Interfaccia Streamlit
st.title("Inserisci Risultato")

# Selezione torneo
torneo = st.selectbox("Seleziona il torneo", ["Top", "Advanced"])

# Selezione giocatori
players = TOP_PLAYERS if torneo == "Top" else ADVANCED_PLAYERS
giocatore1 = st.selectbox("Giocatore 1", players)
giocatore2 = st.selectbox("Giocatore 2", [p for p in players if p != giocatore1])

# Inserimento set
set_input = st.text_input("Inserisci i set separati da virgola (es. 6-4, 3-6, 6-3)")

if st.button("Salva Risultato"):
    if set_input:
        set_list = [s.strip() for s in set_input.split(',')]
        inserisci_partita(torneo, giocatore1, giocatore2, set_list)
    else:
        st.error("Inserisci almeno un set valido.")
