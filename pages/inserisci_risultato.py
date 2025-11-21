
# -*- coding: utf-8 -*-
"""
Streamlit page: inserisci_risultato.py

Funzioni principali:
- Carica la lista dei giocatori da Supabase (classifica_top / classifica_advanced)
- Selectbox per Giocatore 1 / Giocatore 2 (no duplicati)
- Inserimento set (1–3)
- Salvataggio risultato (risultati_top / risultati_advanced)
- Aggiornamento automatico classifica con incremento punti
"""
import os
from typing import List, Tuple
import streamlit as st

try:
    from supabase import create_client
except Exception:
    create_client = None

st.set_page_config(page_title="Inserisci risultato", page_icon="🎾", layout="centered")

# --- Client Supabase: usare cache_resource (non serializzabile con pickle)
@st.cache_resource
def get_supabase_client():
    """Crea e cache la risorsa client Supabase (non serializzabile)."""
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("Variabili d'ambiente SUPABASE_URL/SUPABASE_KEY mancanti.")
    if create_client is None:
        raise RuntimeError("Libreria supabase non disponibile. Installa 'supabase'.")
    return create_client(url, key)

def get_giocatori(torneo: str) -> List[str]:
    client = get_supabase_client()
    tabella_classifica = "classifica_top" if torneo == "top" else "classifica_advanced"
    res = client.table(tabella_classifica).select("giocatore").execute()
    data = res.data or []
    giocatori = sorted([row.get("giocatore", "") for row in data if row.get("giocatore")])
    return giocatori

def salva_risultato(torneo: str, giocatore1: str, giocatore2: str,
                    set1: Tuple[int,int], set2: Tuple[int,int] | None,
                    set3: Tuple[int,int] | None, note: str):
    client = get_supabase_client()
    tabella_risultati = "risultati_top" if torneo == "top" else "risultati_advanced"
    payload = {
        "giocatore1": giocatore1,
        "giocatore2": giocatore2,
        "set1_g1": set1[0],
        "set1_g2": set1[1],
        "set2_g1": set2[0] if set2 else None,
        "set2_g2": set2[1] if set2 else None,
        "set3_g1": set3[0] if set3 else None,
        "set3_g2": set3[1] if set3 else None,
        "note": note or None,
    }
    return client.table(tabella_risultati).insert(payload).execute()

# --- Aggiorna classifica con incremento punti
def aggiorna_classifica(torneo: str, giocatore1: str, giocatore2: str,
                        set1: Tuple[int,int], set2: Tuple[int,int] | None, set3: Tuple[int,int] | None):
    g1_sets = 0
    g2_sets = 0
    for s in [set1, set2, set3]:
        if s:
            if s[0] > s[1]:
                g1_sets += 1
            elif s[1] > s[0]:
                g2_sets += 1

    if g1_sets > g2_sets:
        vincitore = giocatore1
        sconfitto = giocatore2
    else:
        vincitore = giocatore2
        sconfitto = giocatore1

    # Punti: 2-0 → 3/0, 2-1 → 3/1
    if abs(g1_sets - g2_sets) == 2:
        punti_vincitore = 3
        punti_sconfitto = 0
    else:
        punti_vincitore = 3
        punti_sconfitto = 1

    client = get_supabase_client()
    tabella_classifica = "classifica_top" if torneo == "top" else "classifica_advanced"

    def incrementa_punti(giocatore: str, incremento: int):
        # Legge punti attuali, somma e aggiorna
        res = client.table(tabella_classifica).select("punti").eq("giocatore", giocatore).execute()
        punti_attuali = 0
        if res.data:
            row = res.data[0]
            punti_attuali = int(row.get("punti", 0) or 0)
        nuovo_valore = punti_attuali + incremento
        client.table(tabella_classifica).update({"punti": nuovo_valore}).eq("giocatore", giocatore).execute()

    incrementa_punti(vincitore, punti_vincitore)
    incrementa_punti(sconfitto, punti_sconfitto)

    return vincitore, punti_vincitore, sconfitto, punti_sconfitto

# --- UI
st.title("Inserisci risultato partita")

with st.sidebar:
    st.header("Impostazioni")
    torneo = st.radio("Seleziona torneo", ["top", "advanced"], index=0)
    st.caption("I nomi dei giocatori vengono caricati dalla tabella classifica del torneo selezionato.")

try:
    giocatori = get_giocatori(torneo)
except Exception as e:
    st.error(f"Errore nel caricamento giocatori: {e}")
    giocatori = []

if not giocatori:
    st.warning("Nessun giocatore trovato.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    giocatore1 = st.selectbox("Giocatore 1", giocatori, index=0)
with col2:
    giocatori2 = [g for g in giocatori if g != giocatore1]
    if not giocatori2:
        st.error("Serve almeno 2 giocatori nella lista.")
        st.stop()
    giocatore2 = st.selectbox("Giocatore 2", giocatori2, index=0)

st.divider()
st.subheader("Risultato (punteggi dei set)")

def set_input(label: str) -> Tuple[int,int]:
    c1, c2 = st.columns(2)
    with c1:
        g1 = st.number_input(f"{label} - {giocatore1}", min_value=0, max_value=7, value=6)
    with c2:
        g2 = st.number_input(f"{label} - {giocatore2}", min_value=0, max_value=7, value=4)
    return int(g1), int(g2)

set1 = set_input("Set 1")
use_set2 = st.checkbox("Aggiungi Set 2", value=True)
set2 = set_input("Set 2") if use_set2 else None
use_set3 = st.checkbox("Aggiungi Set 3", value=False)
set3 = set_input("Set 3") if use_set3 else None

note = st.text_input("Note (opzionale)")

error_msgs = []
if giocatore1 == giocatore2:
    error_msgs.append("Giocatore 1 e Giocatore 2 devono essere diversi.")
if set1[0] == 0 and set1[1] == 0:
    error_msgs.append("Il Set 1 non può essere 0-0.")

if error_msgs:
    for msg in error_msgs:
        st.error(msg)

salva = st.button("💾 Salva risultato", disabled=bool(error_msgs))

if salva and not error_msgs:
    try:
        res = salva_risultato(torneo, giocatore1, giocatore2, set1, set2, set3, note)
        st.success("Risultato salvato correttamente!")
        vincitore, pv, sconfitto, ps = aggiorna_classifica(torneo, giocatore1, giocatore2, set1, set2, set3)
        st.success(f"Classifica aggiornata: {vincitore} +{pv} punti, {sconfitto} +{ps} punti")
        if hasattr(res, "data"):
            st.json(res.data)
    except Exception as e:
        st.error(f"Errore nel salvataggio: {e}")
