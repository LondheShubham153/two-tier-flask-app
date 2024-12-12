import os
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL from environment variables with defaults
# These configurations allow the app to connect to the MySQL database using
# environment variables with default fallback values for local development.
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'default_user')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'default_password')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'default_db')

# Initialize MySQL
mysql = MySQL(app)

def init_db():
    """Initializes the database by creating the necessary table if it doesn't exist.
    This function ensures that the database is prepared for use by the application. It
    creates a 'messages' table if it does not already exist."""
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message TEXT NOT NULL
                );
            ''')
            mysql.connection.commit()
            cur.close()
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def index():
    """Fetches messages from the database and renders the index.html template."""
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT message FROM messages')
        messages = cur.fetchall()
        cur.close()
        # Ensure messages is a list of strings for rendering
        messages = [msg[0] for msg in messages]
        return render_template('index.html', messages=messages)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch messages: {e}"}), 500

@app.route('/submit', methods=['POST'])
def submit():
    """Handles message submission and stores it in the database."""
    new_message = request.form.get('new_message')
    if not new_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO messages (message) VALUES (%s)', [new_message])
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': new_message}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to insert message: {e}"}), 500

if __name__ == '__main__':
    # Initialize the database before starting the server
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
