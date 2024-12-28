from flask import Flask, render_template, request, redirect, url_for, send_file
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = './static/files'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_filename_list(folder_path):
    try:
        all_items = os.listdir(folder_path)

        filenames = [os.path.splitext(item)[0] for item in all_items if os.path.isfile(os.path.join(folder_path, item))]

        return filenames
    except FileNotFoundError:
        print(f"Error: The folder '{folder_path}' does not exist.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access the folder '{folder_path}'.")
        return []

def json_content(file_path):

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)

    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content

def json_write(file_path, value, key):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)

    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            content = json.load(file)
        except json.JSONDecodeError:
            content = {}

    content[key] = value

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)

@app.route("/")
def home():
    file_path = 'files/resume.json'

    content = json_content(file_path)

    language = content.get('language', 'en_US')
    style = content.get('style', 'basic')

    i18n = json_content(f"i18n/{language}.json")
    
    return render_template(f"{style}.html",
        data=content,
        i18n=i18n
    )

@app.route("/edit", methods=["GET","POST"])
def edit_page():
    file_path = 'files/resume.json'

    content = json_content(file_path)

    language = content.get('language', 'en_US')

    style = content.get('style', 'basic')

    i18n = json_content(f"i18n/{language}.json")
    
    languages = get_filename_list("i18n")

    styles = get_filename_list("static/css")

    if request.method == 'POST':
        form_id = request.form.get('form_id')
        if form_id == 'language_form':
            lang = request.form.get('language', language)
            json_write(file_path,lang,"language")
        elif form_id == 'style_form':
            css = request.form.get('style', style)
            json_write(file_path,css,"style")
        elif form_id == "edit_form":
            action = request.form.get('action')
            if action == "save":
                info = {}
                for key, value in request.form.items():
                    if key.startswith("info["):
                        sub_key = key[5:-1]
                        info[sub_key] = value
                photo = request.files['photo']
                if photo and photo.filename != '':
                    if allowed_file(photo.filename):
                        filename = secure_filename(photo.filename)
                        saved_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        photo.save(saved_file_path)
                info['photo'] = "files/" + filename
                json_write(file_path,info,"info")
                # TODO MORE
            elif action == "cancel":
                pass
            elif action == "add_info":
                id = request.form['info-key']
                info = content['info']
                info[id] = "Default"
                json_write(file_path, info, "info")
            elif action == "delete_info":
                id_to_delete = request.form['delete-info']
                info = content['info']
                if id_to_delete in info:
                    del info[id_to_delete]
                json_write(file_path, info, "info")
        return redirect(url_for("edit_page"))


    return render_template("edit.html",
        data=content,
        i18n=i18n,
        languages=languages,
        styles=styles
    )

if __name__ == "__main__":
    app.run(debug=True)