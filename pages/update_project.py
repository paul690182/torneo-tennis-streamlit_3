
import streamlit as st
import requests
import os
from datetime import datetime

# =============================
# CONFIGURAZIONE SUPABASE
# =============================
# Assicurati di impostare queste variabili d'ambiente su Render:
# - SUPABASE_URL (es. https://xxxx.supabase.co)
# - SUPABASE_KEY (meglio service role se devi fare DELETE/PATCH con RLS attive)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    # Preferire la rappresentazione (200) invece del 204, utile per avere feedback coerente
    'Prefer': 'return=representation',
}

# =============================
# FUNZIONI DI SUPPORTO
# =============================
def log_message(msg, level="info"):
    """Stampa messaggi formattati in Streamlit."""
    if level == "success":
        st.markdown(f"✅ **{msg}**")
    elif level == "warning":
        st.markdown(f"⚠️ **{msg}**")
    elif level == "error":
        st.markdown(f"❌ **{msg}**")
    else:
        st.markdown(f"ℹ️ {msg}")

def delete_rows(table_name, columns, names_to_remove, use_ilike=False):
    """
    Cancella righe filtrando per ciascun nome su ciascuna colonna.
    - Se use_ilike=True, usa filtro case-insensitive: ?col=ilike.%nome%
    - Altrimenti usa ?col=eq.nome
    Gestisce 200 e 204 come successi.
    """
    for col in columns:
        for name in names_to_remove:
            operator = f"ilike.%{name}%" if use_ilike else f"eq.{name}"
            url = f"{SUPABASE_URL}/rest/v1/{table_name}?{col}={operator}"
            try:
                response = requests.delete(url, headers=HEADERS)
                if response.status_code in (200, 204):
                    log_message(
                        f"Cancellate righe da '{table_name}' usando colonna '{col}' "
                        f"({'ilike' if use_ilike else 'eq'}) = '{name}'.",
                        "success",
                    )
                else:
                    log_message(
                        f"Errore cancellando da '{table_name}' con colonna '{col}': "
                        f"{response.status_code} - {response.text}",
                        "error",
                    )
            except Exception as e:
                log_message(f"Eccezione durante DELETE su '{table_name}': {e}", "error")

def get_columns(table_name):
    """
    Prova a ottenere le colonne campionando una riga.
    Se la tabella è vuota o non leggibile, ritorna [].
    """
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit=1"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                return list(data[0].keys())
        return []
    except Exception:
        return []

def nullify_columns(table_name, pivot_cols):
    """
    Imposta a NULL le colonne pivot se esistono nella tabella.
    Se non ci sono, mostra un avviso (non blocca il flusso).
    """
    columns = get_columns(table_name)
    matched = [c for c in columns if c in pivot_cols]
    if not matched:
        log_message(
            f"Nessuna colonna pivot trovata in '{table_name}'. Colonne presenti: {columns}",
            "warning",
        )
        return
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    payload = {col: None for col in matched}
    try:
        response = requests.patch(url, headers=HEADERS, json=payload)
        if response.status_code in (200, 204):
            log_message(
                f"Azzerate/NULL le colonne {matched} su tutte le righe di '{table_name}'.",
                "success",
            )
        else:
            log_message(
                f"Errore azzerando colonne in '{table_name}': {response.status_code} - {response.text}",
                "error",
            )
    except Exception as e:
        log_message(f"Eccezione durante PATCH su '{table_name}': {e}", "error")

# =============================
# INTERFACCIA STREAMLIT
# =============================
st.title("🔧 Manutenzione progetto")
st.write("Questa pagina rimuove giocatori specifici dalle tabelle e conferma la validazione del 3° set.")

st.markdown("---")
st.subheader("⚙️ Impostazioni")

# Opzione per usare il filtro case-insensitive
use_ilike = st.checkbox("Usa filtro 'ilike' (case-insensitive, rimuove chi contiene il nome)", value=True)

# Nomi da rimuovere (di default Paola C., Maura F.)
default_names = "Paola C., Maura F."
names_input = st.text_input("Nomi da rimuovere (separati da virgola)", value=default_names, help="Esempio: Paola C., Maura F.")
names_to_remove = [n.strip() for n in names_input.split(",") if n.strip()]

st.markdown("---")
st.subheader("📋 Avanzamento")

if st.button("Esegui manutenzione"):
    start_time = datetime.now()

    # 1) classifica_advanced (colonna 'giocatore')
    delete_rows("classifica_advanced", ["giocatore"], names_to_remove, use_ilike=use_ilike)

    # 2) risultati_advanced (colonne 'giocatore1', 'giocatore2')
    delete_rows("risultati_advanced", ["giocatore1", "giocatore2"], names_to_remove, use_ilike=use_ilike)

    # 3) partite_advanced (colonne 'giocatore1', 'giocatore2')
    delete_rows("partite_advanced", ["giocatore1", "giocatore2"], names_to_remove, use_ilike=use_ilike)

    # 4) Azzeramento colonne pivot (se presenti)
    # Se avessi uno schema pivot (es. colonne 'paola', 'maura'), verranno messe a NULL.
    nullify_columns("partite_advanced", ["paola", "maura"])

    # Conferma regola super tie-break (super tie-break lungo: min 8, scarto >=2, max 20 per vincitore)
    log_message("Regola super tie-break applicata in 'pages/inserisci_risultato.py'.", "success")

    st.markdown("---")
    st.success("🎉 Manutenzione completata.")
    st.write(f"Tempo totale: {(datetime.now() - start_time).seconds} secondi")
    st.balloons()

