
import streamlit as st
import pandas as pd
from supabase_config import supabase

st.set_page_config(page_title="Torneo Tennis", layout="wide")

# Nascondi sidebar
hide_sidebar_style = """
    <style>
    [data-testid="stSidebar"] {display: none;}
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

st.title("🏆 Torneo Tennis - Inserisci Risultato")

# Gironi
gironi = ["Top", "Advanced"]
scelta_girone = st.selectbox("Seleziona il girone", gironi)

# Dropdown giocatori
giocatori_top = ["Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo", "Cris Cosso", "Giovanni", "Andrea P.", "Giuseppe", "Salvatore", "Leonardino", "Federico", "Luca", "Adriano"]
giocatori_advanced = ["Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.", "Roberto A.", "Susanna", "Paolo Mattioli", "Paolo Rosi", "Michele", "Daniele M.", "Stefano D. R.", "Pino", "Gianni", "Leonardo", "Francesco M."]

if scelta_girone == "Top":
    giocatori = giocatori_top
    tabella = "risultati_top"
else:
    giocatori = giocatori_advanced
    tabella = "risultati_advanced"

col1, col2 = st.columns(2)
with col1:
    giocatore1 = st.selectbox("Giocatore 1", giocatori)
with col2:
    giocatore2 = st.selectbox("Giocatore 2", giocatori)

punteggio1 = st.number_input("Punteggio Giocatore 1", min_value=0, max_value=20, step=1)
punteggio2 = st.number_input("Punteggio Giocatore 2", min_value=0, max_value=20, step=1)

set1 = st.text_input("Set 1 (es. 6-4)")
set2 = st.text_input("Set 2 (es. 3-6)")
set3 = st.text_input("Set 3 (es. 6-4)")

if st.button("Salva Risultato"):
    if giocatore1 != giocatore2:
        data = {
            "giocatore1": giocatore1,
            "giocatore2": giocatore2,
            "punteggio1": punteggio1,
            "punteggio2": punteggio2,
            "set1": set1,
            "set2": set2,
            "set3": set3
        }
        supabase.table(tabella).insert(data).execute()
        st.success("✅ Risultato salvato con successo!")
    else:
        st.error("❌ I due giocatori devono essere diversi.")

st.subheader("📊 Storico Risultati")
res = supabase.table(tabella).select("*").order("created_at", desc=True).execute()
df = pd.DataFrame(res.data)

if not df.empty:
    st.dataframe(df)

    # Calcolo classifica
    st.subheader("🏅 Classifica")
    classifica = {}
    for _, row in df.iterrows():
        g1, g2 = row["giocatore1"], row["giocatore2"]
        p1, p2 = row["punteggio1"], row["punteggio2"]

        # Inizializza giocatori
        for g in [g1, g2]:
            if g not in classifica:
                classifica[g] = {"Punti": 0, "Vittorie": 0, "Sconfitte": 0, "Partite giocate": 0}

        # Aggiorna partite giocate
        classifica[g1]["Partite giocate"] += 1
        classifica[g2]["Partite giocate"] += 1

        # Logica punteggi
        if p1 > p2:
            classifica[g1]["Vittorie"] += 1
            classifica[g2]["Sconfitte"] += 1
            if abs(p1 - p2) >= 2:
                classifica[g1]["Punti"] += 3
            else:
                classifica[g1]["Punti"] += 3
                classifica[g2]["Punti"] += 1
        elif p2 > p1:
            classifica[g2]["Vittorie"] += 1
            classifica[g1]["Sconfitte"] += 1
            if abs(p2 - p1) >= 2:
                classifica[g2]["Punti"] += 3
            else:
                classifica[g2]["Punti"] += 3
                classifica[g1]["Punti"] += 1

    df_classifica = pd.DataFrame.from_dict(classifica, orient="index").sort_values(by="Punti", ascending=False)
    st.dataframe(df_classifica)
else:
    st.info("Nessun risultato inserito ancora.")

