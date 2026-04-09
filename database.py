import pandas as pd
import sqlite3

def get_connection():
    return sqlite3.connect("expense.db", check_same_thread=False)

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_expense(amount, category, date, note):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
        (amount, category, date, note)
    )
    conn.commit()
    conn.close()

def fetch_expenses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT date, category, amount, note FROM expenses ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def total_expense():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM expenses")
    total = cur.fetchone()[0]
    conn.close()
    return total or 0

def fetch_expenses_df():
    conn = get_connection()
    df = pd.read_sql(
       
