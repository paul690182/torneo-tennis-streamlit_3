
import streamlit as st
from postgrest import PostgrestClient
from supabase_config import SUPABASE_URL, SUPABASE_KEY

# Connessione a Supabase
client = PostgrestClient(f"{SUPABASE_URL}/rest/v1", headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"})

st.title("Classifica Torneo Tennis")

# Lettura classifica
try:
    classifica = client.from_('classifica').select('*').execute().data
    if classifica:
        st.subheader("Classifica")
        st.table(classifica)
except Exception as e:
    st.error(f"Errore nel recupero della classifica: {e}")

# Lettura storico
try:
    storico = client.from_('storico').select('*').execute().data
    if storico:
        st.subheader("Storico Partite")
        st.table(storico)
except Exception as e:
    st.error(f"Errore nel recupero dello storico: {e}")
