import os
from flask import (Flask, request, redirect, url_for, send_from_directory,
                   flash, render_template)
from werkzeug.utils import secure_filename
import subprocess

UPLOAD_FOLDER = '/Users/davidfstevens/insight/dance-app/data/input'
ALLOWED_EXTENSIONS = set(['mp4'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # convert to avi
            basename = filename.split('.')[0]
            convert_to_avi(basename)

            # run pose detection
            extract_poses(basename)

            # convert back to mp4
            convert_to_mp4(basename)
            return redirect(url_for('uploaded_file', filename=filename))

    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def convert_to_avi(basename):
    # convert input from mp4 to avi
    subprocess.run([
        "ffmpeg",
        "-i", os.path.join(app.config['UPLOAD_FOLDER'], basename) + '.mp4',
        os.path.join(app.config['UPLOAD_FOLDER'], basename) + '.avi'
    ])
    return True

def extract_poses(basename):
    # TODO: switch to the command on ec2
    subprocess.run([
        "/Users/davidfstevens/insight/openpose/build/examples/openpose/openpose.bin",
        "--video", os.path.join(app.config['UPLOAD_FOLDER'], basename) + '.avi',
        "--write_video", os.path.join("/Users/davidfstevens/insight/dance-app/data/output", basename) + '.avi',
        "--disable_blending",
        "--model_folder", "/Users/davidfstevens/insight/openpose/models/",
        "--display", "0",
        # "--hand", "--hand_render", "1",
        # "--face", "--face_render", "1"
    ])
    return True

def convert_to_mp4(basename):
    # convert input from mp4 to avi
    subprocess.run([
        "ffmpeg",
        "-i", os.path.join("/Users/davidfstevens/insight/dance-app/data/output", basename) + '.avi',
        os.path.join("/Users/davidfstevens/insight/dance-app/data/output", basename) + '.mp4'
    ])
    return True

if __name__ == '__main__':
    app.run()
