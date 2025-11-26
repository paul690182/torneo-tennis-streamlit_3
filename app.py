import streamlit as st
from supabase import create_client, Client
import traceback
import os
import pandas as pd

# Configurazione Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Torneo Tennis", layout="wide")
st.title("3c6 Torneo Tennis - Gestione Gironi")

# Liste statiche dei giocatori
advanced_players = [
    "Paolo R.", "Francesco M.", "Luca S.", "Andrea C.", "Marco T.", "Gianni P.",
    "Stefano B.", "Alessandro G.", "Roberto L.", "Davide F.", "Giorgio N.", "Simone V.",
    "Claudio Z.", "Fabio E.", "Riccardo D."
]

top_players = [
    "Massimo B.", "Daniele T.", "Giuseppe C.", "Antonio R.", "Mauro S.", "Enrico P.",
    "Carlo G.", "Vincenzo L.", "Salvatore F.", "Alberto M.", "Federico N.", "Gabriele V.",
    "Luigi Z.", "Pietro E."
]

# Funzione per inserire un match

def inserisci_match(table_name, g1, g2, s1g1, s1g2, s2g1, s2g2, s3g1, s3g2):
    try:
        record = {
            "giocatore1": g1,
            "giocatore2": g2,
            "set1_g1": s1g1,
            "set1_g2": s1g2,
            "set2_g1": s2g1,
            "set2_g2": s2g2,
            "set3_g1": s3g1,
            "set3_g2": s3g2
        }
        res = supabase.table(table_name).insert(record).execute()
        st.success(f"Match inserito correttamente in {table_name}!")
    except Exception as e:
        st.error(f"Errore nell'inserimento: {e}")
        st.code(traceback.format_exc())

# Funzione per calcolare la classifica

def calcola_classifica(matches, players):
    punti = {p: 0 for p in players}
    for m in matches:
        g1, g2 = m['giocatore1'], m['giocatore2']
        s1g1, s1g2 = m['set1_g1'], m['set1_g2']
        s2g1, s2g2 = m['set2_g1'], m['set2_g2']
        s3g1, s3g2 = m['set3_g1'], m['set3_g2']

        # Conta set vinti
        sets_g1 = sum([s1g1 > s1g2, s2g1 > s2g2, (s3g1 or 0) > (s3g2 or 0)])
        sets_g2 = sum([s1g2 > s1g1, s2g2 > s2g1, (s3g2 or 0) > (s3g1 or 0)])

        if sets_g1 > sets_g2:
            if sets_g1 == 2 and sets_g2 == 0:
                punti[g1] += 3
            else:
                punti[g1] += 3
                punti[g2] += 1
        elif sets_g2 > sets_g1:
            if sets_g2 == 2 and sets_g1 == 0:
                punti[g2] += 3
            else:
                punti[g2] += 3
                punti[g1] += 1

    df = pd.DataFrame(list(punti.items()), columns=['Giocatore', 'Punti']).sort_values(by='Punti', ascending=False)
    return df

# Funzione diagnostica aggiornata con nomi reali

def diagnostica_tabella(table_name):
    try:
        if table_name == "risultati_advanced":
            probe = {
                "giocatore1": "Paolo R.",
                "giocatore2": "Francesco M.",
                "set1_g1": 6, "set1_g2": 4,
                "set2_g1": 6, "set2_g2": 3,
                "set3_g1": None, "set3_g2": None
            }
        else:
            probe = {
                "giocatore1": "Massimo B.",
                "giocatore2": "Daniele T.",
                "set1_g1": 6, "set1_g2": 2,
                "set2_g1": 6, "set2_g2": 4,
                "set3_g1": None, "set3_g2": None
            }

        read = supabase.table(table_name).select("*").limit(1).execute()
        ins = supabase.table(table_name).insert(probe).execute()
        if ins.data:
            supabase.table(table_name).delete().eq("id", ins.data[0]["id"]).execute()

        return f"✅ {table_name}: Read/Insert/Delete ok"
    except Exception as e:
        return f"❌ {table_name}: {str(e)}"

# Layout con tabs

tab1, tab2, tab3 = st.tabs(["48e Girone Advanced", "3c5 Girone Top", "527 Diagnostica"])

with tab1:
    st.header("Inserisci Match - Girone Advanced")
    g1 = st.selectbox("Giocatore 1", advanced_players)
    g2 = st.selectbox("Giocatore 2", [p for p in advanced_players if p != g1])
    s1g1 = st.number_input("Set1 Giocatore1", min_value=0, max_value=7)
    s1g2 = st.number_input("Set1 Giocatore2", min_value=0, max_value=7)
    s2g1 = st.number_input("Set2 Giocatore1", min_value=0, max_value=7)
    s2g2 = st.number_input("Set2 Giocatore2", min_value=0, max_value=7)
    s3g1 = st.number_input("Set3 Giocatore1", min_value=0, max_value=7)
    s3g2 = st.number_input("Set3 Giocatore2", min_value=0, max_value=7)
    if st.button("Inserisci Match Advanced"):
        inserisci_match("risultati_advanced", g1, g2, s1g1, s1g2, s2g1, s2g2, s3g1, s3g2)

    st.subheader("Storico Match Advanced")
    res = supabase.table("risultati_advanced").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df)

    st.subheader("Classifica Advanced")
    if res.data:
        st.dataframe(calcola_classifica(res.data, advanced_players))

with tab2:
    st.header("Inserisci Match - Girone Top")
    g1 = st.selectbox("Giocatore 1", top_players)
    g2 = st.selectbox("Giocatore 2", [p for p in top_players if p != g1])
    s1g1 = st.number_input("Set1 Giocatore1", min_value=0, max_value=7, key="t1")
    s1g2 = st.number_input("Set1 Giocatore2", min_value=0, max_value=7, key="t2")
    s2g1 = st.number_input("Set2 Giocatore1", min_value=0, max_value=7, key="t3")
    s2g2 = st.number_input("Set2 Giocatore2", min_value=0, max_value=7, key="t4")
    s3g1 = st.number_input("Set3 Giocatore1", min_value=0, max_value=7, key="t5")
    s3g2 = st.number_input("Set3 Giocatore2", min_value=0, max_value=7, key="t6")
    if st.button("Inserisci Match Top"):
        inserisci_match("risultati_top", g1, g2, s1g1, s1g2, s2g1, s2g2, s3g1, s3g2)

    st.subheader("Storico Match Top")
    res_top = supabase.table("risultati_top").select("*").execute()
    if res_top.data:
        df_top = pd.DataFrame(res_top.data)
        st.dataframe(df_top)

    st.subheader("Classifica Top")
    if res_top.data:
        st.dataframe(calcola_classifica(res_top.data, top_players))

with tab3:
    st.header("Diagnostica Connessione Supabase")
    st.write(diagnostica_tabella("risultati_advanced"))
    st.write(diagnostica_tabella("risultati_top"))
