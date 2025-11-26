
import streamlit as st
from supabase import create_client
from supabase_config import SUPABASE_URL, SUPABASE_KEY
import os
import re

st.title("🔧 Manutenzione Torneo Tennis")
st.write(
    "Questa pagina rimuove **Paola** e **Maura** dal girone advanced e aggiorna la regola del 3° set (super tie-break)."
)

# Connessione a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

GIOCATORI_DA_RIMUOVERE = ["Paola", "Maura"]

def get_columns(table_name: str):
    """Ritorna l'elenco colonne della tabella prendendo una riga di esempio."""
    try:
        resp = supabase.table(table_name).select("*").limit(1).execute()
        if resp.data:
            return list(resp.data[0].keys())
        return []
    except Exception as e:
        st.error(f"Errore nel leggere colonne da '{table_name}': {e}")
        return []

def delete_rows_by_name(table_name: str, possible_name_cols: list[str], names: list[str]):
    """Prova a cancellare righe da table_name usando una delle colonne nome fornite."""
    cols = get_columns(table_name)
    if not cols:
        st.info(f"Tabella '{table_name}' vuota o non leggibile.")
        return
    used = None
    for c in possible_name_cols:
        if c in cols:
            for n in names:
                supabase.table(table_name).delete().eq(c, n).execute()
            used = c
            break
    if used:
        st.success(f"✅ Cancellate righe da '{table_name}' usando colonna '{used}'.")
    else:
        st.warning(f"⚠️ In '{table_name}' non trovata nessuna tra {possible_name_cols}. Colonne presenti: {cols}")

def remove_from_partite_advanced(names: list[str]):
    """
    Gestisce entrambi i modelli:
    - Modello righe: colonne (player1, player2) o (giocatore1, giocatore2) → DELETE con or().
    - Modello pivot: colonna per ogni giocatore (paola, maura, ...) → azzera/NULL su tutte le righe.
    """
    cols = get_columns("partite_advanced")
    if not cols:
        st.info("Tabella 'partite_advanced' vuota: nulla da rimuovere.")
        return

    # Caso A: modello righe con coppia di colonne per i giocatori
    pairs = [("player1", "player2"), ("giocatore1", "giocatore2"), ("p1", "p2")]
    pair_found = None
    for a, b in pairs:
        if a in cols and b in cols:
            pair_found = (a, b)
            break

    if pair_found:
        a, b = pair_found
        for nome in names:
            # PostgREST or syntax: or(colA.eq.value,colB.eq.value) senza spazi
            filter_str = f"{a}.eq.{nome},{b}.eq.{nome}"
            supabase.table('partite_advanced').delete().or_(filter_str, "").execute()
        st.success(f"✅ Partite rimosse in 'partite_advanced' usando colonne '{a}', '{b}'.")
        return

    # Caso B: modello pivot — colonne con nomi dei giocatori
    lower_names = [n.lower() for n in names]
    to_clear = [c for c in cols if c.lower() in lower_names]
    if not to_clear:
        st.warning(f"⚠️ Modello pivot ipotizzato, ma non ho trovato colonne per {names}. Colonne: {cols}")
        return

    # Recupera tutte le righe per aggiornare riga per riga
    try:
        data = supabase.table('partite_advanced').select("*").execute().data
    except Exception as e:
        st.error(f"Errore nel leggere 'partite_advanced': {e}")
        return

    if not data:
        st.info("Nessuna riga in 'partite_advanced'.")
        return

    id_col = "id" if "id" in cols else None
    updated_count = 0
    for row in data:
        payload = {}
        for c in to_clear:
            v = row.get(c)
            if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
                payload[c] = 0
            else:
                payload[c] = None
        try:
            if id_col:
                supabase.table('partite_advanced').update(payload).eq(id_col, row[id_col]).execute()
                updated_count += 1
            else:
                # Se non esiste una chiave 'id', non facciamo update completo (potrebbe non funzionare senza filtro).
                pass
        except Exception:
            pass

    if updated_count > 0:
        st.success(f"✅ Azzerate/NULL le colonne {', '.join(to_clear)} su {updated_count} righe di 'partite_advanced'.")
    else:
        st.warning("⚠️ Nessuna riga aggiornata (manca colonna 'id' o update non supportato senza filtro).")

def patch_inserisci_risultato():
    """Aggiunge validazione del 3° set (super tie-break max 20, diff ≥ 2) e blocco salvataggio."""
    file_path = "pages/inserisci_risultato.py"
    if not os.path.exists(file_path):
        st.error("❌ 'pages/inserisci_risultato.py' non trovato.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    added = False

    # Funzione di validazione
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
        added = True

    # Limita gli input del 3° set (se usi number_input)
    content = re.sub(
        r'st\.number_input\("Punti 3.*?\)',
        'st.number_input("Punti 3° set", min_value=0, max_value=20, step=1)',
        content
    )

    # Inserisci validazione prima del salvataggio (se non già presente)
    if "valida_super_tiebreak" in content and "tie_ok" not in content:
        blocco_validazione = """
# Validazione punteggio 3° set prima di salvare
tie_ok, tie_msg = valida_super_tiebreak(set3_p1, set3_p2)
if not tie_ok:
    st.error(f"Punteggio 3° set non valido: {tie_msg}")
    st.stop()
"""
        # Inseriamo il blocco appena prima della prima chiamata a supabase.table
        content = content.replace("supabase.table", blocco_validazione + "\nsupabase.table")
        added = True

    if added:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        st.success("✅ Regola super tie-break applicata in 'pages/inserisci_risultato.py'.")
    else:
        st.info("ℹ️ Nessuna modifica necessaria in 'pages/inserisci_risultato.py' (già patchato).")

if st.button("Esegui manutenzione"):
    try:
        # 1) classifica_advanced e risultati_advanced
        delete_rows_by_name("classifica_advanced", ["giocatore", "nome", "player"], GIOCATORI_DA_RIMUOVERE)
        delete_rows_by_name("risultati_advanced", ["giocatore", "nome", "player"], GIOCATORI_DA_RIMUOVERE)

        # 2) partite_advanced (gestione robusta di schema)
        remove_from_partite_advanced(GIOCATORI_DA_RIMUOVERE)

        # 3) Patch regola 3° set
        patch_inserisci_risultato()

        st.success("🎉 Manutenzione completata.")
    except Exception as e:
        st.error(f"Errore durante la manutenzione: {e}")


