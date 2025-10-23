
# Torneo Tennis Streamlit

Questa app consente di gestire un torneo di tennis tutti contro tutti con 12 giocatori.

## Funzionalità
- Inserimento risultati con punteggi completi (es. 6-4, 3-6, 7-5)
- Calcolo automatico del vincitore
- Classifica dinamica con punti:
  - 3 punti al vincitore
  - 1 punto al perdente se perde 2-1
  - 0 punti al perdente se perde 2-0

## Avvio locale
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy su Render
- Carica i file su GitHub
- Crea un Web Service su Render
- Usa `streamlit run app.py` come comando di avvio
