import subprocess
import time
import threading
from flask_socketio import SocketIO

def send_neofetch_data(socketio: SocketIO):
    """ Neofetch məlumatlarını periodik olaraq göndərir. """
    while True:
        try:
            result = subprocess.run(['neofetch', '--stdout'], stdout=subprocess.PIPE, timeout=1)
            neofetch_output = result.stdout.decode('utf-8')
            socketio.emit('update_neofetch', neofetch_output)
        except Exception as e:
            print("Neofetch xətası:", e)

        time.sleep(0.2)

def start_neofetch_thread(socketio: SocketIO):
    """ Neofetch prosesini ayrı bir thread-də başladır. """
    threading.Thread(target=send_neofetch_data, args=(socketio,), daemon=True).start()