import streamlit as st
from supabase import create_client
import datetime
from supabase_config import SUPABASE_URL, SUPABASE_KEY  # Import credenziali

# Connessione a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

lista_giocatori = [
    "Francesco M", "Pasquale V", "Paolo R", "Leo S", "Gianni F",
    "Simone", "Marco", "Riccardo"
]

st.title("Inserisci risultato partita")

# ✅ Selezione giocatori
giocatore1 = st.selectbox("Giocatore 1", lista_giocatori)
giocatore2 = st.selectbox("Giocatore 2", [g for g in lista_giocatori if g != giocatore1])

# ✅ Inserimento set
set1 = st.text_input("Set 1 (es. 6-3)")
set2 = st.text_input("Set 2 (es. 6-4)")
set3 = st.text_input("Set 3 (es. 7-5 o vuoto)")

# ✅ Calcolo automatico tipo vittoria e punti
def calcola_punti(set1, set2, set3):
    vittorie_g1 = 0
    vittorie_g2 = 0
    for s in [set1, set2, set3]:
        if s:
            g1, g2 = map(int, s.split("-"))
            if g1 > g2:
                vittorie_g1 += 1
            else:
                vittorie_g2 += 1
    tipo_vittoria = f"{vittorie_g1}-{vittorie_g2}"
    if vittorie_g1 == 2 and vittorie_g2 == 0:
        return tipo_vittoria, 3, 0
    elif vittorie_g1 == 2 and vittorie_g2 == 1:
        return tipo_vittoria, 3, 1
    elif vittorie_g2 == 2 and vittorie_g1 == 0:
        return tipo_vittoria, 0, 3
    elif vittorie_g2 == 2 and vittorie_g1 == 1:
        return tipo_vittoria, 1, 3
    return tipo_vittoria, 0, 0

if st.button("Salva risultato"):
    tipo_vittoria, punti_g1, punti_g2 = calcola_punti(set1, set2, set3)
    data = {
        "giocatore1": giocatore1,
        "giocatore2": giocatore2,
        "set1": set1,
        "set2": set2,
        "set3": set3,
        "tipo_vittoria": tipo_vittoria,
        "punti_g1": punti_g1,
        "punti_g2": punti_g2,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
    response = supabase.table("partite_advanced").insert(data).execute()
    st.success("Risultato inserito!")
    st.write(response.data)

# ✅ Mostra ultimi risultati
st.subheader("Ultimi risultati")
res = supabase.table("partite_advanced").select("*").order("created_at", desc=True).limit(10).execute()
for row in res.data:
    st.write(f"{row['created_at']} | {row['giocatore1']} vs {row['giocatore2']} | "
             f"Set: {row['set1']}, {row['set2']}, {row['set3']} | Punti: {row['punti_g1']} - {row['punti_g2']}")
