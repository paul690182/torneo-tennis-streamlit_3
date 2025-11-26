
import os
from datetime import datetime
import traceback
import streamlit as st
from supabase import create_client, Client

# ===============================
# Configurazione Supabase
# ===============================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Variabili d'ambiente mancanti: SUPABASE_URL o SUPABASE_KEY.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Torneo Tennis", page_icon="🎾", layout="centered")
st.title("🎾 Torneo Tennis — Due Gironi (Advanced + Top)")

# ===============================
# Liste giocatori STATICHE (DA TE FORNITE)
# ===============================
TOP_GIOCATORI = [
    "Simone",
    "Maurizio P.",
    "Marco",
    "Riccardo",
    "Massimo",
    "Cris Cosso",
    "Giovanni",
    "Andrea P.",
    "Giuseppe",
    "Salvatore",
    "Leonardino",
    "Federico",
    "Luca",
    "Adriano"
]

ADVANCED_GIOCATORI = [
    "Pasquale V.",
    "Gabriele T.",
    "Cris Capparoni",
    "Stefano C.",
    "Roberto A.",
    "Susanna",
    "Paolo Mattioli",
    "Paolo Rosi",
    "Michele",
    "Daniele M.",
    "Stefano D. R.",
    "Pino",
    "Gianni",
    "Leonardo",
    "Francesco M."
]

# ===============================
# Utility comuni
# ===============================
def _safe_int(x):
    return int(x) if x is not None else None

@st.cache_data(ttl=15)
def get_risultati(table_name: str):
    """Ritorna tutti i risultati ordinati per created_at decrescente."""
    try:
        return supabase.table(table_name).select("*").order("created_at", desc=True).execute()
    except Exception as e:
        return e  # gestiamo a UI

@st.cache_data(ttl=15)
def get_classifica(table_name: str):
    """
    Calcola la classifica dai risultati del DB.
    Regole punti:
      - 2-0: 3 punti al vincitore
      - 2-1: 3 punti al vincitore, 1 punto allo sconfitto
      - 0-2: 0 punti
    """
    punti = {}
    try:
        resp = supabase.table(table_name).select("*").execute()
    except Exception as e:
        return e

    if resp and getattr(resp, "data", None):
        for row in resp.data:
            g1 = row.get("giocatore1")
            g2 = row.get("giocatore2")
            s1g1 = row.get("set1_g1"); s1g2 = row.get("set1_g2")
            s2g1 = row.get("set2_g1"); s2g2 = row.get("set2_g2")
            s3g1 = row.get("set3_g1"); s3g2 = row.get("set3_g2")

            vinti_g1 = int(s1g1 > s1g2) + int(s2g1 > s2g2) + (int(s3g1 > s3g2) if s3g1 is not None and s3g2 is not None else 0)
            vinti_g2 = int(s1g2 > s1g1) + int(s2g2 > s2g1) + (int(s3g2 > s3g1) if s3g1 is not None and s3g2 is not None else 0)

            if vinti_g1 == 2:
                punti[g1] = punti.get(g1, 0) + 3
                if vinti_g2 > 0:
                    punti[g2] = punti.get(g2, 0) + 1
            elif vinti_g2 == 2:
                punti[g2] = punti.get(g2, 0) + 3
                if vinti_g1 > 0:
                    punti[g1] = punti.get(g1, 0) + 1

    if isinstance(punti, dict):
        return sorted(punti.items(), key=lambda x: x[1], reverse=True)
    return punti  # se è un'eccezione, la ritorniamo

