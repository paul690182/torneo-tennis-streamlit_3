
# -*- coding: utf-8 -*-
"""
Streamlit page: inserisci_risultato.py

Funzioni principali:
- Carica la lista dei giocatori da Supabase (tabella classifica_top o classifica_advanced)
- Mostra menu a tendina (selectbox) per Giocatore 1 e Giocatore 2
- Impedisce la selezione dello stesso giocatore due volte
- Consente l'inserimento del risultato dell'incontro
- Salva il risultato sul DB (tabella risultati_top o risultati_advanced)

Prerequisiti:
- Variabili d'ambiente SUPABASE_URL e SUPABASE_KEY settate (Render/Supabase)
- Libreria supabase (supabase-py) installata
    pip install supabase

Autore: adattato per Giuseppe D'Eramo
"""
import os
from typing import List, Tuple

import streamlit as st

# Import "lazily" per evitare errori locali quando l'SDK non è disponibile.
try:
    from supabase import create_client
except Exception:
    create_client = None

# -------------------------------
# Configurazione pagina Streamlit
# -------------------------------
st.set_page_config(page_title="Inserisci risultato", page_icon="🎾", layout="centered")

# -------------------------------
# Utility DB
# -------------------------------
@st.cache_data(ttl=300)
def get_supabase_client():
    """Restituisce il client Supabase usando le variabili d'ambiente.
    Cache per 5 minuti.
    """
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError(
            "Variabili d'ambiente SUPABASE_URL/SUPABASE_KEY mancanti."
        )
    if create_client is None:
        raise RuntimeError(
            "Libreria supabase non disponibile. Installa 'supabase' (supabase-py)."
        )
    return create_client(url, key)


def get_giocatori(torneo: str) -> List[str]:
    """Recupera la lista dei giocatori dalla tabella classifica_*.

    Args:
        torneo: "top" oppure "advanced".
    Returns:
        Lista di nomi giocatori (ordinati alfabeticamente).
    """
    client = get_supabase_client()
    tabella_classifica = "classifica_top" if torneo == "top" else "classifica_advanced"
    # Seleziona la colonna "giocatore"; se nel DB la colonna ha nome diverso, adattare qui.
    res = client.table(tabella_classifica).select("giocatore").execute()
    data = res.data or []
    giocatori = sorted([row.get("giocatore", "") for row in data if row.get("giocatore")])
    return giocatori


def salva_risultato(
    torneo: str,
    giocatore1: str,
    giocatore2: str,
    set1: Tuple[int, int],
    set2: Tuple[int, int] | None,
    set3: Tuple[int, int] | None,
    note: str,
):
    """Salva il risultato nella tabella risultati_*.

    La tabella dovrebbe contenere almeno i seguenti campi:
    - giocatore1 (text)
    - giocatore2 (text)
    - set1_g1 (int)
    - set1_g2 (int)
    - set2_g1 (int, nullable)
    - set2_g2 (int, nullable)
    - set3_g1 (int, nullable)
    - set3_g2 (int, nullable)
    - note (text, nullable)
    - created_at (timestamp, default now()) opzionale
    """
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

    res = client.table(tabella_risultati).insert(payload).execute()
    return res


# -------------------------------
# UI
# -------------------------------
st.title("Inserisci risultato partita")

with st.sidebar:
    st.header("Impostazioni")
    torneo = st.radio("Seleziona torneo", ["top", "advanced"], index=0, help="Scegli quale torneo aggiornare.")
    st.caption("I nomi dei giocatori vengono caricati dalla tabella classifica del torneo selezionato.")

# Caricamento lista giocatori
try:
    giocatori = get_giocatori(torneo)
except Exception as e:
    st.error(f"Errore nel caricamento giocatori: {e}")
    giocatori = []

if not giocatori:
    st.warning("Nessun giocatore trovato. Verifica la tabella classifica_* su Supabase e le variabili d'ambiente.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    giocatore1 = st.selectbox("Giocatore 1", giocatori, index=0)
with col2:
    # Escludiamo il giocatore1 dalla lista del secondo menu.
    giocatori2 = [g for g in giocatori if g != giocatore1]
    if not giocatori2:
        st.error("Serve almeno 2 giocatori nella lista.")
        st.stop()
    giocatore2 = st.selectbox("Giocatore 2", giocatori2, index=0)

st.divider()

st.subheader("Risultato (punteggi dei set)")

# Helper per input del set: due number_input affiancati
def set_input(label: str) -> Tuple[int, int]:
    c1, c2 = st.columns(2)
    with c1:
        g1 = st.number_input(f"{label} - {giocatore1}", min_value=0, max_value=7, value=6, step=1)
    with c2:
        g2 = st.number_input(f"{label} - {giocatore2}", min_value=0, max_value=7, value=4, step=1)
    return int(g1), int(g2)

set1 = set_input("Set 1")
use_set2 = st.checkbox("Aggiungi Set 2", value=True)
set2 = set_input("Set 2") if use_set2 else None
use_set3 = st.checkbox("Aggiungi Set 3", value=False)
set3 = set_input("Set 3") if use_set3 else None

note = st.text_input("Note (opzionale)", placeholder="Es. tie-break a 7, infortunio, ecc.")

st.divider()

# Validazioni base
error_msgs = []
if giocatore1 == giocatore2:
    error_msgs.append("Giocatore 1 e Giocatore 2 devono essere diversi.")

# Controllo minimo: almeno set1 deve essere compilato in modo plausibile
if set1[0] == 0 and set1[1] == 0:
    error_msgs.append("Il Set 1 non può essere 0-0.")

if error_msgs:
    for msg in error_msgs:
        st.error(msg)

# Bottone salva
col_left, col_right = st.columns([1, 2])
with col_left:
    salva = st.button("💾 Salva risultato", type="primary", disabled=bool(error_msgs))

with col_right:
    st.caption("Il risultato sarà salvato nella tabella risultati del torneo selezionato.")

if salva and not error_msgs:
    try:
        res = salva_risultato(
            torneo=torneo,
            giocatore1=giocatore1,
            giocatore2=giocatore2,
            set1=set1,
            set2=set2,
            set3=set3,
            note=note,
        )
        st.success("Risultato salvato correttamente!")
        if hasattr(res, "data"):
            st.json(res.data)
    except Exception as e:
        st.error(f"Errore nel salvataggio del risultato: {e}")
        st.stop()
