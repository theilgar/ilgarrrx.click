import os
import hashlib
import subprocess
import time
from flask import Flask, Blueprint, request, render_template, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Güclü və unikal gizli açar seçin

# Blueprint yaradılır
admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

# Konfiqurasiya
CREDENTIALS_FILE = 'admin_credentials.txt'
BEDROCK_SESSION = "bedrock"
BEDROCK_WORKING_DIR = "/home/ubuntu/bedrock"  # Bedrock serverin yerləşdiyi direktoriyanın tam yolu
BEDROCK_START_COMMAND = "ld_LIBRARY_PATH=. ./bedrock_server"  # Serverin işə salınma əmri

# --- Kredensialların idarə olunması ---
def save_credentials(username, password):
    """İstifadəçi adını və şifrəni SHA256 hash-ləyərək faylda saxlayır."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with open(CREDENTIALS_FILE, 'w') as f:
        f.write(f"{username}\n{hashed_password}\n")

def load_credentials():
    """Fayldan saxlanmış kredensialları oxuyur."""
    if not os.path.exists(CREDENTIALS_FILE):
        return None, None
    with open(CREDENTIALS_FILE, 'r') as f:
        lines = f.read().splitlines()
    if len(lines) >= 2:
        return lines[0], lines[1]
    return None, None

# --- Admin giriş və çıxış ---
@admin_bp.route('/', methods=['GET', 'POST'])
def admin_login():
    """
    Əgər admin artıq daxil olubsa, admin panelini göstərir; 
    əks halda, giriş formu və ya ilkin kredensialların təyini üçün səhifəni göstərir.
    """
    if session.get('admin_logged_in'):
        return render_template('admin.html')

    credentials_exist = os.path.exists(CREDENTIALS_FILE)

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not credentials_exist:
            # İlk dəfə giriş zamanı kredensialları təyin edirik
            save_credentials(username, password)
            session['admin_logged_in'] = True
            flash("Admin kredensialları təyin olundu və giriş uğurlu oldu!", "success")
            return redirect(url_for('admin.admin_login'))
        else:
            stored_username, stored_hashed = load_credentials()
            if username == stored_username and hashlib.sha256(password.encode()).hexdigest() == stored_hashed:
                session['admin_logged_in'] = True
                flash("Giriş uğurlu oldu!", "success")
                return redirect(url_for('admin.admin_login'))
            else:
                flash("Səhv kredensiallar!", "danger")
    return render_template('admin_login.html', credentials_exist=credentials_exist)

@admin_bp.route('/logout')
def logout():
    """Admin istifadəçisini sistemdən çıxarır."""
    session.pop('admin_logged_in', None)
    flash("Çıxış edildi.", "info")
    return redirect(url_for('admin.admin_login'))

# --- Bedrock Server idarəetməsi ---
def is_bedrock_running():
    """
    'screen -ls' nəticəsində BEDROCK_SESSION adının olub olmadığını yoxlayaraq serverin işləyib-işləmədiyini müəyyən edir.
    """
    try:
        result = subprocess.run(
            ["screen", "-ls"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return BEDROCK_SESSION in result.stdout
    except subprocess.CalledProcessError:
        return False

def start_bedrock():
    """
    Bedrock serveri detach olunmuş screen session içində işə salır.
    """
    if is_bedrock_running():
        return "Bedrock server artıq çalışır."
    try:
        subprocess.run(
            ["screen", "-dmS", BEDROCK_SESSION, "bash", "-c", BEDROCK_START_COMMAND],
            cwd=BEDROCK_WORKING_DIR,
            check=True
        )
        return "Bedrock server işə salındı."
    except subprocess.CalledProcessError as e:
        return f"Bedrock serverin işə salınmasında xəta: {e}"

def stop_bedrock():
    """
    Bedrock serveri dayandırmaq üçün screen sessiona 'stop' əmri göndərir.
    """
    if not is_bedrock_running():
        return "Bedrock server çalışmır."
    try:
        subprocess.run(
            ["screen", "-S", BEDROCK_SESSION, "-X", "stuff", "stop\n"],
            check=True
        )
        return "Stop əmri göndərildi."
    except subprocess.CalledProcessError as e:
        return f"Bedrock serverin dayandırılmasında xəta: {e}"

def restart_bedrock():
    """
    Bedrock serveri dayandırıb yenidən işə salır.
    """
    stop_msg = stop_bedrock()
    time.sleep(2)  # Dayandırma əmri üçün qısa fasilə
    start_msg = start_bedrock()
    return f"{stop_msg} {start_msg}"

def send_bedrock_command(command):
    """
    Bedrock serverin screen sessionuna istənilən əmri göndərir.
    """
    if not is_bedrock_running():
        return "Bedrock server çalışmır."
    try:
        full_command = command + "\n"
        subprocess.run(
            ["screen", "-S", BEDROCK_SESSION, "-X", "stuff", full_command],
            check=True
        )
        return f"'{command}' əmri göndərildi."
    except subprocess.CalledProcessError as e:
        return f"Əmr göndərərkən xəta: {e}"

@admin_bp.route('/bedrock', methods=['GET', 'POST'])
def bedrock_management():
    """
    Bedrock serverin idarə olunması üçün interfeys:
    - Serverin start, stop, restart və əmrlərin göndərilməsi.
    - Terminal çıxışını istifadəçiyə göstərir.
    """
    if not session.get('admin_logged_in'):
        flash("Əvvəlcə admin girişi edin.", "danger")
        return redirect(url_for('admin.admin_login'))

    status = is_bedrock_running()
    message = ""

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'start':
            message = start_bedrock()
        elif action == 'stop':
            message = stop_bedrock()
        elif action == 'restart':
            message = restart_bedrock()
        elif action == 'send_command':
            cmd = request.form.get('command')
            message = send_bedrock_command(cmd) if cmd else "Əmr daxil edilməyib."
        status = is_bedrock_running()

    cli_output = ""
    if status:
        hardcopy_file = "/tmp/bedrock_output.txt"
        try:
            # Cari terminal çıxışını hardcopy əmri ilə fayla yazırıq
            subprocess.run(
                ["screen", "-S", BEDROCK_SESSION, "-X", "hardcopy", hardcopy_file],
                check=True
            )
            with open(hardcopy_file, "r", encoding="utf-8", errors="replace") as f:
                cli_output = f.read()
        except Exception as e:
            cli_output = f"Terminal çıxışı oxunarkən xəta: {e}"

    return render_template('bedrock_admin.html', status=status, message=message, cli_output=cli_output)

# --- Terminal çıxışını 0.5 saniyə aralıqlarla yeniləyən endpoint ---
@admin_bp.route('/terminal_output')
def terminal_output_api():
    """
    Terminal çıxışını oxuyub JSON formatında qaytarır.
    Bu endpoint frontend tərəfindən hər 0.5 saniyədən bir sorğu ilə çağırılır.
    """
    if not is_bedrock_running():
        return jsonify({'output': "Server işləmir."})
    hardcopy_file = "/tmp/bedrock_output.txt"
    try:
        subprocess.run(
            ["screen", "-S", BEDROCK_SESSION, "-X", "hardcopy", hardcopy_file],
            check=True
        )
        with open(hardcopy_file, "r", encoding="utf-8", errors="replace") as f:
            cli_output = f.read()
        return jsonify({'output': cli_output})
    except Exception as e:
        return jsonify({'output': f"Terminal çıxışı oxunarkən xəta: {e}"})

# Blueprint-i tətbiqə qeyd edirik
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)