def insert_risultato(table_name: str, g1: str, g2: str, s1g1: int, s1g2: int, s2g1: int, s2g2: int, s3g1, s3g2):
    """
    Inserisce il risultato in Supabase con controllo duplicati
    e terzo set come NULL se 0-0.
    """
    set3_g1_val = None if (s3g1 == 0 and s3g2 == 0) else s3g1
    set3_g2_val = None if (s3g1 == 0 and s3g2 == 0) else s3g2

    # Controllo duplicati (aderente alla UNIQUE del DB)
    exists = supabase.table(table_name).select("id")\
        .eq("giocatore1", g1).eq("giocatore2", g2)\
        .eq("set1_g1", s1g1).eq("set1_g2", s1g2)\
        .eq("set2_g1", s2g1).eq("set2_g2", s2g2)\
        .eq("set3_g1", set3_g1_val).eq("set3_g2", set3_g2_val).execute()

    if exists.data:
        return False, "⚠️ Questo risultato è già presente nel database."

    data = {
        "giocatore1": g1.strip(),
        "giocatore2": g2.strip(),
        "set1_g1": int(s1g1), "set1_g2": int(s1g2),
        "set2_g1": int(s2g1), "set2_g2": int(s2g2),
        "set3_g1": _safe_int(set3_g1_val),
        "set3_g2": _safe_int(set3_g2_val),
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        resp = supabase.table(table_name).insert(data).execute()
        if resp.data:
            # invalida cache per aggiornare UI
            get_classifica.clear(); get_risultati.clear()
            return True, "✅ Risultato salvato su Supabase!"
        return False, f"Salvataggio non confermato. Risposta: {resp}"
    except Exception as e:
        return False, f"Errore nel salvataggio: {e}"

# ===============================
# Interfaccia: due TAB (Advanced + Top)
# ===============================
tab_adv, tab_top = st.tabs(["💎 Girone Advanced", "🏅 Girone Top"])

# --------- TAB ADVANCED ---------
with tab_adv:
    st.subheader("📝 Inserisci risultato — Advanced")
    st.caption(f"Giocatori Advanced: {', '.join(ADVANCED_GIOCATORI)}")

    with st.form("form_adv"):
        g1a = st.selectbox("Giocatore 1 (Advanced)", ADVANCED_GIOCATORI, key="adv_g1")
        g2a = st.selectbox("Giocatore 2 (Advanced)", [p for p in ADVANCED_GIOCATORI if p != g1a], key="adv_g2")

        col1, col2 = st.columns(2)
        with col1:
            s1g1a = st.number_input("Set1 G1", min_value=0, max_value=7, value=6, key="adv_s1g1")
            s2g1a = st.number_input("Set2 G1", min_value=0, max_value=7, value=4, key="adv_s2g1")
            s3g1a = st.number_input("Set3 G1", min_value=0, max_value=20, value=0, key="adv_s3g1")
        with col2:
            s1g2a = st.number_input("Set1 G2", min_value=0, max_value=7, value=4, key="adv_s1g2")
            s2g2a = st.number_input("Set2 G2", min_value=0, max_value=7, value=6, key="adv_s2g2")
            s3g2a = st.number_input("Set3 G2", min_value=0, max_value=20, value=0, key="adv_s3g2")

        submit_adv = st.form_submit_button("💾 Salva (Advanced)")

    if submit_adv:
        ok, msg = insert_risultato(
            "risultati_advanced",
            g1a, g2a, s1g1a, s1g2a, s2g1a, s2g2a, s3g1a, s3g2a
        )
        (st.success if ok else st.warning)(msg)

    st.subheader("📊 Classifica — Advanced")
    classifica_adv = get_classifica("risultati_advanced")
    if isinstance(classifica_adv, Exception):
        st.error(f"Errore nel calcolo classifica (Advanced): {classifica_adv}")
    elif classifica_adv:
        for pos, (player, pts) in enumerate(classifica_adv, start=1):
            st.write(f"{pos}. {player} — {pts} punti")
    else:
        st.info("Nessun risultato disponibile per calcolare la classifica (Advanced).")

    st.subheader("🕒 Storico — Advanced")
    storico_adv = get_risultati("risultati_advanced")
    if isinstance(storico_adv, Exception):
        st.error(f"Errore nella lettura storico (Advanced): {storico_adv}")
    elif storico_adv.data:
        for row in storico_adv.data:
            s3_part = ""
            if row.get("set3_g1") is not None and row.get("set3_g2") is not None:
                s3_part = f", {row.get('set3_g1')}-{row.get('set3_g2')}"
            st.write(
                f"{row.get('giocatore1')} vs {row.get('giocatore2')} → "
                f"{row.get('set1_g1')}-{row.get('set1_g2')}, "
                f"{row.get('set2_g1')}-{row.get('set2_g2')}{s3_part}"
            )
    else:
        st.info("Ancora nessun match registrato (Advanced).")

# --------- TAB TOP ---------
with tab_top:
    st.subheader("📝 Inserisci risultato — Top")
    st.caption(f"Giocatori Top: {', '.join(TOP_GIOCATORI)}")

    with st.form("form_top"):
        g1t = st.selectbox("Giocatore 1 (Top)", TOP_GIOCATORI, key="top_g1")
        g2t = st.selectbox("Giocatore 2 (Top)", [p for p in TOP_GIOCATORI if p != g1t], key="top_g2")

        col1, col2 = st.columns(2)
        with col1:
            s1g1t = st.number_input("Set1 G1", min_value=0, max_value=7, value=6, key="top_s1g1")
            s2g1t = st.number_input("Set2 G1", min_value=0, max_value=7, value=4, key="top_s2g1")
            s3g1t = st.number_input("Set3 G1", min_value=0, max_value=20, value=0, key="top_s3g1")
        with col2:
            s1g2t = st.number_input("Set1 G2", min_value=0, max_value=7, value=4, key="top_s1g2")
            s2g2t = st.number_input("Set2 G2", min_value=0, max_value=7, value=6, key="top_s2g2")
            s3g2t = st.number_input("Set3 G2", min_value=0, max_value=20, value=0, key="top_s3g2")

        submit_top = st.form_submit_button("💾 Salva (Top)")

    if submit_top:
        ok, msg = insert_risultato(
            "risultati_top",
            g1t, g2t, s1g1t, s1g2t, s2g1t, s2g2t, s3g1t, s3g2t
        )
        (st.success if ok else st.warning)(msg)

    st.subheader("📊 Classifica — Top")
    classifica_top = get_classifica("risultati_top")
    if isinstance(classifica_top, Exception):
        st.error(f"Errore nel calcolo classifica (Top): {classifica_top}")
    elif classifica_top:
        for pos, (player, pts) in enumerate(classifica_top, start=1):
            st.write(f"{pos}. {player} — {pts} punti")
    else:
        st.info("Nessun risultato disponibile per calcolare la classifica (Top).")

    st.subheader("🕒 Storico — Top")
    storico_top = get_risultati("risultati_top")
    if isinstance(storico_top, Exception):
        st.error(f"Errore nella lettura storico (Top): {storico_top}")
    elif storico_top.data:
        for row in storico_top.data:
            s3_part = ""
            if row.get("set3_g1") is not None and row.get("set3_g2") is not None:
                s3_part = f", {row.get('set3_g1')}-{row.get('set3_g2')}"
            st.write(
                f"{row.get('giocatore1')} vs {row.get('giocatore2')} → "
                f"{row.get('set1_g1')}-{row.get('set1_g2')}, "
                f"{row.get('set2_g1')}-{row.get('set2_g2')}{s3_part}"
            )
    else:
        st.info("Ancora nessun match registrato (Top).")

# ===============================
# Diagnostica per entrambe le tabelle
# ===============================
st.divider()
st.subheader("🔧 Diagnostica connessione Supabase (Advanced + Top)")

def diagnostica_tabella(table_name: str):
    try:
        # READ test
        ping_read = supabase.table(table_name).select("id", count="exact").limit(1).execute()
        cnt = ping_read.count if hasattr(ping_read, "count") else None

        # INSERT test con punteggi validi (6-4, 6-4), poi DELETE
        ts = datetime.utcnow().isoformat()
        probe = {
            "giocatore1": "Probe",
            "giocatore2": "Probe2",
            "set1_g1": 6, "set1_g2": 4,
            "set2_g1": 6, "set2_g2": 4,
            "set3_g1": None, "set3_g2": None,
            "created_at": ts
        }
        ins = supabase.table(table_name).insert(probe).execute()
        ok_insert = bool(ins.data)

        if ok_insert:
            new_id = ins.data[0].get("id")
            if new_id is not None:
                supabase.table(table_name).delete().eq("id", new_id).execute()

        st.success(f"✅ {table_name}: Read count={cnt}, Insert test={ok_insert}")
    except Exception as e:
        st.error(f"❌ {table_name}: {e}")
        st.code(traceback.format_exc())

diagnostica_tabella("risultati_advanced")
diagnostica_tabella("risultati_top")

