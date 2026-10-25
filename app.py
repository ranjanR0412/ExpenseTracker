from flask import Flask, render_template, request, flash, redirect, url_for, session
from db_Connection import get_db_connection
import re


app = Flask(__name__)

app.secret_key = "super_secret_key_123"

@app.route("/")
def home():
    return render_template("register.html")  # your registration form

@app.route("/loginPage")
def loginPage():
    return render_template("login.html")

@app.route("/logout")
def logout():
    # Clear the session
    session.clear()
    # Redirect to login page
    return redirect(url_for("login"))


def is_valid_password(password):
    # At least 5 characters
    if len(password) < 5:
        return False
    # Must contain uppercase, lowercase, digit, and special character
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]

    if not is_valid_password(password):
        flash(
            "❌ Password must be at least 5 characters and \n"
            "include uppercase, lowercase, digit, and special character.",
            "error")
        return render_template("register.html")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert data into your 'login' table
    cursor.execute("INSERT INTO login (email, password) VALUES (%s, %s)", (email, password))
    conn.commit()

    cursor.close()
    conn.close()

    flash("✅ Registration successful!", "success")

    # Redirect back to register.html
    return redirect(url_for("home"))

@app.route("/index", methods=["GET"], endpoint="index")
def index():
    month = request.args.get("month")
    user_email = session.get("user_email")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    base_query = """
        SELECT id, category, date, amount, payment_method, status
        FROM transactions
        WHERE email=%s
    """
    params = [user_email]

    if month:
        base_query += " AND MONTHNAME(date)=%s"
        params.append(month)

    cursor.execute(base_query, tuple(params))
    transactions = cursor.fetchall()

    # Totals
    cursor.execute("SELECT SUM(amount) AS total_income FROM transactions WHERE status='Cash In' AND email=%s" + (" AND MONTHNAME(date)=%s" if month else ""), tuple(params))
    total_income = cursor.fetchone()["total_income"] or 0

    cursor.execute("SELECT SUM(amount) AS total_expense FROM transactions WHERE status='Cash Out' AND email=%s" + (" AND MONTHNAME(date)=%s" if month else ""), tuple(params))
    total_expense = cursor.fetchone()["total_expense"] or 0

    cursor.execute("SELECT SUM(amount) AS total_result FROM transactions WHERE email=%s" + (" AND MONTHNAME(date)=%s" if month else ""), tuple(params))
    total_result = cursor.fetchone()["total_result"] or 0

    # Category breakdown
    cursor.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE status='Cash Out' AND email=%s {filter}
        GROUP BY category
    """.format(filter="AND MONTHNAME(date)=%s" if month else ""), tuple(params))
    category_expenses = cursor.fetchall()

    for c in category_expenses:
        c["percentage"] = round((c["total"] / total_expense * 100), 1) if total_expense > 0 else 0

    cursor.close()
    conn.close()

    return render_template("index.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        total_result=total_result,
        selected_month=month,
        category_expenses=category_expenses
    )

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM login WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session["user_email"] = email   # ✅ store logged‑in user
            return redirect(url_for("index"))
        else:
            flash("❌ Invalid username or password.", "error")
            return render_template("login.html")

    return render_template("login.html")
@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    category = request.form["category"]
    date = request.form["date"]
    amount = request.form["amount"]
    payment_method = request.form["payment_method"]
    status = request.form["status"]
    user_email = session.get("user_email")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (category, date, amount, payment_method, status, email) VALUES (%s, %s, %s, %s, %s, %s)",
        (category, date, amount, payment_method, status, user_email)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Transaction added successfully!", "success")
    return redirect(url_for("index"))

@app.route("/delete_transaction/<int:id>", methods=["POST"])
def delete_transaction(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"success": True}

@app.route("/edit_transaction/<int:id>", methods=["POST"])
def edit_transaction(id):
    category = request.form["category"]
    date = request.form["date"]
    amount = request.form["amount"]
    payment_method = request.form["payment_method"]
    status = request.form["status"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transactions SET category=%s, date=%s, amount=%s, payment_method=%s, status=%s WHERE id=%s",
        (category, date, amount, payment_method, status, id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("✅ Transaction updated successfully!", "success")
    return redirect(url_for("index"))

@app.route("/guest", endpoint="guest_login")
def guest_login():
    session["user_email"] = "guest@cazura.com"  # ✅ store guest identity
    print("Guest session email:", session.get("user_email"))  # optional debug
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
