
import streamlit as st
from db import inserisci_partita, get_classifica, get_storico

st.set_page_config(page_title="Torneo Tennis", layout="centered")
st.title("🎾 Torneo di Tennis")

st.header("Inserisci Risultato Partita")

# Lista giocatori (puoi sostituirla con quella reale)
giocatori = [
    "Paolo R.", "Paola C.", "Francesco M.", "Massimo B.",
    "Daniele T.", "Simone V.", "Gianni F.", "Leo S.",
    "Maura F.", "Giovanni D.", "Andrea P.", "Maurizio P."
]

col1, col2 = st.columns(2)
with col1:
    giocatore1 = st.selectbox("Giocatore 1", giocatori)
with col2:
    giocatore2 = st.selectbox("Giocatore 2", [g for g in giocatori if g != giocatore1])

set1 = st.text_input("Set 1 (es. 6-4)")
set2 = st.text_input("Set 2 (es. 3-6)")
set3 = st.text_input("Set 3 (opzionale, es. 7-5)", value="")

if st.button("Salva Risultato"):
    try:
        inserisci_partita(giocatore1, giocatore2, set1, set2, set3)
        st.success("✅ Partita salvata correttamente!")
    except Exception as e:
        st.error(f"❌ Errore nel salvataggio: {e}")

st.header("📊 Classifica")
classifica = get_classifica()
if classifica and 'data' in classifica:
    st.table(classifica['data'])
else:
    st.info("Nessuna partita registrata.")

st.header("📜 Storico Partite")
storico = get_storico()
if storico and 'data' in storico:
    st.table(storico['data'])
else:
    st.info("Nessuna partita registrata.")
