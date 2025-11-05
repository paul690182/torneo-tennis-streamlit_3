import zipfile

# Nome del file ZIP
zip_filename = "torneo_tennis.zip"

# File da includere
files = ["app.py", ".env.example", "requirements.txt"]

# Creazione ZIP
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for file in files:
        zipf.write(file)

print(f"✅ Pacchetto ZIP creato: {zip_filename}")
