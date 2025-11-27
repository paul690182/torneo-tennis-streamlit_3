
import os
import traceback
import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ===== Configurazione =====
APP_VERSION = "v2025-11-27 (sidebar rimossa + tabs + classifica dinamica)"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None

# ===== Nascondi Sidebar =====
st.set_page_config(page_title="Torneo Tennis", layout="wide")
HIDE_SIDEBAR = """
<style>
[data-testid="stSidebar"] {display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
section[data-testid="stSidebar"] {display: none !important;}
</style>
"""
st.markdown(HIDE_SIDEBAR, unsafe_allow_html=True)

# ===== Titolo =====
st.title("🎾 Torneo Tennis - Gestione Gironi")
st.caption(f"Build: {APP_VERSION}")

# ===== Liste giocatori =====
TOP_PLAYERS = [
    "Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo", "Cris Cosso",
    "Giovanni", "Andrea P.", "Giuseppe", "Salvatore", "Leonardino",
    "Federico", "Luca", "Adriano"
]
ADVANCED_PLAYERS = [
    "Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.", "Roberto A.",
    "Susanna", "Paolo Mattioli", "Paolo Rosi", "Michele", "Daniele M.",
    "Stefano D. R.", "Pino", "Gianni", "Leonardo", "Francesco M."
]

# ===== Funzioni =====
def compute_match_points(sets_p1, sets_p2):
    """Calcola punti secondo logica 3-2-1-0"""
    if sets_p1 == 2 and sets_p2 == 0:
        return 3, 0
    if sets_p1 == 0 and sets_p2 == 2:
        return 0, 3
    if sets_p1 == 2 and sets_p2 == 1:
        return 2, 1
    if sets_p1 == 1 and sets_p2 == 2:
        return 1, 2
    return 0, 0

def sets_won_from_scores(scores):
    """Determina set vinti da punteggi"""
    sets_p1 = 0
    sets_p2 = 0
    for p1, p2 in scores:
        if p1 is not None and p2 is not None:
            if p1 > p2:
                sets_p1 += 1
            elif p2 > p1:
                sets_p2 += 1
    return sets_p1, sets_p2

def inserisci_match(table_name, g1, g2, s1g1, s1g2, s2g1, s2g2, s3g1, s3g2):
    try:
        if g1 == g2:
            st.error("I due giocatori devono essere diversi.")
            return
        # Validazione punteggi
        for v in [s1g1, s1g2, s2g1, s2g2]:
            if v < 0 or v > 7:
                st.error("Set 1 e 2 devono essere tra 0 e 7.")
                return
        if s3g1 and (s3g1 < 0 or s3g1 > 20):
            st.error("Set 3 deve essere tra 0 e 20.")
            return
        if s3g2 and (s3g2 < 0 or s3g2 > 20):
            st.error("Set 3 deve essere tra 0 e 20.")
            return

        # Calcolo set e punti
        sets_p1, sets_p2 = sets_won_from_scores([(s1g1, s1g2), (s2g1, s2g2), (s3g1, s3g2)])
        points_p1, points_p2 = compute_match_points(sets_p1, sets_p2)

        record = {
            "giocatore1": g1,
            "giocatore2": g2,
            "set1_g1": s1g1, "set1_g2": s1g2,
            "set2_g1": s2g1, "set2_g2": s2g2,
            "set3_g1": s3g1 if s3g1 else None,
            "set3_g2": s3g2 if s3g2 else None,
            "sets_g1": sets_p1, "sets_g2": sets_p2,
            "points_g1": points_p1, "points_g2": points_p2
        }

        if supabase is None:
            st.error("Supabase non configurato.")
            return

        supabase.table(table_name).insert(record).execute()
        st.success(f"Match inserito in {table_name}! Punti: {g1}={points_p1}, {g2}={points_p2}")
        st.experimental_rerun()  # Aggiorna classifica
    except Exception as e:
        st.error(f"Errore: {e}")
        st.code(traceback.format_exc())

