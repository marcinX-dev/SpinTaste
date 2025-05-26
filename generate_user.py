import sqlite3

def create_user_table():
    conn = sqlite3.connect('meals.db')
    cursor = conn.cursor()
    
    # Tworzenie tabeli użytkowników, jeśli nie istnieje
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Sprawdzamy czy już istnieje użytkownik admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'karolina'")
    admin_exists = cursor.fetchone()[0] > 0
    
    if not admin_exists:
        # Wstawiamy domyślnego użytkownika (admin)
        # Hasło jest już zahaszowane (z pliku generate_password.py)
        cursor.execute("""
        INSERT INTO users (username, password) 
        VALUES ('karolina', 'scrypt:32768:8:1$hf994dbdhdqUWfoK$c2d84264df28b5e70de6a64ce481be64141a575b1458344d846db4ef11383d1bd549909e8c2a28737117c55adbfc659f0eb55ace42e54ef23cf943d8b0f7bfbb')
        """)
    
    conn.commit()
    conn.close()
    print("Zrobiono")

if __name__ == "__main__":
    create_user_table()