
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

# --- Lettura classifica dalle VIEW del DB ---

import pandas as pd

# --- Lettura classifica dalle VIEW del DB (solo Supabase client) ---
def read_classifica_from_views(supabase, girone: str) -> pd.DataFrame:
    if not supabase:
        st.error("Supabase non configurato: controlla SUPABASE_URL e SUPABASE_ANON_KEY.")
        return pd.DataFrame()

    view_name = "classifica_top" if girone == "Top" else "classifica_advanced"
    try:
        resp = supabase.table(view_name).select("*")\
            .order("punti", desc=True).order("nome").execute()
        return pd.DataFrame(resp.data or [])
    except Exception as e:
        st.error(f"Errore nel leggere la classifica ({view_name}) via Supabase: {e}")
        return pd.DataFrame()

# Leggi la classifica del girone selezionato
df_classifica = read_classifica_from_views(supabase, girone)

 

# ✅ Svuota la cache appena entri nella sezione (temporaneo, utile oggi per pulire i dati vecchi)
import streamlit as st
st.cache_data.clear()




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
        st.stop()
    else:
        # --- Validazioni numeriche sui set ---
        try:
            set1_p1, set1_p2 = int(set1_p1), int(set1_p2)
            set2_p1, set2_p2 = int(set2_p1), int(set2_p2)
            # Terzo set: se vuoto/None, salviamo 0
            s3p1_to_save = int(set3_p1) if str(set3_p1).strip() not in ("", "None") else 0
            s3p2_to_save = int(set3_p2) if str(set3_p2).strip() not in ("", "None") else 0
        except ValueError:
            st.error("I punteggi dei set devono essere numeri interi.")
            st.stop()

        # --- Calcolo set vinti dopo i primi due set ---
        set1_w_p1 = 1 if set1_p1 > set1_p2 else 0
        set1_w_p2 = 1 if set1_p2 > set1_p1 else 0
        set2_w_p1 = 1 if set2_p1 > set2_p2 else 0
        set2_w_p2 = 1 if set2_p2 > set2_p1 else 0

        sets_p1 = set1_w_p1 + set2_w_p1
        sets_p2 = set1_w_p2 + set2_w_p2

        # --- Con 1–1 dopo due set, serve il 3° set / super tie-break ---
        third_played = (s3p1_to_save > 0 or s3p2_to_save > 0)
        if sets_p1 == 1 and sets_p2 == 1 and not third_played:
            st.error("Con 1–1 dopo due set, devi inserire il 3° set (o il super tie-break).")
            st.stop()

        # --- Se è stato giocato il 3° set/super TB, aggiorna i set vinti ---
        if third_played:
            set3_w_p1 = 1 if s3p1_to_save > s3p2_to_save else 0
            set3_w_p2 = 1 if s3p2_to_save > s3p1_to_save else 0
            sets_p1 += set3_w_p1
            sets_p2 += set3_w_p2

        # --- Determina winner e punti 3–1–0 ---
        if sets_p1 > sets_p2:
            winner = p1
            points_p1, points_p2 = (3, 0) if (sets_p1 == 2 and sets_p2 == 0) else (3, 1)
        else:
            winner = p2
            points_p1, points_p2 = (1, 3) if (sets_p1 == 1 and sets_p2 == 2) else (0, 3)

        # --- Salvataggio su Supabase ---
        try:
            data = {
                "girone": girone_selezionato,   # oppure "Top" se non usi la variabile
                "player1": p1,
                "player2": p2,
                "set1_p1": set1_p1, "set1_p2": set1_p2,
                "set2_p1": set2_p1, "set2_p2": set2_p2,
                "set3_p1": s3p1_to_save, "set3_p2": s3p2_to_save,
                "is_super_tb": bool(is_super_tb),
                "winner": winner,               # nome reale del vincitore (p1/p2)
                "points_p1": points_p1, "points_p2": points_p2,
            }

            res = supabase.table("matches").insert(data).execute()
            st.success("Partita salvata su Supabase! ✅")

            # Aggiorna subito la UI
            try:
                st.cache_data.clear()
            except Exception:
                pass
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()

        except Exception as e:
            st.error(f"Errore durante il salvataggio su Supabase: {e}")




        # --- Calcolo set vinti dopo i primi due set ---
        set1_w_p1 = 1 if set1_p1 > set1_p2 else 0
        set1_w_p2 = 1 if set1_p2 > set1_p1 else 0
        set2_w_p1 = 1 if set2_p1 > set2_p2 else 0
        set2_w_p2 = 1 if set2_p2 > set2_p1 else 0

        sets_p1 = set1_w_p1 + set2_w_p1
        sets_p2 = set1_w_p2 + set2_w_p2

        # --- Con 1–1 dopo due set, serve il 3° set / super tie-break ---
        third_played = (s3p1_to_save > 0 or s3p2_to_save > 0)
        if sets_p1 == 1 and sets_p2 == 1 and not third_played:
            st.error("Con 1–1 dopo due set, devi inserire il 3° set (o il super tie-break).")
            st.stop()

        # --- Se è stato giocato il 3° set/super TB, aggiorna i set vinti ---
        if third_played:
            # nel super tie-break vince chi ha più punti; nel set normale idem
            set3_w_p1 = 1 if s3p1_to_save > s3p2_to_save else 0
            set3_w_p2 = 1 if s3p2_to_save > s3p1_to_save else 0
            sets_p1 += set3_w_p1
            sets_p2 += set3_w_p2

        # --- Determina winner e punti 3–1–0 ---
        if sets_p1 > sets_p2:
            winner = p1
            points_p1, points_p2 = (3, 0) if (sets_p1 == 2 and sets_p2 == 0) else (3, 1)
        else:
            winner = p2
            points_p1, points_p2 = (1, 3) if (sets_p1 == 1 and sets_p2 == 2) else (0, 3)

        # --- Salvataggio su Supabase ---
        try:
            data = {
                "girone": girone_selezionato,   # oppure "Top"
                "player1": p1,
                "player2": p2,
                "set1_p1": set1_p1, "set1_p2": set1_p2,
                "set2_p1": set2_p1, "set2_p2": set2_p2,
                "set3_p1": s3p1_to_save, "set3_p2": s3p2_to_save,
                "is_super_tb": bool(is_super_tb),
                "winner": winner,
                "points_p1": points_p1, "points_p2": points_p2,
            }

            res = supabase.table("matches").insert(data).execute()
            st.success("Partita salvata su Supabase! ✅")

            # Aggiorna subito la UI
            try:
                st.cache_data.clear()
            except Exception:
                pass
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()

        except Exception as e:
            st.error(f"Errore durante il salvataggio su Supabase: {e}")

        # --- Salvataggio su Supabase ---
        try:
            data = {
                "girone": girone_selezionato,   # oppure "Top"
                "player1": p1,
                "player2": p2,
                "set1_p1": set1_p1, "set1_p2": set1_p2,
                "set2_p1": set2_p1, "set2_p2": set2_p2,
                "set3_p1": s3p1_to_save, "set3_p2": s3p2_to_save,
                "is_super_tb": bool(is_super_tb),
                "winner": winner,
                "points_p1": points_p1, "points_p2": points_p2,
            }

            res = supabase.table("matches").insert(data).execute()
            st.success("Partita salvata su Supabase! ✅")

            # Aggiorna subito la UI
            try:
                st.cache_data.clear()
            except Exception:
                pass
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()

        except Exception as e:
            st.error(f"Errore durante il salvataggio su Supabase: {e}")

        
    st.success("Partita salvata! ✅")

    # Ricarico immediato (classifica senza bottone)
    try:
        st.cache_data.clear()
    except Exception:
        pass
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

