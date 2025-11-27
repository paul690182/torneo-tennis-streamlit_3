
import streamlit as st
from supabase import create_client, Client
import pandas as pd

# =============================
# CONFIGURAZIONE PAGINA + HIDE SIDEBAR
# =============================
st.set_page_config(page_title="Torneo Tennis", layout="wide")

# Nascondi completamente la sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none !important;}
        .block-container {padding-top: 1rem;}
    </style>
""", unsafe_allow_html=True)

# =============================
# CONFIGURAZIONE SUPABASE (da supabase_config.py)
# =============================
# NON toccare le chiavi: le importiamo dal tuo file dedicato
from supabase_config import SUPABASE_URL, SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# =============================
# LISTE GIOCATORI COMPLETE
# =============================
GIOCATORI_TOP = [
    "Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo", "Cris Cosso", "Giovanni",
    "Andrea P.", "Giuseppe", "Salvatore", "Leonardino", "Federico", "Luca", "Adriano"
]
GIOCATORI_ADVANCED = [
    "Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.", "Roberto A.", "Susanna",
    "Paolo Mattioli", "Paolo Rosi", "Michele", "Daniele M.", "Stefano D. R.", "Pino",
    "Gianni", "Leonardo", "Francesco M."
]

# =============================
# UTILS: VALIDAZIONE + CLASSIFICA
# =============================
def valida_punteggio(val):
    """Accetta '' (vuoto) o interi 0..20."""
    if val == "" or val is None:
        return True
    try:
        v = int(val)
        return 0 <= v <= 20
    except ValueError:
        return False

def calcola_classifica(matches):
    """
    Punteggio:
      - 3 al vincitore
      - 1 allo sconfitto se perde 2–1
      - 0 allo sconfitto se perde 2–0
    Conteggio: Vinte/Perse sul match (non per set).
    """
    stats = {}
    for m in matches:
        g1 = m.get("giocatore1")
        g2 = m.get("giocatore2")
        if not g1 or not g2:
            continue

        if g1 not in stats:
            stats[g1] = {"Vinte": 0, "Perse": 0, "Punti": 0}
        if g2 not in stats:
            stats[g2] = {"Vinte": 0, "Perse": 0, "Punti": 0}

        # Conta i set vinti da ciascuno
        set_g1 = 0
        set_g2 = 0
        for s1, s2 in [
            (m.get("set1_g1"), m.get("set1_g2")),
            (m.get("set2_g1"), m.get("set2_g2")),
            (m.get("set3_g1"), m.get("set3_g2")),
        ]:
            if s1 is not None and s2 is not None:
                try:
                    if int(s1) > int(s2): set_g1 += 1
                    elif int(s2) > int(s1): set_g2 += 1
                except Exception:
                    # Se qualche valore non è convertibile, ignoro quel set
                    pass

        # Determina vincitore match e assegna punti
        if set_g1 > set_g2:
            stats[g1]["Vinte"] += 1
            stats[g2]["Perse"] += 1
            stats[g1]["Punti"] += 3
            # Sconfitto con 2–1 prende 1 punto
            if set_g2 == 1 and set_g1 == 2:
                stats[g2]["Punti"] += 1
        elif set_g2 > set_g1:
            stats[g2]["Vinte"] += 1
            stats[g1]["Perse"] += 1
            stats[g2]["Punti"] += 3
            if set_g1 == 1 and set_g2 == 2:
                stats[g1]["Punti"] += 1
        # Se pari (dati incompleti), non assegno punti

    df = pd.DataFrame.from_dict(stats, orient="index")
    if df.empty:
        return pd.DataFrame(columns=["Giocatore", "Vinte", "Perse", "Punti"])
    df = df.sort_values(by=["Punti", "Vinte"], ascending=[False, False])
    return df.reset_index().rename(columns={"index": "Giocatore"})

# =============================
# UI
# =============================
st.title("🎾 Torneo Tennis — Inserimento & Classifica")

# Selettore girone
st.subheader("Seleziona Girone")
girone = st.selectbox("Girone", ["Top", "Advanced"])

# Tabella e lista giocatori dinamiche
NOME_TABELLA = "risultati_top" if girone == "Top" else "risultati_advanced"
LISTA_GIOCATORI = GIOCATORI_TOP if girone == "Top" else GIOCATORI_ADVANCED

# -----------------------------
# FORM: INSERIMENTO RISULTATO
# -----------------------------
st.subheader("Inserisci Match")

with st.form("inserisci_match", clear_on_submit=True):
    col_nomi = st.columns(2)
    with col_nomi[0]:
        giocatore1 = st.selectbox("Giocatore 1", LISTA_GIOCATORI, key="g1")
    with col_nomi[1]:
        lista_g2 = [g for g in LISTA_GIOCATORI if g != giocatore1]
        giocatore2 = st.selectbox("Giocatore 2", lista_g2, key="g2")

    st.write("**Set 1**")
    c1 = st.columns(2)
    with c1[0]:
        set1_g1 = st.text_input("Punteggio Giocatore 1 (Set 1)", key="s1g1")
    with c1[1]:
        set1_g2 = st.text_input("Punteggio Giocatore 2 (Set 1)", key="s1g2")

    st.write("**Set 2**")
    c2 = st.columns(2)
    with c2[0]:
        set2_g1 = st.text_input("Punteggio Giocatore 1 (Set 2)", key="s2g1")
    with c2[1]:
        set2_g2 = st.text_input("Punteggio Giocatore 2 (Set 2)", key="s2g2")

    st.write("**Set 3 (opzionale)**")
    c3 = st.columns(2)
    with c3[0]:
        set3_g1 = st.text_input("Punteggio Giocatore 1 (Set 3)", key="s3g1")
    with c3[1]:
        set3_g2 = st.text_input("Punteggio Giocatore 2 (Set 3)", key="s3g2")

    submitted = st.form_submit_button("Salva Risultato")

    if submitted:
        # Validazione punteggi
        if not all(valida_punteggio(p) for p in [set1_g1, set1_g2, set2_g1, set2_g2, set3_g1, set3_g2]):
            st.error("I punteggi devono essere numeri interi tra 0 e 20 o vuoti.")
        else:
            def conv(val): return int(val) if val != "" else None
            record = {
                "giocatore1": giocatore1,
                "giocatore2": giocatore2,
                "set1_g1": conv(set1_g1),
                "set1_g2": conv(set1_g2),
                "set2_g1": conv(set2_g1),
                "set2_g2": conv(set2_g2),
                "set3_g1": conv(set3_g1),
                "set3_g2": conv(set3_g2),
            }
            try:
                supabase.table(NOME_TABELLA).insert(record).execute()
                st.success(f"Risultato salvato nel girone {girone}!")
            except Exception as e:
                st.error(f"Errore durante l'inserimento: {e}")

# -----------------------------
# RISULTATI + CLASSIFICA
# -----------------------------
st.subheader(f"📋 Risultati — Girone {girone}")
try:
    resp = supabase.table(NOME_TABELLA).select("*").order("created_at", desc=True).execute()
    matches = resp.data or []
    if matches:
        for m in matches:
            st.markdown(f"**{m.get('giocatore1','?')} vs {m.get('giocatore2','?')}**")
            s1 = f"{m.get('set1_g1','-')}-{m.get('set1_g2','-')}"
            s2 = f"{m.get('set2_g1','-')}-{m.get('set2_g2','-')}"
            s3 = (
                f"{m.get('set3_g1','-')}-{m.get('set3_g2','-')}"
                if (m.get('set3_g1') is not None and m.get('set3_g2') is not None)
                else "- -"
            )
            st.write(f"Set 1: {s1}")
            st.write(f"Set 2: {s2}")
            st.write(f"Set 3: {s3}")
            st.markdown("---")

        st.subheader("🏆 Classifica")
        df = calcola_classifica(matches)
        st.table(df)
    else:
        st.info("Nessun risultato disponibile per questo girone.")
except Exception as e:
    st.error(f"Errore nel recupero dati: {e}")

