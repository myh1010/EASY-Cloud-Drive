from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, Response
import os
import mimetypes
from werkzeug.utils import secure_filename

app = Flask(__name__)
osp = os.getcwd()
app.config['UPLOAD_FOLDER'] = osp+"/"+"uploads"
app.secret_key = '236875'

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files')
        if uploaded_files:
            for file in uploaded_files:
                if file:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
            flash('Files uploaded successfully!', 'success')
            return redirect(url_for('index'))
    return render_template('upload.html')


@app.route('/delete_files', methods=['POST'])
def delete_files():
    filenames = request.form.getlist('files[]')
    for filename in filenames:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(file_path):
            os.remove(file_path)
    flash('Selected files deleted successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/view/<filename>')
def view_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if not os.path.exists(file_path):
        return "File not found", 404

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    if mime_type.startswith('text/') or mime_type == 'application/json':
        with open(file_path, 'r') as f:
            content = f.read()
        return Response(content, mimetype=mime_type)

    elif mime_type.startswith('audio/') or mime_type.startswith('video/') or mime_type.startswith('image/'):
        return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename), as_attachment=False)

    return "Unsupported file type", 415


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))


if __name__ == '__main__':
    app.run(debug=False, port=8070,host='0.0.0.0')
