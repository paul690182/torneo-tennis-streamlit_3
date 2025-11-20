import streamlit as st
from supabase import create_client

# Configurazione Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Inserisci Risultato")

# Selezione torneo
TORNEI = ["top", "advanced"]
torneo = st.selectbox("Seleziona il torneo", TORNEI)

giocatore1 = st.text_input("Giocatore 1")
giocatore2 = st.text_input("Giocatore 2")
set1 = st.text_input("Set 1 (es. 6-4)")
set2 = st.text_input("Set 2 (es. 6-4)")
set3 = st.text_input("Set 3 (opzionale)")

# Funzione per inserire partita e aggiornare classifica
def inserisci_partita(torneo, giocatore1, giocatore2, set_list):
    tabella_risultati = "risultati_top" if torneo == "top" else "risultati_advanced"
    tabella_classifica = "classifica_top" if torneo == "top" else "classifica_advanced"

    # Determina vincitore (logica semplice: chi vince più set)
    sets_g1 = sum([1 for s in set_list if s and s.split("-")[0] > s.split("-")[1]])
    sets_g2 = sum([1 for s in set_list if s and s.split("-")[0] < s.split("-")[1]])
    vincitore = giocatore1 if sets_g1 > sets_g2 else giocatore2

    # Inserisci risultato
    supabase.table(tabella_risultati).insert({
        "giocatore1": giocatore1,
        "giocatore2": giocatore2,
        "set1": set_list[0],
        "set2": set_list[1],
        "set3": set_list[2],
        "vincitore": vincitore
    }).execute()

    # Aggiorna classifica
    aggiorna_classifica(tabella_classifica, vincitore, giocatore1 if vincitore != giocatore1 else giocatore2)

def aggiorna_classifica(tabella, vincitore, sconfitto):
    # Leggi riga vincitore
    vincitore_row = supabase.table(tabella).select("*").eq("giocatore", vincitore).execute().data
    sconfitto_row = supabase.table(tabella).select("*").eq("giocatore", sconfitto).execute().data

    # Se non esiste, crea la riga
    if not vincitore_row:
        supabase.table(tabella).insert({"giocatore": vincitore, "vinte": 0, "perse": 0, "punti": 0}).execute()
        vincitore_row = [{"vinte": 0, "perse": 0, "punti": 0}]

    if not sconfitto_row:
        supabase.table(tabella).insert({"giocatore": sconfitto, "vinte": 0, "perse": 0, "punti": 0}).execute()
        sconfitto_row = [{"vinte": 0, "perse": 0, "punti": 0}]

    # Aggiorna valori
    nuove_vinte = vincitore_row[0].get("vinte", 0) + 1
    nuove_perse = sconfitto_row[0].get("perse", 0) + 1

    supabase.table(tabella).update({
        "vinte": nuove_vinte,
        "punti": vincitore_row[0].get("punti", 0) + 3  # 3 punti per vittoria
    }).eq("giocatore", vincitore).execute()

    supabase.table(tabella).update({
        "perse": nuove_perse,
        "punti": sconfitto_row[0].get("punti", 0) + 1  # 1 punto per sconfitta
    }).eq("giocatore", sconfitto).execute()

# Bottone per inserire risultato
if st.button("Inserisci Risultato"):
    if giocatore1 and giocatore2 and giocatore1 != giocatore2:
        inserisci_partita(torneo, giocatore1, giocatore2, [set1, set2, set3])
        st.success("Risultato inserito e classifica aggiornata!")
    else:
        st.error("Inserisci due giocatori diversi e almeno due set.")
