from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

# Zmień 'twoje_haslo' na hasło, którego chcesz użyć
password = os.getenv('PASSWORD') 
hashed_password = generate_password_hash(password)
print(f"Zahashowane hasło: {hashed_password}")