from flask import Flask, request, Response
from flask_cors import CORS
import sqlite3
import json
from googletrans import Translator

app = Flask(__name__)
CORS(app)
translator = Translator()

DB = 'database.db'

# ---------------------------
# Helper: Connect to DB
# ---------------------------
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------
# Route: Post a message
# ---------------------------
@app.route('/post_message', methods=['POST'])
def post_message():
    data = request.get_json()
    username = data.get('username')
    original_message = data.get('message')
    original_language = data.get('language')  # 'hi', 'en', 'ta'

    if not username or not original_message or not original_language:
        return Response(
            '{"error":"Missing fields"}',
            status=400,
            mimetype='application/json; charset=utf-8'
        )

    try:
        # Translate message to multiple languages
        translation_en = translator.translate(original_message, src='auto', dest='en').text
        translation_hi = translator.translate(original_message, src='auto', dest='hi').text
        translation_ta = translator.translate(original_message, src='auto', dest='ta').text
    except Exception as e:
        # If translation fails, fallback to original text
        translation_en = original_message
        translation_hi = original_message
        translation_ta = original_message

    # Save to DB
    conn = get_db_connection()
    conn.execute(
        '''INSERT INTO messages 
           (username, original_language, original_message, translation_en, translation_hi, translation_ta)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (username, original_language, original_message, translation_en, translation_hi, translation_ta)
    )
    conn.commit()
    conn.close()

    return Response(
        '{"status":"success"}',
        mimetype='application/json; charset=utf-8'
    )

# ---------------------------
# Route: Get messages in a specific language
# ---------------------------
@app.route('/get_messages/<lang>', methods=['GET'])
def get_messages(lang):
    if lang not in ['en', 'hi', 'ta']:
        return Response(
            '{"error":"Unsupported language"}',
            status=400,
            mimetype='application/json; charset=utf-8'
        )

    conn = get_db_connection()
    rows = conn.execute(f'SELECT username, translation_{lang} AS message FROM messages').fetchall()
    conn.close()

    messages = [{"username": row["username"], "message": row["message"]} for row in rows]

    # Return JSON with UTF-8, no unicode escapes
    return Response(
        json.dumps(messages, ensure_ascii=False),
        mimetype='application/json; charset=utf-8'
    )

# ---------------------------
# Initialize DB & Run App
# ---------------------------
if __name__ == '__main__':
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            original_language TEXT NOT NULL,
            original_message TEXT NOT NULL,
            translation_en TEXT,
            translation_hi TEXT,
            translation_ta TEXT
        )
    ''')
    conn.close()
    app.run(debug=True)
