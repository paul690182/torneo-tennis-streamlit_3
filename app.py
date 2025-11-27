
import streamlit as st
from supabase import create_client, Client
import pandas as pd

# =============================
# CONFIGURAZIONE SUPABASE
# =============================
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"  # Inserisci il tuo URL Supabase
SUPABASE_KEY = "YOUR_ANON_KEY"  # Inserisci la tua chiave anon

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =============================
# LISTE GIOCATORI COMPLETE
# =============================
GIOCATORI_TOP = [
    "Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo", "Cris Cosso", "Giovanni",
    "Andrea P.", "Giuseppe", "Salvatore", "Leonardino", "Federico", "Luca", "Adriano"
]

GIOCATORI_ADVANCED = [
    "Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.", "Roberto A.", "Susanna",
    "Paolo Mattioli", "Paolo Rosi", "Michele", "Daniele M.", "Stefano D. R.", "Pino",
    "Gianni", "Leonardo", "Francesco M."
]

# =============================
# FUNZIONE VALIDAZIONE PUNTEGGI
# =============================
def valida_punteggio(val):
    if val == "" or val is None:
        return True
    try:
        val = int(val)
        return 0 <= val <= 20
    except ValueError:
        return False

# =============================
# FUNZIONE CALCOLO CLASSIFICA
# =============================
def calcola_classifica(matches):
    stats = {}
    for match in matches:
        g1 = match['giocatore1']
        g2 = match['giocatore2']

        if g1 not in stats:
            stats[g1] = {'Vinte': 0, 'Perse': 0, 'Punti': 0}
        if g2 not in stats:
            stats[g2] = {'Vinte': 0, 'Perse': 0, 'Punti': 0}

        set_g1 = 0
        set_g2 = 0
        for s1, s2 in [(match['set1_g1'], match['set1_g2']), (match['set2_g1'], match['set2_g2']), (match['set3_g1'], match['set3_g2'])]:
            if s1 is not None and s2 is not None:
                if s1 > s2:
                    set_g1 += 1
                elif s2 > s1:
                    set_g2 += 1

        if set_g1 > set_g2:
            stats[g1]['Vinte'] += 1
            stats[g2]['Perse'] += 1
            stats[g1]['Punti'] += 3
        elif set_g2 > set_g1:
            stats[g2]['Vinte'] += 1
            stats[g1]['Perse'] += 1
            stats[g2]['Punti'] += 3

    df = pd.DataFrame.from_dict(stats, orient='index')
    df = df.sort_values(by=['Punti', 'Vinte'], ascending=[False, False])
    return df.reset_index().rename(columns={'index': 'Giocatore'})

# =============================
# STREAMLIT UI
# =============================
st.title("🎾 Torneo Tennis - Gestione Risultati e Classifica")

st.subheader("Seleziona Girone")
girone = st.selectbox("Girone", ["Top", "Advanced"])

nome_tabella = "risultati_top" if girone == "Top" else "risultati_advanced"
lista_giocatori = GIOCATORI_TOP if girone == "Top" else GIOCATORI_ADVANCED

# =============================
# FORM INSERIMENTO RISULTATI
# =============================
st.subheader("Inserisci Match")
with st.form("inserisci_match", clear_on_submit=True):
    giocatore1 = st.selectbox("Giocatore 1", lista_giocatori)
    giocatore2 = st.selectbox("Giocatore 2", [g for g in lista_giocatori if g != giocatore1])

    st.write("**Set 1**")
    set1_g1 = st.text_input("Punteggio Giocatore 1 (Set 1)")
    set1_g2 = st.text_input("Punteggio Giocatore 2 (Set 1)")

    st.write("**Set 2**")
    set2_g1 = st.text_input("Punteggio Giocatore 1 (Set 2)")
    set2_g2 = st.text_input("Punteggio Giocatore 2 (Set 2)")

    st.write("**Set 3 (opzionale)**")
    set3_g1 = st.text_input("Punteggio Giocatore 1 (Set 3)")
    set3_g2 = st.text_input("Punteggio Giocatore 2 (Set 3)")

    submitted = st.form_submit_button("Salva Risultato")

    if submitted:
