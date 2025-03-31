from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('meals.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/random_meal', methods=['POST'])
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
def lista_przepisow():
    try:
        with get_db_connection() as conn:
            meals = conn.execute("SELECT * FROM meals").fetchall()
            return render_template('lista_przepisow.html', meals=meals)
    except Exception as e:
        return render_template('error.html', error=f"Błąd bazy danych: {str(e)}")

@app.route('/dodaj_posilek', methods=['GET', 'POST'])
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