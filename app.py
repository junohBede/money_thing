from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "cashbook.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 편리하게 가져오기 위함
    return conn

# 앱이 처음 실행될 때 데이터베이스 테이블이 없으면 자동으로 만듭니다.
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            category TEXT NOT NULL,
            memo TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 1. 메인 가계부 페이지 렌더링
@app.route('/')
def index():
    return render_template('index.html')

# 2. 전체 가계부 데이터 조회 API (페이지 로드 시 호출)
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM transactions').fetchall()
    conn.close()
    
    # Frontend something
    data = [dict(row) for row in rows]
    return jsonify(data)

# 3. 내역 추가 API
@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    tx_data = request.json
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO transactions (id, date, type, amount, category, memo) VALUES (?, ?, ?, ?, ?, ?)',
        (tx_data['id'], tx_data['date'], tx_data['type'], tx_data['amount'], tx_data['category'], tx_data['memo'])
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# 4. 내역 수정 API
@app.route('/api/transactions/<tx_id>', methods=['PUT'])
def update_transaction(tx_id):
    tx_data = request.json
    conn = get_db_connection()
    conn.execute(
        'UPDATE transactions SET type=?, category=?, memo=?, amount=? WHERE id=?',
        (tx_data['type'], tx_data['category'], tx_data['memo'], tx_data['amount'], tx_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# 5. 내역 삭제 API
@app.route('/api/transactions/<tx_id>', methods=['DELETE'])
def delete_transaction(tx_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM transactions WHERE id=?', (tx_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    # 테일스케일 접속을 위해 외부 오픈(0.0.0.0), 포트는 5000번 사용
    app.run(host='0.0.0.0', port=5000, debug=True)