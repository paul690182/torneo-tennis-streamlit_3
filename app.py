
import os
from datetime import datetime

import streamlit as st
from supabase import create_client, Client

# --------- Configurazione Supabase ---------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Variabili d'ambiente mancanti: SUPABASE_URL o SUPABASE_KEY.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🏆 Torneo Tennis - Girone Advanced")

# --------- Utility ---------
def _safe_int(x):
    """Ritorna int oppure None se x è None."""
    return int(x) if x is not None else None

@st.cache_data(ttl=30)
def get_giocatori():
    """
    Legge i giocatori dal DB scorrendo tutte le righe presenti.
    Se la tabella è vuota, ritorna lista vuota.
    """
    resp = supabase.table("risultati_advanced").select("giocatore1,giocatore2").execute()
    players = set()
    if resp.data:
        for row in resp.data:
            g1 = row.get("giocatore1")
            g2 = row.get("giocatore2")
            if g1: players.add(g1.strip())
            if g2: players.add(g2.strip())
    return sorted(players)

@st.cache_data(ttl=15)
def get_risultati():
    """Ritorna tutti i risultati ordinati per created_at decrescente."""
    return supabase.table("risultati_advanced").select("*").order("created_at", desc=True).execute()

@st.cache_data(ttl=15)
def get_classifica():
    """
    Calcola la classifica aggregando i risultati dal DB.
    Regole punti:
      - 2-0: 3 punti al vincitore
      - 2-1: 3 punti al vincitore, 1 punto allo sconfitto
      - 0-2: 0 punti
    """
    resp = supabase.table("risultati_advanced").select("*").execute()
    punti = {}
    if resp.data:
        for row in resp.data:
            g1 = row.get("giocatore1")
            g2 = row.get("giocatore2")
            s1g1 = row.get("set1_g1"); s1g2 = row.get("set1_g2")
            s2g1 = row.get("set2_g1"); s2g2 = row.get("set2_g2")
            s3g1 = row.get("set3_g1"); s3g2 = row.get("set3_g2")

            # Conta set vinti (considera il terzo set solo se entrambi non sono None)
            vinti_g1 = int(s1g1 > s1g2) + int(s2g1 > s2g2) + (int(s3g1 > s3g2) if s3g1 is not None and s3g2 is not None else 0)
            vinti_g2 = int(s1g2 > s1g1) + int(s2g2 > s2g1) + (int(s3g2 > s3g1) if s3g1 is not None and s3g2 is not None else 0)

            # Logica punti
            if vinti_g1 == 2:
                punti[g1] = punti.get(g1, 0) + 3
                if vinti_g2 > 0:
                    punti[g2] = punti.get(g2, 0) + 1
            elif vinti_g2 == 2:
                punti[g2] = punti.get(g2, 0) + 3
                if vinti_g1 > 0:
                    punti[g1] = punti.get(g1, 0) + 1

    # Ordina per punti decrescente
    return sorted(punti.items(), key=lambda x: x[1], reverse=True)

# --------- UI: Inserimento risultato ---------
st.subheader("📝 Inserisci nuovo risultato")
giocatori = get_giocatori()

if not giocatori:
    st.info("Non ci sono ancora giocatori registrati nella tabella. Inserisci almeno un match per popolare i menu.")
