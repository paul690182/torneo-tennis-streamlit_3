
# -*- coding: utf-8 -*-
"""
App Streamlit: Torneo Tennis tutti contro tutti
- Sidebar: selettore Girone (Top / Advanced)
- Form: dropdown con i giocatori del girone selezionato
- Inserimento partita: salva su Supabase
- Classifica: aggiornata subito con la logica punteggi
- Supporto long tie-break (super tie-break a 10 punti) nel 3° set

NOTE:
- Compila .env con SUPABASE_URL e SUPABASE_ANON_KEY
- Schema Supabase consigliato:
  * Tabella: matches
    - id: bigint (PK)
    - created_at: timestamptz default now()
    - girone: text ("Top" | "Advanced")
    - player1: text
    - player2: text
    - set1_p1: int
    - set1_p2: int
    - set2_p1: int
    - set2_p2: int
    - set3_p1: int null
    - set3_p2: int null
    - is_super_tb: bool default false
    - winner: text
    - points_p1: int
    - points_p2: int
"""

import os
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# --- Config UI ---
st.set_page_config(page_title="Torneo Tennis", page_icon="🎾", layout="centered")

# --- Players per girone (conservati) ---
PLAYERS = {
    "Top": [
        "Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo", "Cris Cosso",
        "Giovanni", "Andrea P.", "Giuseppe", "Salvatore", "Leonardino", "Federico",
        "Luca", "Adriano"
    ],
    "Advanced": [
        "Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.", "Roberto A.", "Susanna",
        "Paolo Mattioli", "Paolo Rosi", "Michele", "Daniele M.", "Stefano D. R.", "Pino",
        "Gianni", "Leonardo", "Francesco M."
    ],
}

# --- Punteggi ---
# Regola punti torneo (best-of-3 set):
# 2-0 -> 3 punti al vincitore, 0 allo sconfitto
# 2-1 -> 3 al vincitore, 1 allo sconfitto

def compute_points(sets_p1: int, sets_p2: int) -> tuple[int, int]:
    # 2-0 -> 3 punti al vincitore, 0 allo sconfitto
    if sets_p1 == 2 and sets_p2 == 0:
        return 3, 0
    if sets_p2 == 2 and sets_p1 == 0:
        return 0, 3

    # 2-1 -> 2 punti al vincitore, 1 allo sconfitto
    if sets_p1 == 2 and sets_p2 == 1:
        return 2, 1
    if sets_p2 == 2 and sets_p1 == 1:
        return 1, 2

    # Non dovrebbero esistere pareggi in best-of-3
    return 0, 0

# --- Supabase client ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except Exception as e:
        st.sidebar.error(f"Supabase non configurato correttamente: {e}")

# --- Sidebar: selettore girone ---
st.sidebar.header("Impostazioni")
girone = st.sidebar.selectbox("Girone", options=list(PLAYERS.keys()))
players = PLAYERS[girone]

st.title("🎾 Torneo Tennis — Inserimento & Classifica")
st.caption("Girone selezionato: **%s**" % girone)

