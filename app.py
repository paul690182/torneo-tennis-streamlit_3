
import streamlit as st
from supabase_config import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client

# Connessione a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Torneo Tennis - Classifica e Storico")

# Lettura classifica
classifica = supabase.table("classifica").select("*").execute()
if classifica.data:
    st.subheader("Classifica")
    st.table(classifica.data)

# Lettura storico
storico = supabase.table("storico").select("*").execute()
if storico.data:
    st.subheader("Storico Partite")
    st.table(storico.data)
