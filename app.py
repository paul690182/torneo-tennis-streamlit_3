
import pandas as pd
import streamlit as st
from datetime import datetime

# Simulazione: caricamento dati da Supabase (sostituire con query reale)
data = [
    {'giocatore1': 'Paolo R.', 'giocatore2': 'Francesco M.', 'punti_g1': 3, 'punti_g2': 0, 'created_at': '2025-11-02 14:35:08'},
    {'giocatore1': 'Francesco M.', 'giocatore2': 'Andrea P.', 'punti_g1': 3, 'punti_g2': 1, 'created_at': '2025-11-01 16:20:00'},
    {'giocatore1': 'Leo S.', 'giocatore2': 'Maurizio P.', 'punti_g1': 0, 'punti_g2': 3, 'created_at': '2025-10-30 18:00:00'},
    {'giocatore1': 'Daniele T.', 'giocatore2': 'Simone V.', 'punti_g1': 3, 'punti_g2': 1, 'created_at': '2025-10-28 17:45:00'},
    {'giocatore1': 'Simone V.', 'giocatore2': 'Paolo R.', 'punti_g1': 3, 'punti_g2': 0, 'created_at': '2025-10-25 15:30:00'}
]

# Crea DataFrame
df = pd.DataFrame(data)

# Conversione robusta delle date
df["created_at"] = pd.to_datetime(
    df["created_at"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

# Ordina per data
df = df.sort_values(by="created_at", ascending=False)

# Calcola classifica
punteggi = pd.concat([
    df[['giocatore1', 'punti_g1']].rename(columns={'giocatore1': 'giocatore', 'punti_g1': 'punti'}),
    df[['giocatore2', 'punti_g2']].rename(columns={'giocatore2': 'giocatore', 'punti_g2': 'punti'})
])

classifica = punteggi.groupby('giocatore').sum().sort_values(by='punti', ascending=False).reset_index()

# Streamlit UI
st.title("Classifica Torneo")
st.dataframe(classifica)
