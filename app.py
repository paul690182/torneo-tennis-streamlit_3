
import os
import traceback
import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ===== Configurazione =====
APP_VERSION = "v2025-11-26-23:59 (tie-break max 20 + sidebar nascosta)"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None

# ===== Sidebar nascosta =====
st.set_page_config(page_title="Torneo Tennis", layout="wide", initial_sidebar_state="collapsed")
st.title("🎾 Torneo Tennis - Gestione Gironi")
st.caption(f"Build: {APP_VERSION}")

# ===== Liste giocatori =====
ADVANCED_PLAYERS_STATIC = [
    "Paolo R.", "Francesco M.", "Simone V.", "Gianni F.", "Leo S.",
    "Giovanni D.", "Andrea P.", "Maurizio P.", "Massimo B.", "Daniele T."
]
TOP_PLAYERS_STATIC = [
    "Massimo B.", "Daniele T.", "Paolo R.", "Francesco M.", "Simone V.",
    "Gianni F.", "Leo S.", "Giovanni D.", "Andrea P.", "Maurizio P."
]

def parse_env_players(key: str):
    raw = os.getenv(key, "").strip()
    if not raw:
        return []
    return [p.strip() for p in raw.split(",") if p.strip()]

@st.cache_data(show_spinner=False)
def get_players(group: str):
    if group == "advanced":
        env = parse_env_players("ADV_PLAYERS")
        return env if env else ADVANCED_PLAYERS_STATIC
    else:
        env = parse_env_players("TOP_PLAYERS")
        return env if env else TOP_PLAYERS_STATIC

# ===== Funzioni =====

def inserisci_match(table_name, g1, g2, s1g1, s1g2, s2g1, s2g2, s3g1, s3g2):
    try:
        if g1 == g2:
            st.error("I due giocatori devono essere diversi.")
            return
        for v in [s1g1, s1g2, s2g1, s2g2]:
            if v is None or v < 0 or v > 7:
                st.error("I punteggi dei set 1 e 2 devono essere tra 0 e 7.")
                return
        if s3g1 not in (None,) and (s3g1 < 0 or s3g1 > 20):
            st.error("Il punteggio del set 3 deve essere tra 0 e 20 o vuoto.")
            return
        if s3g2 not in (None,) and (s3g2 < 0 or s3g2 > 20):
            st.error("Il punteggio del set 3 deve essere tra 0 e 20 o vuoto.")
            return
        record = {
            "giocatore1": g1,
            "giocatore2": g2,
            "set1_g1": int(s1g1),
            "set1_g2": int(s1g2),
            "set2_g1": int(s2g1),
            "set2_g2": int(s2g2),
            "set3_g1": None if s3g1 in (None, "") else int(s3g1),
            "set3_g2": None if s3g2 in (None, "") else int(s3g2)
        }
        if supabase is None:
            st.error("Supabase non configurato: controlla SUPABASE_URL e SUPABASE_KEY.")
            return
        supabase.table(table_name).insert(record).execute()
        st.success(f"Match inserito in {table_name}!")
    except Exception as e:
        st.error(f"Errore nell'inserimento: {e}")
        st.code(traceback.format_exc())

def calcola_classifica(matches, players):
    punti = {p: 0 for p in players}
    for m in matches:
        g1, g2 = m.get('giocatore1'), m.get('giocatore2')
        s1g1, s1g2 = m.get('set1_g1'), m.get('set1_g2')
        s2g1, s2g2 = m.get('set2_g1'), m.get('set2_g2')
        s3g1, s3g2 = m.get('set3_g1'), m.get('set3_g2')
        sets_g1 = int((s1g1 or 0) > (s1g2 or 0)) + int((s2g1 or 0) > (s2g2 or 0)) + int((s3g1 or 0) > (s3g2 or 0))
        sets_g2 = int((s1g2 or 0) > (s1g1 or 0)) + int((s2g2 or 0) > (s2g1 or 0)) + int((s3g2 or 0) > (s3g1 or 0))
        if g1 not in punti or g2 not in punti:
            continue
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
    df = pd.DataFrame({"Giocatore": list(punti.keys()), "Punti": list(punti.values())})
    df = df.sort_values(by="Punti", ascending=False).reset_index(drop=True)
    return df

