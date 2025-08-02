import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    ref_id INTEGER,
    balance INTEGER DEFAULT 0
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (
    invoice_id TEXT PRIMARY KEY,
    user_id INTEGER,
    amount REAL,
    status TEXT DEFAULT 'pending'
)''')

conn.commit()
conn.close()

def add_user(user_id, username, ref_id=None):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, username, ref_id) VALUES (?, ?, ?)",
                (user_id, username, ref_id))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()
    conn.close()
    return result

def get_balance(user_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cur.fetchone()[0]
    conn.close()
    return result

def update_balance(user_id, coins):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (coins, user_id))
    conn.commit()
    conn.close()

def get_ref_count(user_id):
    conn = sqlite3.connect("bot.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE ref_id = ?", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count