import streamlit as st
from supabase import create_client

# Configurazione Supabase
from supabase_config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

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

# Funzione per aggiornare la classifica
def aggiorna_classifica(torneo, vincitore, sconfitto, punti_vincitore, punti_sconfitto):
    tabella = "classifica_top" if torneo == "Top" else "classifica_advanced"
    supabase.table(tabella).update({"punti": supabase.rpc("increment", {"col": "punti", "val": punti_vincitore}),
                                    "vinte": supabase.rpc("increment", {"col": "vinte", "val": 1})}).eq("giocatore", vincitore).execute()
    supabase.table(tabella).update({"punti": supabase.rpc("increment", {"col": "punti", "val": punti_sconfitto}),
                                    "perse": supabase.rpc("increment", {"col": "perse", "val": 1})}).eq("giocatore", sconfitto).execute()

# Funzione per inserire la partita
def inserisci_partita(torneo, giocatore1, giocatore2, set_list):
    tabella = "partite_top" if torneo == "Top" else "partite_advanced"
    supabase.table(tabella).insert({"giocatore1": giocatore1, "giocatore2": giocatore2, "risultato": ", ".join(set_list)}).execute()
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
        st.success("Risultato inserito e classifica aggiornata!")
    else:
        st.error("Inserisci almeno un set valido.")
