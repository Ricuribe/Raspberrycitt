from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
import subprocess
import time
import threading
import sys
import keyboard

app = Flask(__name__)
app.secret_key = ""
UPLOAD_FOLDER = 'static/uploads/'
# contraseña para subir; cambiar aquí o mediante la variable de entorno UPLOAD_PASSWORD
UPLOAD_PASSWORD = os.environ.get('UPLOAD_PASSWORD', '')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/css/style.css')
def css_style():
    return send_from_directory(os.path.join(app.root_path, 'static', 'css'), 'style.css', mimetype='text/css')

monitor_proc = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def start_monitor_script():
    global monitor_proc
    monitor_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'monitor.py')
    monitor_proc = subprocess.Popen([sys.executable, monitor_script_path])
    return monitor_proc

def shutdown_all():
    print("Hotkey detectado: cerrando monitor y aplicación...")
    global monitor_proc
    try:
        if monitor_proc:
            monitor_proc.terminate()
    except Exception:
        pass
    # dar tiempo para que monitor.py capture la señal y termine feh
    time.sleep(1)
    os._exit(0)

def start_hotkey_listener():
    # Ctrl+Shift+Q para terminar todo
    keyboard.add_hotkey('ctrl+shift+q', shutdown_all)
    # Mantener el hilo vivo
    keyboard.wait()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # verificar contraseña primero
        pw = request.form.get('password', '')
        if pw != UPLOAD_PASSWORD:
            flash('Contraseña incorrecta')
            return redirect(request.url)

        if 'file' not in request.files:
            flash('No hay ningún archivo seleccionado')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No hay ningún archivo seleccionado')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f'El Archivo {filename} subido exitosamente')
            return redirect(url_for('upload_file', filename=filename))
        else:
            flash('Tipo de archivo no permitido (solo se permiten png, jpg, jpeg, gif)')
            return redirect(request.url)
    return render_template('upload.html')

if __name__ == '__main__':
    start_monitor_script()
    # iniciar listener en hilo separado para no bloquear el servidor
    t = threading.Thread(target=start_hotkey_listener, daemon=True)
    t.start()
    time.sleep(2)  # Esperar un momento para asegurar que el monitor se inicie
    # desactivar el reloader para evitar que se registren hotkeys múltiples
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
