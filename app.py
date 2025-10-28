
import os
from supabase import create_client, Client

# --- Connessione a Supabase ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Funzione per calcolare i punti ---
def calcola_punti(set1, set2, set3):
    g1_vinti = sum([int(s.split('-')[0]) > int(s.split('-')[1]) for s in [set1, set2, set3] if s])
    g2_vinti = sum([int(s.split('-')[1]) > int(s.split('-')[0]) for s in [set1, set2, set3] if s])

    if g1_vinti == 2 and g2_vinti == 0:
        return (3, 0)
    elif g2_vinti == 2 and g1_vinti == 0:
        return (0, 3)
    elif g1_vinti == 2 and g2_vinti == 1:
        return (3, 1)
    elif g2_vinti == 2 and g1_vinti == 1:
        return (1, 3)
    else:
        return (0, 0)

# --- Recupera tutte le partite ---
response = supabase.table("partite_completo").select("*").execute()
partite = response.data

# --- Aggiorna ogni riga con punti calcolati se mancanti ---
for partita in partite:
    if 'punti_g1' not in partita or 'punti_g2' not in partita:
        set1 = partita.get("set1", "")
        set2 = partita.get("set2", "")
        set3 = partita.get("set3", "")
        punti_g1, punti_g2 = calcola_punti(set1, set2, set3)
        supabase.table("partite_completo").update({
            "punti_g1": punti_g1,
            "punti_g2": punti_g2
        }).eq("id", partita["id"]).execute()

print("Aggiornamento completato.")