def diagnostica_tabella(table_name):
    try:
        if supabase is None:
            return f"❌ {table_name}: Supabase non configurato."
        p = get_players("advanced" if table_name == "risultati_advanced" else "top")
        probe = {
            "giocatore1": p[0],
            "giocatore2": p[1],
            "set1_g1": 6, "set1_g2": 4,
            "set2_g1": 6, "set2_g2": 3,
            "set3_g1": None, "set3_g2": None
        }
        _ = supabase.table(table_name).select("*").limit(1).execute()
        ins = supabase.table(table_name).insert(probe).execute()
        if ins.data:
            supabase.table(table_name).delete().eq("id", ins.data[0]["id"]).execute()
        return f"✅ {table_name}: Read/Insert/Delete ok"
    except Exception as e:
        return f"❌ {table_name}: {str(e)}"

# ===== Layout Tabs =====
TAB_ADV, TAB_TOP, TAB_DIAG = st.tabs(["💎 Girone Advanced", "🏅 Girone Top", "🔧 Diagnostica"]) 

with TAB_ADV:
    st.subheader("Dati del Match - Advanced")
    adv_players = get_players("advanced")
    g1 = st.selectbox("Giocatore 1", adv_players, key="adv_g1")
    g2 = st.selectbox("Giocatore 2", [p for p in adv_players if p != g1], key="adv_g2")
    c1, c2, c3 = st.columns(3)
    with c1:
        s1g1 = st.number_input("Set1 G1", min_value=0, max_value=7, step=1, key="adv_s1g1")
        s2g1 = st.number_input("Set2 G1", min_value=0, max_value=7, step=1, key="adv_s2g1")
        s3g1 = st.number_input("Set3 G1 (opzionale)", min_value=0, max_value=20, step=1, key="adv_s3g1")
    with c2:
        s1g2 = st.number_input("Set1 G2", min_value=0, max_value=7, step=1, key="adv_s1g2")
        s2g2 = st.number_input("Set2 G2", min_value=0, max_value=7, step=1, key="adv_s2g2")
        s3g2 = st.number_input("Set3 G2 (opzionale)", min_value=0, max_value=20, step=1, key="adv_s3g2")
    with c3:
        if st.button("Salva risultato Advanced", type="primary"):
            inserisci_match("risultati_advanced", g1, g2, s1g1, s1g2, s2g1, s2g2, s3g1, s3g2)
    st.markdown("---")
    st.subheader("Storico Advanced")
    if supabase is not None:
        res = supabase.table("risultati_advanced").select("*").order("created_at", desc=True).execute()
        df = pd.DataFrame(res.data or [])
        st.dataframe(df if not df.empty else pd.DataFrame(columns=["Nessun risultato inserito"]))
    st.subheader("Classifica Advanced")
    if supabase is not None:
        res = supabase.table("risultati_advanced").select("*").execute()
        st.dataframe(calcola_classifica(res.data or [], adv_players))

with TAB_TOP:
    st.subheader("Dati del Match - Top")
    top_players = get_players("top")
    tg1 = st.selectbox("Giocatore 1", top_players, key="top_g1")
    tg2 = st.selectbox("Giocatore 2", [p for p in top_players if p != tg1], key="top_g2")
    c1, c2, c3 = st.columns(3)
    with c1:
        ts1g1 = st.number_input("Set1 G1", min_value=0, max_value=7, step=1, key="top_s1g1")
        ts2g1 = st.number_input("Set2 G1", min_value=0, max_value=7, step=1, key="top_s2g1")
        ts3g1 = st.number_input("Set3 G1 (opzionale)", min_value=0, max_value=20, step=1, key="top_s3g1")
    with c2:
        ts1g2 = st.number_input("Set1 G2", min_value=0, max_value=7, step=1, key="top_s1g2")
        ts2g2 = st.number_input("Set2 G2", min_value=0, max_value=7, step=1, key="top_s2g2")
        ts3g2 = st.number_input("Set3 G2 (opzionale)", min_value=0, max_value=20, step=1, key="top_s3g2")
    with c3:
        if st.button("Salva risultato Top", type="primary"):
            inserisci_match("risultati_top", tg1, tg2, ts1g1, ts1g2, ts2g1, ts2g2, ts3g1, ts3g2)
    st.markdown("---")
    st.subheader("Storico Top")
    if supabase is not None:
        res_top = supabase.table("risultati_top").select("*").order("created_at", desc=True).execute()
        df_top = pd.DataFrame(res_top.data or [])
        st.dataframe(df_top if not df_top.empty else pd.DataFrame(columns=["Nessun risultato inserito"]))
    st.subheader("Classifica Top")
    if supabase is not None:
        res_top = supabase.table("risultati_top").select("*").execute()
        st.dataframe(calcola_classifica(res_top.data or [], top_players))

with TAB_DIAG:
    st.subheader("Diagnostica Connessione Supabase")
    st.write(diagnostica_tabella("risultati_advanced"))
    st.write(diagnostica_tabella("risultati_top"))

