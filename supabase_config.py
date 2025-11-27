
from supabase import create_client
import os
from dotenv import load_dotenv

# Carica .env solo in locale
if os.path.exists(".env"):
    load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Variabili d'ambiente mancanti: SUPABASE_URL e/o SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