except Exception as e:
    st.error(f"Errore durante il salvataggio su Supabase: {e}")





        # ✅ invalida cache delle classifiche e ricarica
        st.cache_data.clear()
        st.experimental_rerun()

    except Exception as e:
        st.error(f"Errore durante il salvataggio su Supabase: {e}")
else:
    st.warning("Supabase non configurato: la partita non è stata salvata. Configura .env e ricarica l'app.")



# --- Classifica aggiornata (solo VIEW) ---
st.subheader("📈 Classifica aggiornata")

if df_classifica.empty:
    st.info("Nessuna riga in classifica per questo girone (inserisci una partita per iniziare).")
else:
    st.dataframe(df_classifica, use_container_width=True)

# separatore e nota sulle VIEW (fuori dal blocco if/else → allineato a sinistra)
st.divider()
st.markdown("ℹ️ La classifica è calcolata dal DB (VIEW). Il 3° set può essere un **super tie-break a 10 punti** (es. 10–8).")

# seconda tabella: standings_df (se presente). Allineata a sinistra (fuori da if/else).
if 'standings_df' in locals() and standings_df is not None and getattr(standings_df, 'empty', False) is False:
    st.dataframe(standings_df, use_container_width=True)

st.divider()
st.markdown("ℹ️ Il 3° set può essere giocato come **super tie-break a 10 punti**. L’app assegna il set al giocatore con più punti nel TB10.")


st.divider()
st.markdown("ℹ️ Il 3° set può essere giocato come **super tie-break a 10 punti**. L’app assegna il set al giocatore con più punti nel TB10.")

