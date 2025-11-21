
# -*- coding: utf-8 -*-
"""
Streamlit page: classifica.py

Funzioni principali:
- Legge la tabella classifica_top o classifica_advanced da Supabase
- Calcola statistiche: partite giocate, set vinti, set persi, differenza set
- Ordina per punti decrescenti e differenza set
- Mostra una tabella ordinata
"""
import os
import streamlit as st
import pandas as pd

try:
    from supabase import create_client
except Exception:
    create_client = None

st.set_page_config(page_title="Classifica", page_icon="🏆", layout="wide")

@st.cache_resource
def get_supabase_client():
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("Variabili d'ambiente mancanti.")
    if create_client is None:
        raise RuntimeError("Libreria supabase non disponibile.")
    return create_client(url, key)

@st.cache_data(ttl=300)
def get_classifica(torneo: str):
    client = get_supabase_client()
    tabella_classifica = "classifica_top" if torneo == "top" else "classifica_advanced"
    res = client.table(tabella_classifica).select("giocatore,punti").execute()
    return res.data or []

@st.cache_data(ttl=300)
def get_risultati(torneo: str):
    client = get_supabase_client()
    tabella_risultati = "risultati_top" if torneo == "top" else "risultati_advanced"
    res = client.table(tabella_risultati).select(
        "giocatore1,giocatore2,set1_g1,set1_g2,set2_g1,set2_g2,set3_g1,set3_g2"
    ).execute()
    return res.data or []

@st.cache_data(ttl=60)
def calcola_statistiche(classifica, risultati):
    # Inizializza stats anche per giocatori che compaiono solo nei risultati
    stats = {}
    for row in classifica:
        g = row['giocatore']
        stats[g] = {'punti': int(row.get('punti', 0) or 0), 'partite': 0, 'set_vinti': 0, 'set_persi': 0}

    for r in risultati:
        g1 = r['giocatore1']
        g2 = r['giocatore2']
        stats.setdefault(g1, {'punti': 0, 'partite': 0, 'set_vinti': 0, 'set_persi': 0})
        stats.setdefault(g2, {'punti': 0, 'partite': 0, 'set_vinti': 0, 'set_persi': 0})
        sets = [
            (r['set1_g1'], r['set1_g2']),
            (r.get('set2_g1'), r.get('set2_g2')),
            (r.get('set3_g1'), r.get('set3_g2')),
        ]
        stats[g1]['partite'] += 1
        stats[g2]['partite'] += 1
        for s in sets:
            if s and s[0] is not None and s[1] is not None:
                if s[0] > s[1]:
                    stats[g1]['set_vinti'] += 1
                    stats[g2]['set_persi'] += 1
                elif s[1] > s[0]:
                    stats[g2]['set_vinti'] += 1
                    stats[g1]['set_persi'] += 1

    df = []
    for g, v in stats.items():
        diff_set = v['set_vinti'] - v['set_persi']
        df.append({
            'Giocatore': g,
            'Punti': v['punti'],
            'Partite': v['partite'],
            'Set vinti': v['set_vinti'],
            'Set persi': v['set_persi'],
            'Diff set': diff_set,
        })
    df = pd.DataFrame(df)
    if not df.empty:
        df.sort_values(by=['Punti', 'Diff set', 'Giocatore'], ascending=[False, False, True], inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.insert(0, 'Posizione', df.index + 1)
    return df

st.title("Classifica torneo")
with st.sidebar:
    torneo = st.radio("Seleziona torneo", ["top", "advanced"], index=0)

try:
    classifica = get_classifica(torneo)
    risultati = get_risultati(torneo)
    df = calcola_statistiche(classifica, risultati)
    st.subheader(f"Classifica {torneo.capitalize()}")
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error(f"Errore nel caricamento classifica: {e}")