# --- Form: inserimento partita ---
st.subheader("Inserisci una partita")
with st.form("match_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        p1 = st.selectbox("Giocatore 1", players, index=0)
    with col2:
        p2 = st.selectbox("Giocatore 2", players, index=1)

    st.markdown("**Punteggi set** *(inserisci i game vinti nei set 1 e 2; il 3° set può essere un super tie-break a 10)*")

    # Checkbox per super tie-break (long tie-break) nel 3° set
    is_super_tb = st.checkbox("Long tie-break nel 3° set (a 10 punti)", value=True,
                              help="Se attivo, il 3° set viene deciso con un super tie-break a 10 punti (chi arriva prima a 10 con 2 punti di scarto).")

    c1, c2 = st.columns(2)
    with c1:
        set1_p1 = st.number_input("Set 1 - P1 (game)", min_value=0, max_value=7, value=6)
        set2_p1 = st.number_input("Set 2 - P1 (game)", min_value=0, max_value=7, value=6)
        # max per set 3 dipende dal super tie-break
        max_set3 = 15 if is_super_tb else 7
        set3_p1 = st.number_input("Set 3 - P1 (game o punti TB)", min_value=0, max_value=max_set3, value=0)
    with c2:
        set1_p2 = st.number_input("Set 1 - P2 (game)", min_value=0, max_value=7, value=4)
        set2_p2 = st.number_input("Set 2 - P2 (game)", min_value=0, max_value=7, value=4)
        set3_p2 = st.number_input("Set 3 - P2 (game o punti TB)", min_value=0, max_value=max_set3, value=0)

    submitted = st.form_submit_button("Salva partita su Supabase")

    if submitted:
        # Validazioni base
        if p1 == p2:
            st.error("I due giocatori devono essere diversi.")
        else:
            # Calcolo set vinti per i primi due set
            set1_w_p1 = int(set1_p1 > set1_p2)
            set1_w_p2 = int(set1_p2 > set1_p1)
            set2_w_p1 = int(set2_p1 > set2_p2)
            set2_w_p2 = int(set2_p2 > set2_p1)

            sets_p1 = set1_w_p1 + set2_w_p1
            sets_p2 = set1_w_p2 + set2_w_p2

            # Se è 1-1 dopo due set, il 3° set è obbligatorio
            third_played = (set3_p1 > 0 or set3_p2 > 0)
            if sets_p1 == 1 and sets_p2 == 1 and not third_played:
                st.error("Con 1–1 dopo due set, devi inserire il 3° set (super tie-break o set normale).")
            else:
                # Valutazione 3° set (se giocato)
                if third_played:
                    # Nel super tie-break vince chi ha più punti (tipicamente a 10)
                    set3_w_p1 = int(set3_p1 > set3_p2)
                    set3_w_p2 = int(set3_p2 > set3_p1)
                    sets_p1 += set3_w_p1
                    sets_p2 += set3_w_p2

                # Nessun pareggio ammesso in best-of-3
                if sets_p1 == sets_p2:
                    st.error("Best-of-3 non consente pareggi: controlla i punteggi dei set.")
                else:
                    pnts_p1, pnts_p2 = compute_points(sets_p1, sets_p2)
                    winner = p1 if sets_p1 > sets_p2 else p2

                    payload = {
                        "created_at": datetime.utcnow().isoformat(),
                        "girone": girone,
                        "player1": p1,
                        "player2": p2,
                        "set1_p1": int(set1_p1),
                        "set1_p2": int(set1_p2),
                        "set2_p1": int(set2_p1),
                        "set2_p2": int(set2_p2),
                        "set3_p1": int(set3_p1),
                        "set3_p2": int(set3_p2),
                        "is_super_tb": bool(is_super_tb),
                        "winner": winner,
                        "points_p1": pnts_p1,
                        "points_p2": pnts_p2,
                    }

                    if supabase:
                        try:
                            res = supabase.table("matches").insert(payload).execute()
                            st.success("Partita salvata! ✅")
                            # Riepilogo compatto
                            def fmt_set(a, b):
                                return f"{a}-{b}"
                            set3_label = " (TB10)" if is_super_tb and third_played else ""
                            st.info(
                                f"**{p1} vs {p2}** — "
                                f"{fmt_set(set1_p1, set1_p2)}, {fmt_set(set2_p1, set2_p2)}"
                                + (f", {fmt_set(set3_p1, set3_p2)}{set3_label}" if third_played else "")
                                + f" — **Vincitore:** {winner} — **Punti:** {pnts_p1}-{pnts_p2}"
                            )
                        except Exception as e:
                            st.error(f"Errore salvataggio su Supabase: {e}")
                    else:
                        st.warning("Supabase non configurato: la partita non è stata salvata. Configura .env e ricarica l'app.")

# --- Classifica ---
st.subheader("Classifica aggiornata")

matches_df = pd.DataFrame()
if supabase:
    try:
        data = supabase.table("matches").select("*").eq("girone", girone).execute()
        rows = data.data if hasattr(data, 'data') else []
        matches_df = pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Errore lettura matches: {e}")

if matches_df.empty:
    st.info("Nessuna partita presente per questo girone.")
else:
    # Calcolo classifica: punti cumulati, partite giocate, vittorie
    def row_points(r):
        return {
            r["player1"]: r.get("points_p1", 0),
            r["player2"]: r.get("points_p2", 0),
        }

    points = {}
    wins = {}
    played = {}

    for _, r in matches_df.iterrows():
        for pl, pts in row_points(r).items():
            points[pl] = points.get(pl, 0) + int(pts)
            played[pl] = played.get(pl, 0) + 1
        w = r.get("winner")
        if w and w not in (None, "", "Pareggio"):
            wins[w] = wins.get(w, 0) + 1

    # Costruisci dataframe classifica con tutti i giocatori del girone (anche senza partite)
    rows = []
    for pl in players:
        rows.append({
            "Giocatore": pl,
            "Punti": points.get(pl, 0),
            "Giocate": played.get(pl, 0),
            "Vittorie": wins.get(pl, 0),
        })
    standings_df = pd.DataFrame(rows).sort_values(["Punti", "Vittorie"], ascending=[False, False]).reset_index(drop=True)

    st.dataframe(standings_df, use_container_width=True)

st.divider()
st.markdown("ℹ️ Il 3° set può essere giocato come **super tie-break a 10 punti**. L’app assegna il set al giocatore con più punti nel TB10.")

