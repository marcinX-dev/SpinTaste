from flask import Flask, render_template, request, jsonify
import sqlite3
import random

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('meals.db')
    conn.row_factory = sqlite3.Row
    return conn
#test
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/random_meal', methods=['POST'])
def random_meal():
    data = request.get_json()
    category = data.get('category', None)  

    if not category:
        return jsonify({"error": "Brak kategorii w żądaniu."}), 400

    conn = get_db_connection()
    meals = conn.execute(
        "SELECT * FROM meals WHERE category = ?",
        (category,)
    ).fetchall()
    conn.close()

    if not meals:
        return jsonify({"error": f"Brak posiłków w kategorii: {category}"}), 404

    chosen = random.choice(meals)
 
    meal_data = {
        "id": chosen["id"],
        "name": chosen["name"],
        "ingredients": chosen["ingredients"],
        "preparation": chosen["preparation"],
        "category": chosen["category"]
    }
    return jsonify(meal_data), 200

@app.route('/lista_przepisow')
def lista_przepisow():
    conn = get_db_connection()
    meals = conn.execute("SELECT * FROM meals").fetchall()
    conn.close()
    return render_template('lista_przepisow.html', meals=meals)

if __name__ == '__main__':
    app.run(debug=True)
