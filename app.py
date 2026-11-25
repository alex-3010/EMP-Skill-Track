from pathlib import Path
import sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "skilltrack-local-app"
DB_PATH = Path(__file__).with_name("skilltrack.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                department TEXT NOT NULL
            )
        """)


def get_employees():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT employee_id, name, department FROM employees ORDER BY name"
        ).fetchall()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    with sqlite3.connect(DB_PATH) as conn:
        employee_count = conn.execute(
            "SELECT COUNT(*) FROM employees"
        ).fetchone()[0]
    return render_template("dashboard.html", employee_count=employee_count)


@app.route("/employees", methods=["GET", "POST"])
def employees():
    error = None
    form_values = {"employee_id": "", "name": "", "department": ""}

    if request.method == "POST":
        form_values = {
            "employee_id": request.form.get("employee_id", "").strip(),
            "name": request.form.get("name", "").strip(),
            "department": request.form.get("department", "").strip(),
        }

        if not all(form_values.values()):
            error = "Ella details-um fill pannunga."
        else:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute(
                        "INSERT INTO employees (employee_id, name, department) VALUES (?, ?, ?)",
                        (
                            form_values["employee_id"],
                            form_values["name"],
                            form_values["department"],
                        ),
                    )
                flash("Employee save aayiduchu.")
                return redirect(url_for("employees"))
            except sqlite3.IntegrityError:
                error = "Indha Employee ID already use aagudhu."

    return render_template(
        "employees.html",
        employees=get_employees(),
        error=error,
        form_values=form_values,
    )


init_db()

if __name__ == "__main__":
    app.run(debug=True)