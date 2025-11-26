
import streamlit as st
from supabase import create_client
import os
from datetime import datetime

# Configurazione Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🏆 Torneo Tennis - Girone Advanced")

# Funzione per leggere giocatori dal DB
def get_giocatori():
    response = supabase.table("risultati_advanced").select("giocatore1,giocatore2").execute()
    if response.data:
        # Estrai tutti i nomi e rimuovi duplicati
        players = set()
        for row in response.data:
            if row["giocatore1"]: players.add(row["giocatore1"])
            if row["giocatore2"]: players.add(row["giocatore2"])
        return sorted(players)
    return []

# Funzione per leggere risultati e calcolare classifica
def get_classifica():
    response = supabase.table("risultati_advanced").select("*").execute()
    punti = {}
    if response.data:
        for row in response.data:
            g1, g2 = row["giocatore1"], row["giocatore2"]
            s1g1, s1g2 = row["set1_g1"], row["set1_g2"]
            s2g1, s2g2 = row["set2_g1"], row["set2_g2"]
            s3g1, s3g2 = row["set3_g1"], row["set3_g2"]

            # Conta set vinti
            vinti_g1 = (s1g1 > s1g2) + (s2g1 > s2g2) + (s3g1 > s3g2 if s3g1 is not None and s3g2 is not None else 0)
            vinti_g2 = (s1g2 > s1g1) + (s2g2 > s2g1) + (s3g2 > s3g1 if s3g1 is not None and s3g2 is not None else 0)

            # Logica punti
            if vinti_g1 == 2:
                if vinti_g2 == 0:
                    punti[g1] = punti.get(g1, 0) + 3
                else:
                    punti[g1] = punti.get(g1, 0) + 3
                    punti[g2] = punti.get(g2, 0) + 1
            elif vinti_g2 == 2:
                if vinti_g1 == 0:
                    punti[g2] = punti.get(g2, 0) + 3
                else:
                    punti[g2] = punti.get(g2, 0) + 3
                    punti[g1] = punti.get(g1, 0) + 1
    return sorted(punti.items(), key=lambda x: x[1], reverse=True)

# UI: Form inserimento risultato
st.subheader("Inserisci nuovo risultato")
giocatori = get_giocatori()
if giocatori:
    with st.form("form_risultato"):
        g1 = st.selectbox("Giocatore 1", giocatori)
        g2 = st.selectbox("Giocatore 2", [p for p in giocatori if p != g1])
        col1, col2 = st.columns(2)
        with col1:
            s1g1 = st.number_input("Set1 G1", 0, 7, 6)
            s2g1 = st.number_input("Set2 G1", 0, 7, 4)
            s3g1 = st.number_input("Set3 G1", 0, 20, 0)
        with col2:
            s1g2 = st.number_input("Set1 G2", 0, 7, 4)
            s2g2 = st.number_input("Set2 G2", 0, 7, 6)
            s3g2 = st.number_input("Set3 G2", 0, 20, 0)
        submit = st.form_submit_button("Salva risultato")

    if submit:
        data = {
            "giocatore1": g1,
            "giocatore2": g2,
            "set1_g1": s1g1, "set1_g2": s1g2,
            "set2_g1": s2g1, "set2_g2": s2g2,
            "set3_g1": s3g1 if s3g1 > 0 or s3g2 > 0 else None,
            "set3_g2": s3g2 if s3g1 > 0 or s3g2 > 0 else None,
            "created_at": datetime.utcnow().isoformat()
        }
        response = supabase.table("risultati_advanced").insert(data).execute()
        if response.data:
            st.success("✅ Risultato salvato!")
        else:
            st.error("Errore nel salvataggio.")

# Mostra classifica
st.subheader("Classifica")
classifica = get_classifica()
if classifica:
    for pos, (player, pts) in enumerate(classifica, start=1):
        st.write(f"{pos}. {player} — {pts} punti")
else:
    st.info("Nessun risultato disponibile.")

# Storico risultati
st.subheader("Storico Risultati")
response = supabase.table("risultati_advanced").select("*").order("created_at", desc=True).execute()
if response.data:
    for row in response.data:
        st.write(f"{row['giocatore1']} vs {row['giocatore2']} → "
                 f"{row['set1_g1']}-{row['set1_g2']}, {row['set2_g1']}-{row['set2_g2']}, "
                 f"{row['set3_g1']}-{row['set3_g2'] if row['set3_g2'] else ''}")
else:
    st.info("Ancora nessun match registrato.")
