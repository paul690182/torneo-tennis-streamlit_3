
import streamlit as st

def test_viste(supabase):
    # Test rapido per verificare che le viste siano leggibili
    supabase.table("classifica_top").select("*").limit(1).execute()
    supabase.table("classifica_advanced").select("*").limit(1).execute()

def get_classifica(supabase, girone: str):
    view = "classifica_top" if girone == "Top" else "classifica_advanced"
    resp = supabase.table(view).select("*")\
        .order("punti", desc=True).order("nome", desc=False).execute()
    return resp.data or []

def calcola_punti_e_winner(s1_p1, s1_p2, s2_p1, s2_p2, s3_p1=None, s3_p2=None):
    v1 = (1 if s1_p1 > s1_p2 else 0) + (1 if s2_p1 > s2_p2 else 0) + (1 if (s3_p1 is not None and s3_p2 is not None and s3_p1 > s3_p2) else 0)
    v2 = (1 if s1_p2 > s1_p1 else 0) + (1 if s2_p2 > s2_p1 else 0) + (1 if (s3_p1 is not None and s3_p2 is not None and s3_p2 > s3_p1) else 0)
    winner = "p1" if v1 > v2 else ("p2" if v2 > v1 else None)
    if v1 == 2 and v2 == 0: return winner, 3, 0
    if v2 == 2 and v1 == 0: return winner, 0, 3
    if winner == "p1": return winner, 2, 1
    if winner == "p2": return winner, 1, 2
    return winner, 0, 0

def inserisci_match(supabase, girone, p1, p2, s1_p1, s1_p2, s2_p1, s2_p2, s3_p1=None, s3_p2=None):
    winner, points_p1, points_p2 = calcola_punti_e_winner(s1_p1, s1_p2, s2_p1, s2_p2, s3_p1, s3_p2)
    payload = {
        "girone": girone,
        "player1": p1, "player2": p2,
        "winner": (p1 if winner == "p1" else (p2 if winner == "p2" else None)),
        "points_p1": points_p1, "points_p2": points_p2,
        "set1_p1": s1_p1, "set1_p2": s1_p2,
        "set2_p1": s2_p1, "set2_p2": s2_p2,
        "set3_p1": s3_p1, "set3_p2": s3_p2,
    }
    return supabase.table("matches").insert(payload).execute()
