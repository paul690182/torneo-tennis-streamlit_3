
import streamlit as st
import requests
import os
from datetime import datetime

# =============================
# CONFIGURAZIONE SUPABASE
# =============================
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

# =============================
# FUNZIONI DI SUPPORTO
# =============================
def log_message(msg, level="info"):
    if level == "success":
        st.markdown(f"✅ **{msg}**")
    elif level == "warning":
        st.markdown(f"⚠️ **{msg}**")
    elif level == "error":
        st.markdown(f"❌ **{msg}**")
    else:
        st.markdown(f"ℹ️ {msg}")

def salva_risultato(giocatore1, giocatore2, set1_g1, set1_g2, set2_g1, set2_g2, set3_g1, set3_g2, note):
    url = f"{SUPABASE_URL}/rest/v1/risultati_advanced"
    payload = {
        "giocatore1": giocatore1,
        "giocatore2": giocatore2,
        "set1_g1": set1_g1,
        "set1_g2": set1_g2,
        "set2_g1": set2_g1,
        "set2_g2": set2_g2,
        "set3_g1": set3_g1,
        "set3_g2": set3_g2,
        "note": note,
        "created_at": datetime.utcnow().isoformat()
    }
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code in (200, 201):
            log_message("Risultato salvato correttamente nel database.", "success")
        else:
            log_message(f"Errore nel salvataggio: {response.status_code} - {response.text}", "error")
    except Exception as e:
        log_message(f"Eccezione durante il salvataggio: {e}", "error")

# =============================
# INTERFACCIA STREAMLIT
# =============================
st.title("🏆 Inserisci Risultato")
st.write("Compila i punteggi dei set e salva il risultato.")

# Selezione giocatori (dropdown)
st.subheader("Giocatori")
# Lista statica (puoi sostituire con query al DB)
giocatori = ["Daniele M.", "Stefano D. R.", "Paolo R.", "Francesco M.", "Massimo B.", "Simone V.", "Gianni F.", "Leo S.", "Giovanni D.", "Andrea P.", "Maurizio P."]
giocatore1 = st.selectbox("Giocatore A", giocatori)
giocatore2 = st.selectbox("Giocatore B", [g for g in giocatori if g != giocatore1])

st.markdown("---")
st.subheader("Risultato (punteggi dei set)")

# --- Set 1 ---
set1_g1 = st.number_input("Set 1 - Giocatore A", min_value=0, max_value=7, step=1)
set1_g2 = st.number_input("Set 1 - Giocatore B", min_value=0, max_value=7, step=1)

# --- Set 2 ---
aggiungi_set2 = st.checkbox("Aggiungi Set 2")
if aggiungi_set2:
    set2_g1 = st.number_input("Set 2 - Giocatore A", min_value=0, max_value=7, step=1)
    set2_g2 = st.number_input("Set 2 - Giocatore B", min_value=0, max_value=7, step=1)
else:
    set2_g1, set2_g2 = 0, 0

# --- Set 3 (super tie-break) ---
aggiungi_set3 = st.checkbox("Aggiungi Set 3")
if aggiungi_set3:
    set3_g1 = st.number_input("Set 3 - Giocatore A", min_value=0, max_value=20, step=1)
    set3_g2 = st.number_input("Set 3 - Giocatore B", min_value=0, max_value=20, step=1)
else:
    set3_g1, set3_g2 = 0, 0

note = st.text_area("Note (opzionale)")

# =============================
# VALIDAZIONE
# =============================
error_messages = []

# Validazione Set 1
if set1_g1 == set1_g2 and (set1_g1 > 0 or set1_g2 > 0):
    error_messages.append("Il punteggio del Set 1 non può essere pari.")

# Validazione Set 2
if aggiungi_set2 and set2_g1 == set2_g2 and (set2_g1 > 0 or set2_g2 > 0):
    error_messages.append("Il punteggio del Set 2 non può essere pari.")

# Validazione Set 3 (super tie-break)
if aggiungi_set3 and (set3_g1 > 0 or set3_g2 > 0):
    if set3_g1 == set3_g2:
        error_messages.append("Il punteggio del 3° set non può essere pari.")
    else:
        max_punti = max(set3_g1, set3_g2)
        diff = abs(set3_g1 - set3_g2)
        if max_punti < 8:
            error_messages.append("Il vincitore del 3° set deve avere almeno 8 punti.")
        elif diff < 2:
            error_messages.append("Il vincitore del 3° set deve avere almeno 2 punti di vantaggio.")
        elif max_punti > 20:
            error_messages.append("Il punteggio massimo consentito nel 3° set è 20.")

# =============================
# SALVATAGGIO
# =============================
if st.button("Salva risultato"):
    if not giocatore1 or not giocatore2:
        st.error("Seleziona entrambi i giocatori.")
    elif error_messages:
        for msg in error_messages:
            st.error(msg)
    else:
        salva_risultato(giocatore1, giocatore2, set1_g1, set1_g2, set2_g1, set2_g2, set3_g1, set3_g2, note)


