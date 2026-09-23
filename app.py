from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)
DB_NAME = "cashbook.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # retrieve the results as dictionary form
    return conn

# Initialize DB
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            memo TEXT,
            pay_cycle INTEGER
            payment_method TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 1. Render main page 
@app.route('/')
def index():
    return render_template('index.html')

# 2. Look up the entire data
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM transactions').fetchall()
    conn.close()
    
    # Frontend part
    data = [dict(row) for row in rows]
    return jsonify(data)

# 3. Add value
@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    tx_data = request.json
    cycle_num = calculate_pay_cycle(tx_data['date'])
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO transactions (id, date, type, amount, category, memo, payment_method, pay_cycle) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (tx_data['id'], tx_data['date'], tx_data['type'], tx_data['amount'], tx_data['category'], tx_data['memo'], tx_data['payment_method'], cycle_num)
    ) 
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}) 

# 4. Edit value
@app.route('/api/transactions/<tx_id>', methods=['PUT'])
def update_transaction(tx_id):
    tx_data = request.json
    conn = get_db_connection()
    conn.execute(
        'UPDATE transactions SET type=?, category=?, memo=?, amount=? WHERE id=?',
        (tx_data['type'], tx_data['category'], tx_data['memo'], tx_data['amount'], tx_data['payment_method'], cycle_num, tx_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# 5. Delete value
@app.route('/api/transactions/<tx_id>', methods=['DELETE'])
def delete_transaction(tx_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM transactions WHERE id=?', (tx_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# 6. Biweekly data sorting helper function
def calculate_pay_cycle(tx_date_str):
    anchor_date = datetime(2026, 1, 31).date()
    tx_date = datetime.strptime(tx_date_str, '%Y-%m-%d').date()
    days_diff = (tx_date - anchor_date).days
    cycle_number = days_diff // 14
    return cycle_number


# 1-2. Stat page
@app.route('/stats')
def stats():
    return render_template('stats.html')


# 1-3. Paycheck period stat page
@app.route('/paycheck_period')
def paycheck_period():
    return render_template('paycheck_period.html')

if __name__ == '__main__':
    init_db()
    # 0.0.0.0 for Tailscale
    app.run(host='0.0.0.0', port=5000, debug=True)