import os
import socket

import pymysql
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configure MySQL from environment variables
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'port': int(os.environ.get('MYSQL_PORT', '3306')),
    'user': os.environ.get('MYSQL_USER', 'default_user'),
    'password': os.environ.get('MYSQL_PASSWORD', 'default_password'),
    'database': os.environ.get('MYSQL_DB', 'default_db'),
}


def get_conn():
    return pymysql.connect(**DB_CONFIG)


_db_ready = False


def init_db():
    global _db_ready
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message TEXT
            );
            ''')
        conn.commit()
    finally:
        conn.close()
    _db_ready = True


def ensure_db():
    # Create the table on first use (idempotent) so the app also works under
    # gunicorn and against a brand-new RDS instance, even if the DB came up
    # after the app did.
    if not _db_ready:
        init_db()


@app.route('/health')
def health():
    # Deliberately does not touch the database: a DB blip should not make a
    # load balancer mark every web instance unhealthy at the same time.
    return jsonify({'status': 'ok'})


@app.route('/')
def hello():
    ensure_db()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT message FROM messages')
            messages = cur.fetchall()
    finally:
        conn.close()
    return render_template('index.html', messages=messages, hostname=socket.gethostname())


@app.route('/submit', methods=['POST'])
def submit():
    new_message = request.form.get('new_message')
    ensure_db()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
        conn.commit()
    finally:
        conn.close()
    return jsonify({'message': new_message})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_DEBUG') == '1')
