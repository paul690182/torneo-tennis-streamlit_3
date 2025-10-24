
import streamlit as st
import psycopg2
import os

st.set_page_config(page_title="Torneo Tennis", layout="wide")

st.sidebar.title("🔧 Debug & Configurazione")

# Mostra variabili d'ambiente utili
st.sidebar.subheader("Variabili d'ambiente")
db_url = os.environ.get("SUPABASE_DB_URL", "❌ Non trovata")
st.sidebar.text(f"SUPABASE_DB_URL:
{db_url}")

# Connessione al database PostgreSQL (Supabase)
conn = None
try:
    if db_url == "❌ Non trovata":
        raise ValueError("Variabile SUPABASE_DB_URL non impostata")

    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    st.sidebar.success("✅ Connessione a Supabase riuscita")

except Exception as e:
    st.sidebar.error("❌ Errore nella connessione a Supabase")
    st.sidebar.code(str(e))

# Esempio di utilizzo del database (solo se connessione riuscita)
if conn:
    st.title("🎾 Torneo Tennis - Tutti contro tutti")
    st.write("Qui puoi visualizzare la classifica e inserire i risultati.")
    # ... qui va il resto della tua logica per visualizzare e aggiornare i dati ...
else:
    st.warning("Connessione al database non disponibile. Controlla le impostazioni.")
