from flask import Flask, render_template, redirect, request, session, url_for, flash
import mysql.connector
import os
from dotenv import load_dotenv
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path = env_path)


app = Flask(__name__)
app.debug = True

app.secret_key = os.getenv("SECRET_KEY")

def get_db():
    return mysql.connector.connect(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        database = os.getenv("DB_NAME")
    )



@app.route('/')
def default():
    return redirect("/home")

@app.route('/home')
def home():
    db = get_db();
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    cur.close()
    db.close()
    return render_template("Home.html", items = items)

@app.route('/checkout', methods = ["GET", "POST"])
def checkout():
    #initial cart loading procces
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    #form request
    if request.method == "POST":
        db = get_db()
        cur = db.cursor(dictionary=True)

        try:
            cur.execute("SELECT items.item_id, cart_items.quantity as quantity, price "
                f"FROM items JOIN cart_items "
                f"ON cart_items.item_id = items.item_id "
                f"WHERE user_id = {user_id};")
            items = cur.fetchall()

            cur.execute(f"INSERT INTO transactions (user_id, time) "
                f"VALUES ({user_id}, \"{datetime.now().replace(microsecond=0)}\");")
            transaction_id = cur.lastrowid
            db.commit()

            for item in items:
                item_id = item['item_id']
                quantity = item['quantity']
                price = item['price']

                cur.execute(f"INSERT INTO transaction_items (transaction_id, item_id, price, quantity) "
                    f"VALUES ({transaction_id}, {item_id}, {price}, {quantity});")

                cur.execute(f"UPDATE items "
                    f"SET quantity = quantity - {quantity} "
                    f"WHERE item_id = {item_id};")

            cur.execute(f"DELETE FROM cart_items WHERE user_id = {user_id};")
            db.commit()

        finally:
            print(cur.fetchall())

            cur.close()
            db.close()

    # Load cart items
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute("""SELECT i.item_id, i.name, i.price, c.quantity FROM cart_items c JOIN items i ON c.item_id = i.item_id WHERE c.user_id = %s""", (user_id,))

    cart_items = cur.fetchall()
    cur.close()
    db.close()

    return render_template("checkout.html", cart_items=cart_items)

@app.route('/contact')
def contact():
    return render_template("Contact-Info.html")

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    db = get_db();
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM users where email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    db.close()

    if not user:
        return "Invalid email or password", 401

    if not check_password_hash(user['password'], password):
        return "Invalid email or password", 401

    session['user_id'] = user['user_id']
    session['username'] = user['username']

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/signup')
def signup():
    return render_template("signUp.html")

@app.route('/signupform', methods=['POST'])
def signupform():
    username = request.form['username']
    first_name = request.form['FirstName']
    last_name = request.form['LastName']
    street = request.form['streetAddress']
    city = request.form['city']
    state = request.form['state']
    zip_code = request.form['zipCode']
    country = request.form['country']
    gender = request.form['gender']
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirmPassword']
    terms = request.form.get('terms')

    if password != confirm:
        return "Password do not match", 400

    if not terms:
        return "You must agree to the terms", 400

    hashed = generate_password_hash(password)

    db = get_db();
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("INSERT INTO users (username, email, password, first_name, last_name, street, city, state, zip_code, country, gender) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (username, email, hashed, first_name, last_name, street, city, state, zip_code, country, gender))
        db.commit()
    except mysql.connector.errors.IntegrityError:
        return "Username or email already exists", 400

    finally:
        cur.close()
        db.close()

    return redirect(url_for('home'))

@app.route('/addtocart/<int:item_id>', methods=['POST'])
def addtocart(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        quantitty_items = get_quantitty_items(item_id)
        quantitty_cart  = get_quantitty_cart(user_id, item_id)

        if quantitty_cart >= quantitty_items:
            flash("No dice of that type available", "failure")
            return redirect(url_for('home'))

        cur.execute("""INSERT INTO cart_items (user_id, item_id, quantity) VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE quantity = quantity + 1; """, (user_id, item_id))
        db.commit()

    except mysql.connector.Error as e:
        return f"Database error: {e}", 400

    finally:
        cur.close()
        db.close()

    flash("Item added to cart!", "success")
    return redirect(url_for('home'))

@app.route('/delete_from_cart/<int:item_id>', methods=['POST'])
def delete_from_cart(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            "DELETE FROM cart_items WHERE user_id = %s AND item_id = %s",
            (user_id, item_id)
        )
        db.commit()
        flash("Item removed from cart.", "warning")
    except mysql.connector.Error:
        flash("Could not delete item.", "danger")
    finally:
        cur.close()
        db.close()

    return redirect(url_for('checkout'))

def get_quantitty_cart(user_id, item_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("SELECT quantity FROM cart_items WHERE user_id = %s AND item_id = %s; ",(user_id, item_id))
        row = cur.fetchone()
    finally:
        cur.close()
        db.close()

    return row['quantity'] if row else 0

def get_quantitty_items(item_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("SELECT quantity FROM items WHERE item_id = %s; ", (item_id,))
        row = cur.fetchone()
    finally:
        cur.close()
        db.close()

    return row['quantity'] if row else 0


if __name__ == "__main__":
    app.run(debug=True)

