
import asyncio
from postgrest import AsyncPostgrestClient
import streamlit as st
from supabase_config import SUPABASE_URL, SUPABASE_KEY
from collections import defaultdict
import pandas as pd

# Funzione per calcolare la classifica
def calcola_classifica(partite):
    classifica = defaultdict(lambda: {"punti": 0, "vittorie": 0, "sconfitte": 0, "giocate": 0})

    for partita in partite:
        g1 = partita["giocatore1"]
        g2 = partita["giocatore2"]
        p1 = partita["punteggio_g1"]
        p2 = partita["punteggio_g2"]

        classifica[g1]["giocate"] += 1
        classifica[g2]["giocate"] += 1

        if p1 == 2 and p2 == 0:
            classifica[g1]["punti"] += 3
            classifica[g1]["vittorie"] += 1
            classifica[g2]["sconfitte"] += 1
        elif p1 == 2 and p2 == 1:
            classifica[g1]["punti"] += 3
            classifica[g1]["vittorie"] += 1
            classifica[g2]["punti"] += 1
            classifica[g2]["sconfitte"] += 1
        elif p2 == 2 and p1 == 0:
            classifica[g2]["punti"] += 3
            classifica[g2]["vittorie"] += 1
            classifica[g1]["sconfitte"] += 1
        elif p2 == 2 and p1 == 1:
            classifica[g2]["punti"] += 3
            classifica[g2]["vittorie"] += 1
            classifica[g1]["punti"] += 1
            classifica[g1]["sconfitte"] += 1

    classifica_ordinata = sorted(classifica.items(), key=lambda x: x[1]["punti"], reverse=True)
    return classifica_ordinata

# Funzione per recuperare i dati da Supabase
async def fetch_data():
    client = AsyncPostgrestClient(f"{SUPABASE_URL}/rest/v1", headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    try:
        partite_response = await client.from_("partite_classifica").select("*").execute()
        return partite_response
    except Exception as e:
        st.error(f"Errore nel recupero dei dati: {e}")
        return None

# Funzione principale dell'app
async def main():
    st.title("Torneo Tennis - Classifica e Storico")

    partite_response = await fetch_data()

    if partite_response and hasattr(partite_response, 'data'):
        partite = partite_response.data
        df = pd.DataFrame(partite)

        # Filtri
        giocatori = sorted(set(df['giocatore1']).union(df['giocatore2']))
        giocatore_selezionato = st.selectbox("Filtra per giocatore", ["Tutti"] + giocatori)
        date_disponibili = sorted(df['data_partita'].dropna().unique())
        data_selezionata = st.selectbox("Filtra per data", ["Tutte"] + list(date_disponibili))

        if giocatore_selezionato != "Tutti":
            df = df[(df['giocatore1'] == giocatore_selezionato) | (df['giocatore2'] == giocatore_selezionato)]
        if data_selezionata != "Tutte":
            df = df[df['data_partita'] == data_selezionata]

        # Calcola la classifica
        classifica = calcola_classifica(df.to_dict(orient="records"))

        # Mostra la classifica
        st.subheader("Classifica")
        st.table([
            {"Giocatore": g, **stats}
            for g, stats in classifica
        ])

        # Mostra lo storico partite con set
        st.subheader("Storico Partite")
        colonne = ["data_partita", "giocatore1", "giocatore2", "set1", "set2", "set3", "punteggio_g1", "punteggio_g2", "vincitore"]
        st.dataframe(df[colonne])
    else:
        st.warning("Dati non disponibili.")

# Avvia l'app
if __name__ == "__main__":
    asyncio.run(main())