def calcola_classifica(matches, players):
    punti = {p: 0 for p in players}
    sets_vinti = {p: 0 for p in players}
    sets_persi = {p: 0 for p in players}
    games_vinti = {p: 0 for p in players}

    for m in matches:
        g1, g2 = m['giocatore1'], m['giocatore2']
        punti[g1] += m.get('points_g1', 0)
        punti[g2] += m.get('points_g2', 0)
        sets_vinti[g1] += m.get('sets_g1', 0)
        sets_vinti[g2] += m.get('sets_g2', 0)
        sets_persi[g1] += m.get('sets_g2', 0)
        sets_persi[g2] += m.get('sets_g1', 0)
        games_vinti[g1] += sum([m.get('set1_g1', 0), m.get('set2_g1', 0), m.get('set3_g1', 0) or 0])
        games_vinti[g2] += sum([m.get('set1_g2', 0), m.get('set2_g2', 0), m.get('set3_g2', 0) or 0])

    df = pd.DataFrame({
        "Giocatore": players,
        "Punti": [punti[p] for p in players],
        "Set vinti": [sets_vinti[p] for p in players],
        "Set persi": [sets_persi[p] for p in players],
        "Diff set": [sets_vinti[p] - sets_persi[p] for p in players],
        "Game vinti": [games_vinti[p] for p in players]
    })
    df.sort_values(by=["Punti", "Diff set", "Game vinti"], ascending=[False, False, False], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.insert(0, "Posizione", df.index + 1)
    return df

# ===== Layout Tabs =====
TAB_ADV, TAB_TOP, TAB_DIAG = st.tabs(["💎 Girone Advanced", "🏅 Girone Top", "🔧 Diagnostica"])

with TAB_ADV:
    st.subheader("Inserisci risultato - Advanced")
    g1 = st.selectbox("Giocatore 1", ADVANCED_PLAYERS, key="adv_g1")
    g2 = st.selectbox("Giocatore 2", [p for p in ADVANCED_PLAYERS if p != g1], key="adv_g2")
    c1, c2, c3 = st.columns(3)
    with c1:
        s1g1 = st.number_input("Set1 G1", 0, 7, 6)
        s2g1 = st.number_input("Set2 G1", 0, 7, 6)
        s3g1 = st.number_input("Set3 G1 (TB)", 0, 20, 0)
    with c2:
        s1g2 = st.number_input("Set1 G2", 0, 7, 4)
        s2g2 = st.number_input("Set2 G2", 0, 7, 4)
        s3g2 = st.number_input("Set3 G2 (TB)", 0, 20, 0)
    with c3:
        if st.button("Salva risultato Advanced", type="primary"):
            inserisci_match("risultati_advanced", g1, g2, s1g1, s1g2, s2g1, s2g2, s3g1, s3g2)

    st.markdown("---")
    st.subheader("Classifica Advanced")
    if supabase:
        res = supabase.table("risultati_advanced").select("*").execute()
        st.dataframe(calcola_classifica(res.data or [], ADVANCED_PLAYERS), use_container_width=True)

with TAB_TOP:
    st.subheader("Inserisci risultato - Top")
    tg1 = st.selectbox("Giocatore 1", TOP_PLAYERS, key="top_g1")
    tg2 = st.selectbox("Giocatore 2", [p for p in TOP_PLAYERS if p != tg1], key="top_g2")
    c1, c2, c3 = st.columns(3)
    with c1:
        ts1g1 = st.number_input("Set1 G1", 0, 7, 6)
        ts2g1 = st.number_input("Set2 G1", 0, 7, 6)
        ts3g1 = st.number_input("Set3 G1 (TB)", 0, 20, 0)
    with c2:
        ts1g2 = st.number_input("Set1 G2", 0, 7, 4)
        ts2g2 = st.number_input("Set2 G2", 0, 7, 4)
        ts3g2 = st.number_input("Set3 G2 (TB)", 0, 20, 0)
    with c3:
        if st.button("Salva risultato Top", type="primary"):
            inserisci_match("risultati_top", tg1, tg2, ts1g1, ts1g2, ts2g1, ts2g2, ts3g1, ts3g2)

    st.markdown("---")
    st.subheader("Classifica Top")
    if supabase:
        res_top = supabase.table("risultati_top").select("*").execute()
        st.dataframe(calcola_classifica(res_top.data or [], TOP_PLAYERS), use_container_width=True)

with TAB_DIAG:
    st.subheader("Diagnostica Supabase")
    st.write("Advanced:", "OK" if supabase else "❌")
    st.write("Top:", "OK" if supabase else "❌")

