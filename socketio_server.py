from flask_socketio import SocketIO, emit
from flask import session
from neofetch import start_neofetch_thread

socketio = SocketIO(cors_allowed_origins="*")

online_visitors = set()

@socketio.on('connect')
def handle_connect():
    online_visitors.add(session.get('user_id', ''))
    emit('update_online_count', len(online_visitors), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    online_visitors.discard(session.get('user_id', ''))
    emit('update_online_count', len(online_visitors), broadcast=True)

def start_socketio(app):
    """ Socket.IO serverini işə salır """
    socketio.init_app(app)
    start_neofetch_thread(socketio)  # Neofetch prosesini başladır
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)