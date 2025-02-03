from flask import Flask, request, render_template, session
from flask_socketio import SocketIO, emit
from datetime import datetime
import subprocess
import uuid
import threading
import time

app = Flask(__name__)
app.secret_key = 'gizli_acar'  # Sessiyalar üçün gizli açar
socketio = SocketIO(app, cors_allowed_origins="*")

# Ümumi və online ziyarətçi sayğacı
total_visits = 0
online_visitors = set()

# Ziyarətçi məlumatlarının saxlanması
visitor_logs = {}

@app.route('/')
def index():
    global total_visits

    # İstifadəçiyə unikal sessiya ID-si verək
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

    def get_client_ip():
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        return request.remote_addr

    user_ip = get_client_ip()
    user_agent = request.headers.get('User-Agent')
    visit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Ümumi ziyarətçi sayını artırırıq
    total_visits += 1

    # Eyni IP-ləri qruplaşdırırıq
    if user_ip not in visitor_logs:
        visitor_logs[user_ip] = []
    
    visitor_logs[user_ip].append({
        'user_agent': user_agent,
        'visit_time': visit_time
    })

    return render_template(
        'index.html',
        visitor_logs=visitor_logs,
        total_visits=total_visits,
        online_count=len(online_visitors)
    )

@socketio.on('connect')
def handle_connect():
    online_visitors.add(session['user_id'])
    emit('update_online_count', len(online_visitors), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    online_visitors.discard(session['user_id'])
    emit('update_online_count', len(online_visitors), broadcast=True)

def send_neofetch_data():
    while True:
        try:
            # Neofetch məlumatlarını al
            result = subprocess.run(['neofetch', '--stdout'], stdout=subprocess.PIPE, timeout=1)
            neofetch_output = result.stdout.decode('utf-8')

            # Məlumatı real vaxtda göndər
            socketio.emit('update_neofetch', neofetch_output)  # broadcast=True çıxarıldı
        except Exception as e:
            print("Neofetch xətası:", e)

        time.sleep(0.2)  # 200ms gözlət

# Neofetch yeniləməsini fon prosesində başladırıq
threading.Thread(target=send_neofetch_data, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)