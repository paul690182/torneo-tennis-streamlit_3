import streamlit as st
from supabase import create_client
import datetime
from supabase_config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

torneo = st.selectbox("Seleziona torneo", ["Advanced", "Top"], key="torneo")

giocatori_advanced = ["Pasquale V.", "Gabriele T.", "Cris Capparoni", "Stefano C.", "Roberto A.", "Susanna", "Maura","Paolo Mattioli", "Paola Colonna", "Paolo Rosi", "Michele", "Daniele M.", "Stefano D. R.", "Pino","Gianni", "Leonardo", "Francesco M.", "Leonardino", "Federico", "Luca", "Adriano"]

giocatori_top = ["Simone", "Maurizio P.", "Marco", "Riccardo", "Massimo", "Cris Cosso", "Giovanni", "Andrea P.","Giuseppe", "Salvatore", "Paolo Mattioli", "Paola Colonna", "Leonardo", "Francesco M."]

lista_giocatori = giocatori_advanced if torneo == "Advanced" else giocatori_top
tabella_partite = "partite_advanced" if torneo == "Advanced" else "partite_top"
tabella_classifica = "classifica_advanced" if torneo == "Advanced" else "classifica_top"

st.title(f"Inserisci risultato ({torneo})")

giocatore1 = st.selectbox("Giocatore 1", lista_giocatori, key="giocatore1")
giocatore2 = st.selectbox("Giocatore 2", [g for g in lista_giocatori if g != giocatore1], key="giocatore2")

set1 = st.text_input("Set 1 (es. 6-3)")
set2 = st.text_input("Set 2 (es. 6-4)")
set3 = st.text_input("Set 3 (opzionale, es. 7-5)")

def valida_set(s):
    if not s:
        return True
    try:
        g1, g2 = map(int, s.split("-"))
        if g1 == g2:
            return False
        if max(g1, g2) < 6:
            return False
        if max(g1, g2) == 6 and abs(g1 - g2) >= 2:
            return True
        if max(g1, g2) == 7 and abs(g1 - g2) in [1, 2]:
            return True
        return False
    except:
        return False

def calcola_punti_e_vincitore(set1, set2, set3, giocatore1, giocatore2):
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
    vincitore = giocatore1 if vittorie_g1 > vittorie_g2 else giocatore2

    if vittorie_g1 == 2 and vittorie_g2 == 0:
        return tipo_vittoria, 3, 0, vincitore
    elif vittorie_g1 == 2 and vittorie_g2 == 1:
        return tipo_vittoria, 3, 1, vincitore
    elif vittorie_g2 == 2 and vittorie_g1 == 0:
        return tipo_vittoria, 0, 3, vincitore
    elif vittorie_g2 == 2 and vittorie_g1 == 1:
        return tipo_vittoria, 1, 3, vincitore
    return tipo_vittoria, 0, 0, vincitore

def aggiorna_classifica(giocatore, punti):
    res = supabase.table(tabella_classifica).select("*").eq("giocatore", giocatore).execute()
    if len(res.data) == 0:
        supabase.table(tabella_classifica).insert({"giocatore": giocatore, "punti": punti}).execute()
    else:
        punti_attuali = res.data[0]["punti"]
        supabase.table(tabella_classifica).update({"punti": punti_attuali + punti}).eq("giocatore", giocatore).execute()

if st.button("Salva risultato"):
    if not giocatore2:
        st.error("Seleziona il secondo giocatore!")
    elif not (valida_set(set1) and valida_set(set2) and valida_set(set3)):
        st.error("Errore nei punteggi dei set! Controlla il formato e le regole (es. 6-4, 7-5).")
    else:
        tipo_vittoria, punti_g1, punti_g2, vincitore = calcola_punti_e_vincitore(set1, set2, set3, giocatore1, giocatore2)
        data = {"giocatore1": giocatore1,"giocatore2": giocatore2,"set1": set1,"set2": set2,"set3": set3,"tipo_vittoria": tipo_vittoria,"punti_g1": punti_g1,"punti_g2": punti_g2,"vincitore": vincitore,"created_at": datetime.datetime.utcnow().isoformat()}
        response = supabase.table(tabella_partite).insert(data).execute()
        st.success("Risultato inserito!")
        st.write(response.data)

        aggiorna_classifica(giocatore1, punti_g1)
        aggiorna_classifica(giocatore2, punti_g2)

        st.experimental_rerun()

st.subheader(f"Ultimi risultati ({torneo})")
res = supabase.table(tabella_partite).select("*").order("created_at", desc=True).limit(10).execute()
for row in res.data:
    st.write(f"{row['created_at']} | {row['giocatore1']} vs {row['giocatore2']} | Set: {row['set1']}, {row['set2']}, {row['set3']} | Punti: {row['punti_g1']} - {row['punti_g2']} | Vincitore: {row['vincitore']}")

st.subheader(f"Classifica {torneo}")
classifica = supabase.table(tabella_classifica).select("*").order("punti", desc=True).execute()
st.table(classifica.data)
