
import asyncio
from postgrest import AsyncPostgrestClient
import streamlit as st
from supabase_config import SUPABASE_URL, SUPABASE_KEY

# Funzione asincrona per recuperare i dati da Supabase
async def fetch_data():
    client = AsyncPostgrestClient(f"{SUPABASE_URL}/rest/v1", headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    })
    try:
        classifica_response = await client.from_('classifica').select('*').execute()
        storico_response = await client.from_('storico').select('*').execute()

        return classifica_response, storico_response
    except Exception as e:
        st.error(f"Errore nel recupero dei dati: {e}")
        return None, None

# Funzione principale Streamlit
async def main():
    st.title("Torneo Tennis - Classifica e Storico")

    classifica, storico = await fetch_data()

    if classifica and hasattr(classifica, 'data'):
        st.subheader("Classifica")
        st.table(classifica.data)
    else:
        st.warning("Classifica non disponibile.")

    if storico and hasattr(storico, 'data'):
        st.subheader("Storico Partite")
        st.table(storico.data)
    else:
        st.warning("Storico non disponibile.")

# Avvia l'app Streamlit con asyncio
asyncio.run(main())
