import sqlite3
from datetime import datetime

DB_PATH = "visitors.db"

# Verilənlər bazasını və cədvəlləri yaradın (əgər mövcud deyilsə)
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT,
                user_agent TEXT,
                visit_time TEXT,
                screen_width INTEGER,
                screen_height INTEGER,
                platform TEXT,
                language TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                key TEXT PRIMARY KEY,
                value INTEGER
            )
        ''')
        # Əgər ümumi ziyarət sayı mövcud deyilsə, sıfırdan başlamaq əvəzinə saxla
        cursor.execute("INSERT OR IGNORE INTO stats (key, value) VALUES ('total_visits', 0)")
        conn.commit()

# Ümumi ziyarətçi sayını əldə et
def get_total_visits():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM stats WHERE key = 'total_visits'")
        result = cursor.fetchone()
        return result[0] if result else 0

# Ümumi ziyarətçi sayını artır
def increment_total_visits():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE stats SET value = value + 1 WHERE key = 'total_visits'")
        conn.commit()

# Yeni ziyarətçini bazaya əlavə et
def log_visitor(ip, user_agent, visit_time, screen_width=None, screen_height=None, platform=None, language=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO visitors (ip, user_agent, visit_time, screen_width, screen_height, platform, language)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ip, user_agent, visit_time, screen_width, screen_height, platform, language))
        conn.commit()

# Bütün ziyarətçi loglarını əldə et
def get_visitor_logs():
    visitor_logs = {}
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ip, user_agent, visit_time, screen_width, screen_height, platform, language FROM visitors ORDER BY visit_time DESC")
        logs = cursor.fetchall()

        for log in logs:
            ip, user_agent, visit_time, screen_width, screen_height, platform, language = log
            if ip not in visitor_logs:
                visitor_logs[ip] = []
            visitor_logs[ip].append({
                'user_agent': user_agent,
                'visit_time': visit_time,
                'screen_width': screen_width,
                'screen_height': screen_height,
                'platform': platform,
                'language': language
            })

    return visitor_logs