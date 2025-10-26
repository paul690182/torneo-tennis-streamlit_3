
# Torneo Tennis - Streamlit App

Questa applicazione consente di gestire partite e classifiche di un torneo di tennis, con salvataggio su Supabase.

## 🚀 Funzionalità
- Inserimento partite con set e vincitore
- Calcolo automatico dei punteggi dai set
- Classifica aggiornata con punteggio personalizzato
- Salvataggio su Supabase

## 🧰 Requisiti
- Python >= 3.8
- Streamlit
- Pandas
- Supabase Python Client

## 📦 Installazione

1. Clona il repository:
```bash
git clone https://github.com/tuo-utente/torneo-tennis-streamlit.git
cd torneo-tennis-streamlit
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

## 🔐 Configurazione Supabase

Imposta le variabili d'ambiente nel tuo sistema o su Render:
```bash
export SUPABASE_URL="https://<tuo-progetto>.supabase.co"
export SUPABASE_KEY="<tua-chiave-api>"
```

Su Render, vai su **Environment > Environment Variables** e aggiungile manualmente.

## ▶️ Avvio locale
```bash
streamlit run app.py
```

## 🌐 Deploy su Render

1. Collega il repository GitHub a Render
2. Crea un nuovo servizio Web (Python)
3. Assicurati che `app.py` sia il file principale
4. Imposta le variabili d'ambiente
5. Attiva Auto-Deploy

## 📊 Sistema di punteggio
- 3 punti al vincitore per 2-0
- 3 punti al vincitore + 1 punto allo sconfitto per 2-1
- 0 punti per chi perde 0-2

## 📁 File principali
- `app.py`: codice principale Streamlit
- `requirements.txt`: dipendenze
- `README.md`: istruzioni

## 🧑‍💻 Autore
Giuseppe - torneo tennis 2025
