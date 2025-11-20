import streamlit as st
from supabase import create_client
from supabase_config import SUPABASE_URL, SUPABASE_KEY  # Importa credenziali dal file
import pandas as pd

# Connessione a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Classifica Tornei")

# Selezione torneo
TORNEI = ["top", "advanced"]
torneo = st.selectbox("Seleziona il torneo", TORNEI)

tabella_classifica = "classifica_top" if torneo == "top" else "classifica_advanced"

# Recupera dati classifica
response = supabase.table(tabella_classifica).select("*").execute()
dati = response.data

if dati:
    # Converti in DataFrame e ordina per punti e vinte
    df = pd.DataFrame(dati)
    if "punti" in df.columns and "vinte" in df.columns:
        df = df.sort_values(by=["punti", "vinte"], ascending=[False, False])

    st.subheader(f"Classifica {torneo.capitalize()}")
    st.dataframe(df)
else:
    st.warning("Nessun dato disponibile per questo torneo.")
