from dotenv import load_dotenv
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use a porta do Render ou 5000 como padrão
    app.run(host="0.0.0.0", port=port)

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
