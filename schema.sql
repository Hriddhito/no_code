CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    original_language TEXT NOT NULL,
    original_message TEXT NOT NULL,
    translation_en TEXT,
    translation_hi TEXT,
    translation_ta TEXT
);
