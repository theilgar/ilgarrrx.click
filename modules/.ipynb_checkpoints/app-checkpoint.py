from flask import Flask, request, render_template, session, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import subprocess
import uuid
import threading
import time
import sqlite3
import socket

app = Flask(__name__)
app.secret_key = 'gizli_acar'
socketio = SocketIO(app, cors_allowed_origins="*")

# Verilənlər bazasını yarat
def init_db():
    with sqlite3.connect("visitors.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_ip TEXT,
            ipv4 TEXT,
            ipv6 TEXT,
            user_agent TEXT,
            visit_time TEXT,
            screen_width INTEGER,
            screen_height INTEGER,
            platform TEXT,
            language TEXT
        )
        """)
        conn.commit()

# Verilənlər bazasını başlat
init_db()

# Sayğaclar
total_visits = 0
online_visitors = set()

def get_client_ip():
    """ Müştərinin həm IPv4, həm də IPv6 ünvanını qaytarır. """
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if ip:
        ip_list = ip.split(',')
        user_ip = ip_list[0].strip()  # Ən birinci IP-ni götür

        try:
            ipv4 = socket.gethostbyname(user_ip)  # IPv4 ünvanını al
        except socket.gaierror:
            ipv4 = None

        try:
            ipv6 = socket.getaddrinfo(user_ip, None, socket.AF_INET6)[0][4][0]  # IPv6 ünvanını al
        except (socket.gaierror, IndexError):
            ipv6 = None

        return user_ip, ipv4, ipv6
    return None, None, None  # IP tapılmazsa, None qaytar

@app.route('/')
def index():
    global total_visits

    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

    user_ip, ipv4, ipv6 = get_client_ip()
    user_agent = request.headers.get('User-Agent')
    visit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Məlumatı verilənlər bazasına yaz
    with sqlite3.connect("visitors.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO visitors (user_ip, ipv4, ipv6, user_agent, visit_time) VALUES (?, ?, ?, ?, ?)", 
                       (user_ip, ipv4, ipv6, user_agent, visit_time))
        conn.commit()

    total_visits += 1

    # Ziyarətçi məlumatlarını bazadan götür
    with sqlite3.connect("visitors.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_ip, ipv4, ipv6, user_agent, visit_time FROM visitors ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()

    # List-i dictionary formatına çeviririk
    visitor_logs = {}
    for row in rows:
        user_ip, ipv4, ipv6, user_agent, visit_time = row
        if user_ip not in visitor_logs:
            visitor_logs[user_ip] = []
        visitor_logs[user_ip].append({
            'ipv4': ipv4 if ipv4 else "Yoxdur",
            'ipv6': ipv6 if ipv6 else "Yoxdur",
            'user_agent': user_agent,
            'visit_time': visit_time
        })

    return render_template(
        'index.html',
        visitor_logs=visitor_logs,
        total_visits=total_visits,
        online_count=len(online_visitors),
        user_ip_v4=ipv4 if ipv4 else "Bilinmir",
        user_ip_v6=ipv6 if ipv6 else "Bilinmir",
        enumerate=enumerate
    )

@app.route('/collect-info', methods=['POST'])
def collect_info():
    """ Frontend-dən gələn ekran ölçüsü, platforma və dili saxlayır """
    data = request.json
    user_ip, _, _ = get_client_ip()

    with sqlite3.connect("visitors.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE visitors 
            SET screen_width=?, screen_height=?, platform=?, language=? 
            WHERE user_ip=? 
            ORDER BY id DESC LIMIT 1
        """, (data.get('screen_width'), data.get('screen_height'), data.get('platform'), data.get('language'), user_ip))
        conn.commit()

    return jsonify({"status": "success"})

def send_neofetch_data():
    while True:
        try:
            result = subprocess.run(['neofetch', '--stdout'], stdout=subprocess.PIPE, timeout=1)
            neofetch_output = result.stdout.decode('utf-8')
            socketio.emit('update_neofetch', neofetch_output)
        except Exception as e:
            print("Neofetch xətası:", e)

        time.sleep(0.2)

def run():
    threading.Thread(target=send_neofetch_data, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=False)

if __name__ == "__main__":
    run()