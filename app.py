#!/home/ubuntu/myenv/bin/python
from flask import Flask, request, render_template, session
from datetime import datetime
import uuid
from database import init_db, get_total_visits, increment_total_visits, log_visitor, get_visitor_logs
from socketio_server import start_socketio

# Admin modulunu import edirik
from admin import admin_bp

app = Flask(__name__)
app.secret_key = 'gizli_acar'

# Bazanı hazırlayırıq
init_db()
total_visits = get_total_visits()

@app.route('/')
def index():
    global total_visits

    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())

    def get_client_ip():
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        return request.remote_addr

    user_ip = get_client_ip()
    user_agent = request.headers.get('User-Agent')
    visit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Ümumi ziyarətçi sayını artır və bazaya yaz
    total_visits += 1
    increment_total_visits()
    log_visitor(user_ip, user_agent, visit_time)

    # Ziyarətçi məlumatlarını bazadan al
    visitor_logs = get_visitor_logs()

    return render_template(
        'index.html',
        visitor_logs=visitor_logs,
        total_visits=total_visits,
        user_ip=user_ip,  # IP adresi HTML-ə ötürürük
        enumerate=enumerate
    )

# Admin blueprint‑ini /admin URL‑i ilə qeyd edirik
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == "__main__":
    start_socketio(app)