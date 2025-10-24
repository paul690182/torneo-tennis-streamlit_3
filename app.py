
import streamlit as st
import pandas as pd
import os

# Connessione al database: PostgreSQL se disponibile, altrimenti SQLite
try:
    import psycopg2
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ.get("DB_PORT", 5432)
    )
    c = conn.cursor()
    st.sidebar.success("Connesso a PostgreSQL")
    def execute_query(query, params=()):
        c.execute(query, params)
        conn.commit()
    def read_query(query):
        return pd.read_sql_query(query, conn)
except:
    import sqlite3
    conn = sqlite3.connect("torneo.db", check_same_thread=False)
    c = conn.cursor()
    st.sidebar.warning("Connessione a SQLite locale")
    def execute_query(query, params=()):
        c.execute(query, params)
        conn.commit()
    def read_query(query):
        return pd.read_sql_query(query, conn)

# Crea tabella se non esiste
execute_query("""
CREATE TABLE IF NOT EXISTS risultati (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    giocatore1 TEXT,
    giocatore2 TEXT,
    punteggio TEXT,
    vincitore TEXT
)
""")

st.title("Torneo Tennis - Tutti contro tutti")

# Lista giocatori
giocatori = [f"Giocatore {i}" for i in range(1, 13)]

# Inserimento risultato
st.header("Inserisci Risultato")
g1 = st.selectbox("Giocatore 1", giocatori)
g2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != g1])
punteggio = st.text_input("Punteggio (es. 6-4, 3-6, 7-5)")
vincitore = st.selectbox("Vincitore", [g1, g2])

if st.button("Salva Risultato"):
    execute_query(
        "INSERT INTO risultati (giocatore1, giocatore2, punteggio, vincitore) VALUES (?, ?, ?, ?)",
        (g1, g2, punteggio, vincitore)
    )
    st.success("Risultato salvato correttamente!")

# Classifica
st.header("Classifica")
df = read_query("SELECT * FROM risultati")

classifica = {g: {"Partite": 0, "Vittorie": 0, "Set Vinti": 0, "Set Persi": 0, "Punti": 0} for g in giocatori}

for _, row in df.iterrows():
    g1, g2, punteggio, vincitore = row["giocatore1"], row["giocatore2"], row["punteggio"], row["vincitore"]
    set_g1, set_g2 = 0, 0
    for s in punteggio.split(","):
        try:
            p1, p2 = map(int, s.strip().split("-"))
            if p1 > p2:
                set_g1 += 1
            else:
                set_g2 += 1
        except:
            continue

    classifica[g1]["Partite"] += 1
    classifica[g2]["Partite"] += 1
    classifica[g1]["Set Vinti"] += set_g1
    classifica[g1]["Set Persi"] += set_g2
    classifica[g2]["Set Vinti"] += set_g2
    classifica[g2]["Set Persi"] += set_g1
    classifica[vincitore]["Vittorie"] += 1

    perdente = g2 if vincitore == g1 else g1

    if (set_g1 == 2 and set_g2 == 0) or (set_g2 == 2 and set_g1 == 0):
        classifica[vincitore]["Punti"] += 3
        classifica[perdente]["Punti"] += 0
    elif (set_g1, set_g2) in [(2, 1), (1, 2)]:
        classifica[vincitore]["Punti"] += 1
        classifica[perdente]["Punti"] += 1

df_classifica = pd.DataFrame.from_dict(classifica, orient="index")
st.dataframe(df_classifica.sort_values(by=["Punti", "Vittorie"], ascending=False))

conn.close()
