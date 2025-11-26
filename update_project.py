
import streamlit as st
from supabase import create_client
from supabase_config import SUPABASE_URL, SUPABASE_KEY
import re
import os

st.title("🔧 Manutenzione Torneo Tennis")
st.write("Questa pagina permette di rimuovere Paola e Maura dal girone advanced e aggiornare la regola del 3° set.")

# Connessione a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if st.button("Esegui manutenzione"):
    try:
        # === RIMOZIONE GIOCATORI ===
        giocatori_da_rimuovere = ["Paola", "Maura"]
        for nome in giocatori_da_rimuovere:
            supabase.table('classifica_advanced').delete().eq('giocatore', nome).execute()
            supabase.table('partite_advanced').delete().or_(f"player1.eq.{nome},player2.eq.{nome}", '').execute()
            supabase.table('risultati_advanced').delete().eq('giocatore', nome).execute()
        st.success("✅ Paola e Maura rimosse dal girone advanced e dalle partite/risultati.")

        # === AGGIORNAMENTO FILE inserisci_risultato.py ===
        file_path = "pages/inserisci_risultato.py"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Aggiungi funzione di validazione se non presente
            if "def valida_super_tiebreak" not in content:
                funzione_validazione = """
def valida_super_tiebreak(p1: int, p2: int) -> tuple[bool, str]:
    \"\"\"
    Regole 3 set (super tie-break):
    - Vince chi arriva a >= 8 punti con differenza >= 2.
    - Il vincitore non può superare 20.
    \"\"\"
    if p1 < 0 or p2 < 0:
        return False, "I punti devono essere >= 0"

    winner = max(p1, p2)
    loser = min(p1, p2)
    diff = abs(p1 - p2)

    if winner < 8:
        return False, "Il 3 set può terminare solo da 8 punti in su per il vincitore."
    if winner > 20:
        return False, "Il 3 set non può superare 20 punti."
    if diff < 2:
        return False, "Il 3 set deve terminare con almeno 2 punti di differenza."
    if winner == 20 and loser > 18:
        return False, "A 20 punti del vincitore, il perdente deve essere al massimo 18 (es. 20-18)."

    return True, ""
"""
                content = funzione_validazione + "\n" + content

            # Aggiorna i campi di input per il 3° set con max_value=20
            content = re.sub(r'st\\.number_input\\("Punti 3.*?\\)',
                             'st.number_input("Punti 3° set", min_value=0, max_value=20, step=1)',
                             content)

            # Inserisci validazione prima del salvataggio
            if "valida_super_tiebreak" in content and "tie_ok" not in content:
                blocco_validazione = """
# Validazione punteggio 3° set prima di salvare
tie_ok, tie_msg = valida_super_tiebreak(set3_p1, set3_p2)
if not tie_ok:
    st.error(f"Punteggio 3° set non valido: {tie_msg}")
    st.stop()
"""
                content = content.replace("supabase.table", blocco_validazione + "\nsupabase.table")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            st.success("✅ File inserisci_risultato.py aggiornato con regola super tie-break.")
        else:
            st.error("❌ File inserisci_risultato.py non trovato.")
    except Exception as e:
        st.error(f"Errore durante la manutenzione: {e}")
