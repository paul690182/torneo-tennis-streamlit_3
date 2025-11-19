import streamlit as st
from supabase import create_client
import datetime
from supabase_config import SUPABASE_URL, SUPABASE_KEY

# Connessione a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ✅ Selezione torneo
torneo = st.selectbox("Seleziona torneo", ["Advanced", "Top"])

# ✅ Liste giocatori per ogni torneo
giocatori_advanced = [
    "Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.", "Roberto A.", "Susanna", "Maura",
    "Paolo Mattioli", "Paola Colonna", "Paolo Rosi", "Michele", "Daniele M.", "Stefano D. R.", "Pino",
    "Gianni", "Leonardo", "Francesco M.", "Leonardino", "Federico", "Luca", "Adriano"
]

giocatori_top = [
    "Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo", "Cris Cosso", "Giovanni", "Andrea P.",
    "Giuseppe", "Salvatore"
]

lista_giocatori = giocatori_advanced if torneo == "Advanced" else giocatori_top
tabella = "partite_advanced" if torneo == "Advanced" else "partite_top"

st.title(f"Inserisci risultato ({torneo})")

# ✅ Selezione giocatori
giocatore1 = st.selectbox("Giocatore 1", lista_giocatori, key="giocatore1")
giocatore2 = st.selectbox(
    "Giocatore 2",
    [g for g in lista_giocatori if g != giocatore1],
    key="giocatore2"
)

# ✅ Debug visivo
st.write(f"DEBUG → Giocatore 1: {giocatore1}, Giocatore 2: {giocatore2}")

# ✅ Inserimento set
set1 = st.text_input("Set 1 (es. 6-3)")
set2 = st.text_input("Set 2 (es. 6-4)")
set3 = st.text_input("Set 3 (opzionale, es. 7-5)")

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

# ✅ Funzione per aggiornare la classifica

def aggiorna_classifica(giocatore, punti):
    res = supabase.table("classifica").select("*").eq("giocatore", giocatore).execute()
    if len(res.data) == 0:
        supabase.table("classifica").insert({"giocatore": giocatore, "punti": punti}).execute()
    else:
        punti_attuali = res.data[0]["punti"]
        supabase.table("classifica").update({"punti": punti_attuali + punti}).eq("giocatore", giocatore).execute()

if st.button("Salva risultato"):
    if not giocatore2:
        st.error("Seleziona il secondo giocatore!")
    else:
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
        response = supabase.table(tabella).insert(data).execute()
        st.success("Risultato inserito!")
        st.write(response.data)

        # Aggiorna classifica
        aggiorna_classifica(giocatore1, punti_g1)
        aggiorna_classifica(giocatore2, punti_g2)

        # Reset form
        st.experimental_rerun()

# ✅ Mostra ultimi risultati
st.subheader(f"Ultimi risultati ({torneo})")
res = supabase.table(tabella).select("*").order("created_at", desc=True).limit(10).execute()
for row in res.data:
    st.write(f"{row['created_at']} | {row['giocatore1']} vs {row['giocatore2']} | "
             f"Set: {row['set1']}, {row['set2']}, {row['set3']} | Punti: {row['punti_g1']} - {row['punti_g2']}")

# ✅ Mostra classifica aggiornata
st.subheader("Classifica aggiornata")
classifica = supabase.table("classifica").select("*").order("punti", desc=True).execute()
st.table(classifica.data)
