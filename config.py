from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações do MongoDB
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
