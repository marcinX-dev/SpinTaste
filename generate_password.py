from werkzeug.security import generate_password_hash

# Zmień 'twoje_haslo' na hasło, którego chcesz użyć
password = 'Slodziak2202!'
hashed_password = generate_password_hash(password)
print(f"Zahashowane hasło: {hashed_password}")