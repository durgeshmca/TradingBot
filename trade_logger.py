import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('db/trades.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT,
        symbol TEXT,
        signal TEXT
    )''')
    conn.commit()
    conn.close()

def log_trade_to_db(signal, symbol='RELIANCE'):
    conn = sqlite3.connect('db/trades.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trades (datetime, symbol, signal) VALUES (?, ?, ?)",
                   (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol, signal))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()