import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

APP_NAME = os.environ.get("APP_NAME", "Personal Task Board")
DATABASE_PATH = os.environ.get("DATABASE_PATH", str(Path(__file__).resolve().parent.parent / "data" / "tasks.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only")


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def get_db():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )


init_db()


@app.get("/")
def home():
    return render_template("index.html", app_name=APP_NAME)


@app.get("/health")
def health():
    """Used by Docker HEALTHCHECK and by you while learning."""
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        db_ok = True
    except sqlite3.Error:
        db_ok = False
    status = "ok" if db_ok else "degraded"
    code = 200 if db_ok else 503
    return jsonify(
        {
            "status": status,
            "app": APP_NAME,
            "database": "up" if db_ok else "down",
            "time": utc_now(),
        }
    ), code


@app.get("/api/tasks")
def list_tasks():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, title, done, created_at FROM tasks ORDER BY done ASC, id DESC"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/tasks")
def create_task():
    payload = request.get_json(silent=True) or {}
    title = (payload.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done, created_at) VALUES (?, 0, ?)",
            (title, utc_now()),
        )
        task_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, title, done, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    return jsonify(dict(row)), 201


@app.patch("/api/tasks/<int:task_id>")
def toggle_task(task_id):
    with get_db() as conn:
        row = conn.execute("SELECT id, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return jsonify({"error": "not found"}), 404
        new_done = 0 if row["done"] else 1
        conn.execute("UPDATE tasks SET done = ? WHERE id = ?", (new_done, task_id))
        updated = conn.execute(
            "SELECT id, title, done, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    return jsonify(dict(updated))


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "not found"}), 404
    return ("", 204)
