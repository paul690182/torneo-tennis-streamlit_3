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
# FUNZIONE VALIDAZIONE PUNTEGGI
# =============================
def valida_punteggio(val):
    if val == "" or val is None:
        return True
    try:
        val = int(val)
        return 0 <= val <= 20  # Range aggiornato
    except ValueError:
        return False

# =============================
# FUNZIONE CALCOLO CLASSIFICA
# =============================
def calcola_classifica(matches):
    # Dizionario per accumulare statistiche
    stats = {}
    for match in matches:
        g1 = match['giocatore1']
        g2 = match['giocatore2']

        # Inizializza giocatori
        if g1 not in stats:
            stats[g1] = {'Vinte': 0, 'Perse': 0, 'Punti': 0}
        if g2 not in stats:
            stats[g2] = {'Vinte': 0, 'Perse': 0, 'Punti': 0}

        # Conta set vinti
        set_g1 = 0
        set_g2 = 0
        for s1, s2 in [(match['set1_g1'], match['set1_g2']), (match['set2_g1'], match['set2_g2']), (match['set3_g1'], match['set3_g2'])]:
            if s1 is not None and s2 is not None:
                if s1 > s2:
                    set_g1 += 1
                elif s2 > s1:
                    set_g2 += 1

        # Determina vincitore
        if set_g1 > set_g2:
            stats[g1]['Vinte'] += 1
            stats[g2]['Perse'] += 1
            stats[g1]['Punti'] += 3  # 3 punti per vittoria
        elif set_g2 > set_g1:
            stats[g2]['Vinte'] += 1
            stats[g1]['Perse'] += 1
            stats[g2]['Punti'] += 3

    # Converti in DataFrame
    df = pd.DataFrame.from_dict(stats, orient='index')
    df = df.sort_values(by=['Punti', 'Vinte'], ascending=[False, False])
    return df.reset_index().rename(columns={'index': 'Giocatore'})

# =============================
# STREAMLIT UI
# =============================
st.title("F3BE Torneo Tennis - Gestione Risultati e Classifica")

# Selettore girone
st.subheader("Seleziona Girone")
girone = st.selectbox("Girone", ["Top", "Advanced"])

# Nome tabella in base al girone
nome_tabella = "risultati_top" if girone == "Top" else "risultati_advanced"

# =============================
# FORM INSERIMENTO RISULTATI
# =============================
st.subheader("Inserisci Match")
with st.form("inserisci_match"):
    giocatore1 = st.text_input("Giocatore 1")
    giocatore2 = st.text_input("Giocatore 2")

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
        # Validazione campi
        if not giocatore1 or not giocatore2:
            st.error("Inserisci entrambi i nomi dei giocatori.")
        elif not all(valida_punteggio(p) for p in [set1_g1, set1_g2, set2_g1, set2_g2, set3_g1, set3_g2]):
            st.error("I punteggi devono essere numeri interi tra 0 e 20 o vuoti.")
        else:
            # Conversione punteggi
            def conv(val):
                return int(val) if val != "" else None

            record = {
                "giocatore1": giocatore1,
                "giocatore2": giocatore2,
                "set1_g1": conv(set1_g1),
                "set1_g2": conv(set1_g2),
                "set2_g1": conv(set2_g1),
                "set2_g2": conv(set2_g2),
                "set3_g1": conv(set3_g1),
                "set3_g2": conv(set3_g2)
            }

            try:
                response = supabase.table(nome_tabella).insert(record).execute()
                st.success(f"Risultato salvato nel girone {girone}!")
            except Exception as e:
                st.error(f"Errore durante l'inserimento: {e}")

# =============================
# VISUALIZZAZIONE RISULTATI
# =============================
st.subheader(f"F4CB Risultati Girone {girone}")
try:
    data = supabase.table(nome_tabella).select("*").order("created_at", desc=True).execute()
    if data.data:
        for match in data.data:
            st.markdown(f"**{match['giocatore1']} vs {match['giocatore2']}**")
            st.write(f"Set 1: {match['set1_g1']}-{match['set1_g2']}")
            st.write(f"Set 2: {match['set2_g1']}-{match['set2_g2']}")
            st.write(f"Set 3: {match['set3_g1'] if match['set3_g1'] else '-'}-{match['set3_g2'] if match['set3_g2'] else '-'}")
            st.markdown("---")

        # =============================
        # CLASSIFICA AUTOMATICA
        # =============================
        st.subheader("

🏆 Classifica")
        df_classifica = calcola_classifica(data.data)
        st.table(df_classifica)
    else:
        st.info("Nessun risultato disponibile per questo girone.")
except Exception as e:
    st.error(f"Errore nel recupero dati: {e}")

