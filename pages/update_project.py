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
    'Content-Type': 'application/json'
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

# Funzione per ottenere colonne di una tabella

def get_columns(table_name):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200 and response.json():
        return list(response.json()[0].keys())
    return []

# Funzione per cancellare righe in base a colonne

def delete_rows(table_name, valid_columns, names_to_remove):
    columns = get_columns(table_name)
    matched_cols = [col for col in columns if col in valid_columns]
    if not matched_cols:
        log_message(f"In '{table_name}' non trovata nessuna tra {valid_columns}. Colonne presenti: {columns}", "warning")
        return
    for col in matched_cols:
        for name in names_to_remove:
            url = f"{SUPABASE_URL}/rest/v1/{table_name}"
            params = {col: f"eq.{name}"}
            response = requests.delete(url, headers=HEADERS, params=params)
            if response.status_code == 200:
                log_message(f"Cancellate righe da '{table_name}' usando colonna '{col}'.", "success")
            else:
                log_message(f"Errore cancellando da '{table_name}' con colonna '{col}': {response.text}", "error")

# Funzione per azzerare colonne pivot

def nullify_columns(table_name, pivot_cols):
    columns = get_columns(table_name)
    matched_cols = [col for col in columns if col in pivot_cols]
    if not matched_cols:
        log_message(f"Nessuna colonna pivot trovata in '{table_name}'. Colonne presenti: {columns}", "warning")
        return
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    payload = {col: None for col in matched_cols}
    response = requests.patch(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        log_message(f"Azzerate/NULL le colonne {matched_cols} su tutte le righe di '{table_name}'.", "success")
    else:
        log_message(f"Errore azzerando colonne in '{table_name}': {response.text}", "error")

# =============================
# INTERFACCIA STREAMLIT
# =============================

st.title("🔧 Manutenzione progetto")
st.write("Questa pagina rimuove giocatori specifici e applica regole di validazione.")

st.markdown("---")
st.subheader("⚙️ Operazioni disponibili")
st.write("- Rimozione giocatori da tabelle avanzate")
st.write("- Azzeramento colonne pivot (se presenti)")
st.write("- Conferma regola super tie-break")

if st.button("Esegui manutenzione"):
    start_time = datetime.now()
    giocatori_da_rimuovere = ["Paola", "Maura"]

    st.markdown("### 🔍 Avanzamento")

    # 1. classifica_advanced
    delete_rows("classifica_advanced", ["giocatore"], giocatori_da_rimuovere)

    # 2. risultati_advanced (FIX: usa giocatore1 e giocatore2)
    delete_rows("risultati_advanced", ["giocatore1", "giocatore2"], giocatori_da_rimuovere)

    # 3. partite_advanced
    delete_rows("partite_advanced", ["giocatore1", "giocatore2"], giocatori_da_rimuovere)

    # 4. Azzeramento colonne pivot (se presenti)
    nullify_columns("partite_advanced", ["paola", "maura"])

    # Conferma regola super tie-break
    log_message("Regola super tie-break applicata in 'pages/inserisci_risultato.py'.", "success")

    st.markdown("---")
    st.success("🎉 Manutenzione completata.")
    st.write(f"Tempo totale: {(datetime.now() - start_time).seconds} secondi")
    st.balloons()


