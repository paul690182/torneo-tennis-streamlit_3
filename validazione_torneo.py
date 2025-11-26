
# -*- coding: utf-8 -*-
"""
validazione_torneo.py

Modulo per:
- Validazione punteggi dei set (1° e 2° set normali, 3° set long tie-break)
- Inserimento risultato con calcolo vincitore
- Aggiornamento dinamico della classifica
- Query SQL di verifica per Supabase
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

@dataclass
class Match:
    giocatore1: str
    giocatore2: str
    set1: Tuple[int, int]
    set2: Tuple[int, int]
    set3: Tuple[int, int]
    vincitore: Optional[str] = None

class ValidatoreTennis:
    @staticmethod
    def valida_set_normale(g1: int, g2: int) -> bool:
        if g1 == g2:
            return False
        m, n = (g1, g2) if g1 > g2 else (g2, g1)
        if m < 6 or m > 7:
            return False
        diff = m - n
        if m == 6 and diff < 2:
            return False
        if m == 7 and n < 5:  # consente 7-5 e 7-6
            return False
        return True

    @staticmethod
    def valida_long_tiebreak(g1: int, g2: int) -> bool:
        if g1 == g2:
            return False
        if not (0 <= g1 <= 20 and 0 <= g2 <= 20):
            return False
        if max(g1, g2) < 8:
            return False
        if abs(g1 - g2) < 2:
            return False
        return True

class TorneoTennis:
    def __init__(self) -> None:
        self.risultati: List[Match] = []
        self.classifica: Dict[str, int] = {}

    def _conteggia_set_vinti(self, set1, set2, set3) -> Tuple[int, int]:
        p1 = (1 if set1[0] > set1[1] else 0) + (1 if set2[0] > set2[1] else 0)
