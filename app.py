import os
import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import altair as alt

# --- Configurazione Supabase ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY"))

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Variabili Supabase mancanti! Controlla secrets o Environment Variables.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🏆 Torneo Tennis - Gestione Risultati")

# --- Funzione per calcolare punti e tipo vittoria ---
def calcola_punti(set_g1, set_g2):
    if set_g1 == 2 and set_g2 == 0:
        return 3, 0, "2-0"
    elif set_g1 == 2 and set_g2 == 1:
        return 3, 1, "2-1"
    elif set_g2 == 2 and set_g1 == 0:
        return 0, 3, "0-2"
    elif set_g2 == 2 and set_g1 == 1:
        return 1, 3, "1-2"
    else:
        return 0, 0, "ND"

# --- Form inserimento partita ---
st.subheader("➕ Inserisci Nuova Partita")
with st.form("inserimento_partita"):
    giocatori = ["Paolo R.", "Francesco M.", "Daniele T.", "Simone V.", "Leo S.", "Maurizio P.", "Andrea P.", "Gianni F.", "Maura F."]
    giocatore1 = st.selectbox("Giocatore 1", giocatori)
    giocatore2 = st.selectbox("Giocatore 2", giocatori)
    set1 = st.text_input("Set 1 (es. 7-5)")
    set2 = st.text_input("Set 2 (es. 1-6)")
    set3 = st.text_input("Set 3 (opzionale, es. 6-4)")
    submit = st.form_submit_button("Salva Risultato")

if submit:
    if giocatore1 == giocatore2:
        st.error("❌ I due giocatori devono essere diversi!")
    else:
        # Conta set vinti
        set_g1 = 0
        set_g2 = 0
        for s in [set1, set2, set3]:
            if s:
                try:
                    g1_score, g2_score = map(int, s.split("-"))
                    if g1_score > g2_score:
                        set_g1 += 1
                    else:
                        set_g2 += 1
                except:
                    st.error("Formato set non valido! Usa es. 6-4")
                    st.stop()

        punti_g1, punti_g2, tipo_vittoria = calcola_punti(set_g1, set_g2)

        # Salva su Supabase
        supabase.table("partite_completo").insert({
            "giocatore1": giocatore1,
            "giocatore2": giocatore2,
            "set1": set1,
            "set2": set2,
            "set3": set3,
            "punti_g1": punti_g1,
            "punti_g2": punti_g2,
            "tipo_vittoria": tipo_vittoria,
            "created_at": datetime.now().isoformat()
        }).execute()

        st.success("✅ Partita salvata con successo!")

# --- Recupera dati dal DB ---
res = supabase.table("partite_completo").select("*").order("created_at", desc=True).execute()
df = pd.DataFrame(res.data)

if df.empty:
    st.warning("Nessuna partita registrata.")
    st.stop()

# --- Mostra storico ---
st.subheader("📜 Storico Partite")
st.dataframe(df[["giocatore1", "giocatore2", "set1", "set2", "set3", "tipo_vittoria", "punti_g1", "punti_g2", "created_at"]])

# Download CSV storico
csv_storico = df.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Scarica Storico CSV", csv_storico, "storico_partite.csv", "text/csv")

# --- Classifica ---
st.subheader("🏅 Classifica Torneo")

# ✅ Opzione 1: Leggere direttamente dalla tabella classifica (trigger attivo)
try:
    res_classifica = supabase.table("classifica").select("*").order("punti", desc=True).execute()
    df_classifica = pd.DataFrame(res_classifica.data)
except:
    df_classifica = pd.DataFrame()

# ✅ Se la tabella classifica è vuota, calcola dinamicamente
if df_classifica.empty:
    punteggi = pd.concat([
        df[['giocatore1', 'punti_g1']].rename(columns={'giocatore1': 'giocatore', 'punti_g1': 'punti'}),
        df[['giocatore2', 'punti_g2']].rename(columns={'giocatore2': 'giocatore', 'punti_g2': 'punti'})
    ])
    df_classifica = punteggi.groupby('giocatore').sum().sort_values(by='punti', ascending=False).reset_index()

st.dataframe(df_classifica)

# Download CSV classifica
csv_classifica = df_classifica.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Scarica Classifica CSV", csv_classifica, "classifica.csv", "text/csv")

# --- Grafico a barre ---
st.subheader("📊 Grafico Classifica")
chart = alt.Chart(df_classifica).mark_bar().encode(
    x=alt.X('giocatore', sort='-y'),
    y='punti',
    color='giocatore'
).properties(width=600)
st.altair_chart(chart, use_container_width=True)
