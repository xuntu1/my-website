import os
from flask import Flask, render_template, request, send_from_directory, redirect
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'activity.log'

# Ensure the upload folder exists and create it if not
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return "No file part"
        files = request.files.getlist('file')
        for file in files:
            if file and file.filename:  # Check if file is not empty
                save_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(save_path)
                log_activity(f"Uploaded file: {file.filename}")
        return redirect('/')
    except Exception as e:
        log_activity(f"Failed to upload file - Error: {str(e)}")
        return f"Failed to upload file: {str(e)}", 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        log_activity(f"Failed to access file: {filename} - Error: {str(e)}")
        return f"Failed to access file: {str(e)}", 500

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        log_activity(f"Deleted file: {filename}")
        return redirect('/')
    except Exception as e:
        log_activity(f"Failed to delete file: {filename} - Error: {str(e)}")
        return 'Failed to delete file', 500

@app.route('/rename/<old_filename>', methods=['POST'])
def rename_file(old_filename):
    try:
        new_filename = request.form['new_filename'].strip()
        
        # Extract the original file extension
        file_extension = os.path.splitext(old_filename)[1]
        
        # Remove any extension that the user might have mistakenly added
        new_filename_no_ext = os.path.splitext(new_filename)[0]

        # Combine the new name with the original extension
        final_filename = f"{new_filename_no_ext}{file_extension}"

        # Check if the new filename already exists to prevent overwriting
        old_file_path = os.path.join(UPLOAD_FOLDER, old_filename)
        new_file_path = os.path.join(UPLOAD_FOLDER, final_filename)
        if os.path.exists(new_file_path):
            log_activity(f"Rename failed: {final_filename} already exists")
            return f"Rename failed: {final_filename} already exists", 400
        
        # Rename the file
        os.rename(old_file_path, new_file_path)
        log_activity(f"Renamed file: {old_filename} to {final_filename}")
        return 'Success', 200
    except Exception as e:
        log_activity(f"Failed to rename file: {old_filename} - Error: {str(e)}")
        return f'Failed to rename file: {str(e)}', 500

@app.route('/log')
def log_view():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            logs = log_file.readlines()
            logs.reverse()  # Show the newest entries at the top
    else:
        logs = []
    return render_template('log.html', logs=logs)

@app.route('/refresh_log', methods=['GET'])
def refresh_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as log_file:
            logs = log_file.readlines()
            logs.reverse()  # Show the newest entries at the top
    else:
        logs = []
    return {'logs': logs}

@app.route('/log_change', methods=['POST'])
def log_change():
    action = request.form['action']
    try:
        log_activity(f"Password/Link change - {action}")
        return 'Success', 200
    except Exception as e:
        log_activity(f"Failed to log change - Error: {str(e)}")
        return 'Failed to log change', 500

@app.route('/files')
def files():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('files.html', files=files)

@app.route('/password')
def password():
    return render_template('password.html')


def log_activity(action):
    ip = request.remote_addr
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp},{ip},{action}\n"
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(log_entry)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