else:
    with st.form("form_risultato"):
        g1 = st.selectbox("Giocatore 1", giocatori)
        g2 = st.selectbox("Giocatore 2", [p for p in giocatori if p != g1])

        col1, col2 = st.columns(2)
        with col1:
            s1g1 = st.number_input("Set1 G1", min_value=0, max_value=7, value=6)
            s2g1 = st.number_input("Set2 G1", min_value=0, max_value=7, value=4)
            s3g1 = st.number_input("Set3 G1", min_value=0, max_value=20, value=0)
        with col2:
            s1g2 = st.number_input("Set1 G2", min_value=0, max_value=7, value=4)
            s2g2 = st.number_input("Set2 G2", min_value=0, max_value=7, value=6)
            s3g2 = st.number_input("Set3 G2", min_value=0, max_value=20, value=0)

        submit = st.form_submit_button("💾 Salva risultato")

    if submit:
        # Se il terzo set è 0-0, salviamo come NULL per significare "non giocato"
        set3_g1_val = None if (s3g1 == 0 and s3g2 == 0) else s3g1
        set3_g2_val = None if (s3g1 == 0 and s3g2 == 0) else s3g2

        data = {
            "giocatore1": g1.strip(),
            "giocatore2": g2.strip(),
            "set1_g1": int(s1g1), "set1_g2": int(s1g2),
            "set2_g1": int(s2g1), "set2_g2": int(s2g2),
            "set3_g1": _safe_int(set3_g1_val),
            "set3_g2": _safe_int(set3_g2_val),
            # Se la colonna ha DEFAULT now() sul DB, questa riga non è necessaria.
            "created_at": datetime.utcnow().isoformat()
        }

        try:
            resp = supabase.table("risultati_advanced").insert(data).execute()
            if resp.data:
                st.success("✅ Risultato salvato su Supabase!")
                # invalida la cache per ricalcolare classifica e storico
                get_classifica.clear()
                get_risultati.clear()
                get_giocatori.clear()
            else:
                st.warning(f"Salvataggio non confermato. Risposta: {resp}")
        except Exception as e:
            st.error(f"Errore nel salvataggio: {e}")

# --------- Classifica ---------
st.subheader("📊 Classifica (persistente)")
classifica = get_classifica()
if classifica:
    for pos, (player, pts) in enumerate(classifica, start=1):
        st.write(f"{pos}. {player} — {pts} punti")
else:
    st.info("Nessun risultato disponibile per calcolare la classifica.")

# --------- Storico ---------
st.subheader("🕒 Storico Risultati")
storico = get_risultati()
if storico.data:
    for row in storico.data:
        s3_part = ""
        s3g1 = row.get("set3_g1")
        s3g2 = row.get("set3_g2")
        if s3g1 is not None and s3g2 is not None:
            s3_part = f", {s3g1}-{s3g2}"
        st.write(
            f"{row.get('giocatore1')} vs {row.get('giocatore2')} → "
            f"{row.get('set1_g1')}-{row.get('set1_g2')}, "
            f"{row.get('set2_g1')}-{row.get('set2_g2')}{s3_part}"
        )
else:
    st.info("Ancora nessun match registrato.")


# Storico risultati
st.subheader("🕒 Storico Risultati")
storico = get_risultati()
if storico.data:
    for row in storico.data:
        s3_part = ""
        s3g1 = row.get("set3_g1")
        s3g2 = row.get("set3_g2")
        if s3g1 is not None and s3g2 is not None:
            s3_part = f", {s3g1}-{s3g2}"
        st.write(
            f"{row.get('giocatore1')} vs {row.get('giocatore2')} → "
            f"{row.get('set1_g1')}-{row.get('set1_g2')}, "
            f"{row.get('set2_g1')}-{row.get('set2_g2')}{s3_part}"
        )
else:
    st.info("Ancora nessun match registrato.")

# ✅ Inserisci qui il pannello diagnostico
import traceback

st.divider()
st.subheader("🔧 Diagnostica connessione Supabase")

try:
    # Test lettura
    ping_read = supabase.table("risultati_advanced").select("id", count="exact").limit(1).execute()
    cnt = ping_read.count if hasattr(ping_read, "count") else None

    # Test insert + delete
    ts = datetime.utcnow().isoformat()
    probe = {
        "giocatore1": "Probe",
        "giocatore2": "Probe2",
        "set1_g1": 1, "set1_g2": 0,
        "set2_g1": 1, "set2_g2": 0,
        "set3_g1": None, "set3_g2": None,
        "created_at": ts
    }
    ins = supabase.table("risultati_advanced").insert(probe).execute()
    ok_insert = bool(ins.data)

    # Se inserito, rimuovi per pulizia
    if ok_insert:
        new_id = ins.data[0].get("id")
        if new_id is not None:
            supabase.table("risultati_advanced").delete().eq("id", new_id).execute()

    st.success(f"✅ Supabase OK — Read count: {cnt}, Insert test: {ok_insert}")
except Exception as e:
    st.error(f"❌ Supabase non raggiungibile o policy bloccante: {e}")
    st.code(traceback.format_exc())

