from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = ""
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

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
    app.run(host='0.0.0.0', port=5000,debug=True)
