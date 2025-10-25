
from supabase import create_client, Client
from datetime import date

SUPABASE_URL = "https://urrkxfohjpsdxlzicsye.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVycmt4Zm9oanBzZHhsemljc3llIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEzMjY4OTcsImV4cCI6MjA3NjkwMjg5N30.7kn4pX-sunIYkeP35lzK57nCvI4HoSqwjGu8j0ZOvRk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def calcola_punti(set1, set2, set3):
    punteggi = [set1, set2] + ([set3] if set3 else [])
    g1_vinti = sum(int(s.split('-')[0]) > int(s.split('-')[1]) for s in punteggi)
    g2_vinti = len(punteggi) - g1_vinti

    if g1_vinti == 2 and g2_vinti == 0:
        return 3, 0
    elif g1_vinti == 2 and g2_vinti == 1:
        return 3, 1
    elif g1_vinti == 1 and g2_vinti == 2:
        return 1, 3
    elif g1_vinti == 0 and g2_vinti == 2:
        return 0, 3
    return 0, 0

def inserisci_partita(g1, g2, set1, set2, set3):
    p1, p2 = calcola_punti(set1, set2, set3)
    vincitore = g1 if p1 > p2 else g2
    supabase.table("partite_classifica").insert({
        "giocatore1": g1,
        "giocatore2": g2,
        "set1": set1,
        "set2": set2,
        "set3": set3,
        "vincitore": vincitore,
        "punteggio_g1": p1,
        "punteggio_g2": p2,
        "data_partita": date.today().isoformat()
    }).execute()

def get_classifica():
    query = """
    SELECT giocatore, SUM(punti) AS totale_punti, COUNT(*) AS partite_giocate
    FROM (
        SELECT giocatore1 AS giocatore, punteggio_g1 AS punti FROM partite_classifica
        UNION ALL
        SELECT giocatore2 AS giocatore, punteggio_g2 AS punti FROM partite_classifica
    ) AS unione
    GROUP BY giocatore
    ORDER BY totale_punti DESC;
    """
    return supabase.rpc("execute_sql", {"sql": query})

def get_storico():
    return supabase.table("partite_classifica").select("*").order("data_partita", desc=True).execute()
