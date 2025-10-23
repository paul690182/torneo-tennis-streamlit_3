
# Torneo Tennis Streamlit

Questa applicazione consente di gestire un torneo di tennis tutti contro tutti con 12 giocatori.

## Funzionalità
- Inserimento risultati con punteggi completi (es. 6-4, 3-6, 7-5)
- Calcolo automatico della classifica
- Visualizzazione dinamica dei dati
- Salvataggio su database SQLite condivisibile

## Avvio locale
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy su Render
- Carica i file su GitHub
- Crea un Web Service su Render
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app.py --server.port=10000 --server.address=0.0.0.0`
```
