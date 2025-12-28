import os
from werkzeug.utils import secure_filename

def save_uploaded_file(file, upload_dir):
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    #print(upload_dir+" file directory 😅")
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_dir, filename)

    file.save(file_path)
    return file_path
   
