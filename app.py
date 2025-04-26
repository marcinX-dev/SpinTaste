from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import random
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')  

# Konfiguracja Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Strona, do której przekieruje, gdy użytkownik nie jest zalogowany

# Klasa użytkownika dla Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# Funkcja do ładowania użytkownika dla Flask-Login
@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    
    if user:
        return User(user['id'], user['username'], user['password'])
    return None

def get_db_connection():
    conn = sqlite3.connect('meals.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            # Zaloguj użytkownika
            user_obj = User(user['id'], user['username'], user['password'])
            login_user(user_obj, remember=remember)
            
            # Przekierowanie po zalogowaniu
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            error = "Nieprawidłowa nazwa użytkownika lub hasło"
    
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostałeś wylogowany')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/random_meal', methods=['POST'])
@login_required
def random_meal():
    data = request.get_json()
    category = data.get('category', None)  

    if not category:
        return jsonify({"error": "Brak kategorii w żądaniu."}), 400

    try:
        with get_db_connection() as conn:
            meals = conn.execute(
                "SELECT * FROM meals WHERE category = ?",
                (category,)
            ).fetchall()
            
            if not meals:
                return jsonify({"error": f"Brak posiłków w kategorii: {category}"}), 404
                
            chosen = random.choice(meals)
            
            meal_data = {
                "id": chosen["id"],
                "name": chosen["name"],
                "ingredients": chosen["ingredients"],
                "recipe": chosen["recipe"],
                "category": chosen["category"]
            }
            return jsonify(meal_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/lista_przepisow')
@login_required
def lista_przepisow():
    try:
        with get_db_connection() as conn:
            meals = conn.execute("SELECT * FROM meals").fetchall()
            return render_template('lista_przepisow.html', meals=meals)
    except Exception as e:
        return render_template('error.html', error=f"Błąd bazy danych: {str(e)}")

@app.route('/dodaj_posilek', methods=['GET', 'POST'])
@login_required
def dodaj_posilek():
    if request.method == 'POST':
        name = request.form.get('name')
        ingredients = request.form.get('ingredients')
        recipe = request.form.get('recipe')
        category = request.form.get('category')
        goals = request.form.get('goals', '')  # Opcjonalne pole
        
        # Walidacja danych
        if not name or not ingredients or not recipe or not category:
            return render_template('dodaj_posilek.html', error="Wszystkie wymagane pola muszą być wypełnione!")
        
        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO meals (name, ingredients, recipe, category, goals) VALUES (?, ?, ?, ?, ?)",
                    (name, ingredients, recipe, category, goals)
                )
                conn.commit()
                return render_template('dodaj_posilek.html', success=True)
        except Exception as e:
            return render_template('dodaj_posilek.html', error=f"Wystąpił błąd podczas dodawania posiłku: {e}")
    
    return render_template('dodaj_posilek.html')

@app.route('/usun_przepis/<int:recipe_id>', methods=['POST'])
@login_required
def usun_przepis(recipe_id):
    try:
        with get_db_connection() as conn:
            # Sprawdzamy, czy przepis istnieje
            recipe = conn.execute("SELECT * FROM meals WHERE id = ?", (recipe_id,)).fetchone()
            
            if recipe is None:
                return jsonify({"error": "Przepis nie istnieje"}), 404
            
            # Usuwamy przepis
            conn.execute("DELETE FROM meals WHERE id = ?", (recipe_id,))
            conn.commit()
            return jsonify({"success": True, "message": "Przepis został usunięty"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)