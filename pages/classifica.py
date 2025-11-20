import streamlit as st
from supabase import create_client
import pandas as pd

# Configurazione Supabase
SUPABASE_URL = "YOUR_SUPABASE_URL"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Classifica Torneo Tennis")

# Funzione per ottenere la classifica da Supabase
def get_classifica(tabella):
    response = supabase.table(tabella).select("*").execute()
    data = response.data
    if data:
        df = pd.DataFrame(data)
        df = df.sort_values(by="punti", ascending=False)
        return df
    else:
        return pd.DataFrame()

# Selezione torneo (opzionale)
torneo = st.radio("Seleziona la classifica da visualizzare", ["Top", "Advanced", "Entrambe"])

if torneo == "Top":
    st.subheader("Classifica Top")
    df_top = get_classifica("classifica_top")
    st.table(df_top)
elif torneo == "Advanced":
    st.subheader("Classifica Advanced")
    df_adv = get_classifica("classifica_advanced")
    st.table(df_adv)
else:
    st.subheader("Classifica Top")
    df_top = get_classifica("classifica_top")
    st.table(df_top)

    st.subheader("Classifica Advanced")
    df_adv = get_classifica("classifica_advanced")
    st.table(df_adv)
