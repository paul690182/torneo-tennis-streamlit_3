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
        try:
            g1 = partita["giocatore1"]
            g2 = partita["giocatore2"]
            p1 = partita["punteggio_g1"]
            p2 = partita["punteggio_g2"]
        except KeyError:
            continue

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

        if not df.empty and 'giocatore1' in df.columns and 'giocatore2' in df.columns:
            giocatori = sorted(set(df['giocatore1'].dropna().unique()).union(df['giocatore2'].dropna().unique()))
            giocatore_selezionato = st.selectbox("Filtra per giocatore", ["Tutti"] + giocatori)
        else:
            giocatore_selezionato = "Tutti"

        if 'data_partita' in df.columns:
            df['data_partita'] = pd.to_datetime(df['data_partita'], errors='coerce')
            data_min = df['data_partita'].min()
            data_max = df['data_partita'].max()
            data_selezionata = st.date_input("Filtra per data", value=data_max.date() if pd.notnull(data_max) else None)
        else:
            data_selezionata = None

        if giocatore_selezionato != "Tutti":
            df = df[(df['giocatore1'] == giocatore_selezionato) | (df['giocatore2'] == giocatore_selezionato)]

        if data_selezionata:
            df = df[df['data_partita'].dt.date == data_selezionata]

        classifica = calcola_classifica(df.to_dict(orient='records'))

        st.subheader("Classifica")
        st.table([{"Giocatore": g, **stats} for g, stats in classifica])

        st.subheader("Storico Partite")
        colonne_da_mostrare = ["data_partita", "giocatore1", "giocatore2", "set1", "set2", "set3", "punteggio_g1", "punteggio_g2", "vincitore"]
        colonne_presenti = [col for col in colonne_da_mostrare if col in df.columns]
        st.dataframe(df[colonne_presenti])
    else:
        st.warning("Dati non disponibili.")

# Avvia l'app
if __name__ == "__main__":
    asyncio.run(main())
