from flask import Flask, render_template, request, redirect, url_for
import json
import os
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

file_path = 'files/resume.json'

resume_template = {
    "info":{},
    "education":[],
    "skill":{},
    "experience":[],
    "style":"basic"
}

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
            json.dump(resume_template, file, ensure_ascii=False, indent=4)

    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    return content

def json_write(file_path, value, key):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(resume_template, file, ensure_ascii=False, indent=4)

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
    content = json_content(file_path)

    language = content.get('language', 'en_US')

    style = content.get('style', 'basic')

    i18n = json_content(f"i18n/{language}.json")
    
    languages = get_filename_list("i18n")

    styles = get_filename_list("static/css")

    if request.method == 'POST':
        form_id = request.form.get('form_id')
        if form_id == 'language_form':
            change_language(language)
        elif form_id == 'style_form':
            change_style(style)
        elif form_id == "edit_form":
            action = request.form.get('action')
            if action == "save":
                save_resume()
            elif action == "cancel":
                pass
            elif action == "add_info":
                add_more_info(content)
            elif action == "delete_info":
                delete_info(content)
        elif form_id == "skill_form":
            skill_index = int(request.form['skill_index'])
            skill_key = request.form['skill_key']
            action = request.form.get('action')
            skill = content['skill']
            if action == "add":
                skill[skill_key].insert(skill_index, "")
            elif action == "delete":
                skill[skill_key].pop(skill_index - 1)
            elif action == "add_more":
                if skill_key and skill_key not in skill:
                    skill[skill_key] = []
            elif action == "delete_key":
                del skill[skill_key]
            json_write(file_path,skill,"skill")
        elif form_id == "education_form":
            action = request.form.get("action")
            if action == "add":
                education = content['education']
                education.append({
                    "school": "",
                    "school_original_name": "",
                    "duration": " - ",
                    "major": "",
                    "major_orginal_name": ""
                },)
                json_write(file_path, education, "education")
            elif action == "delete":
                pass
        return redirect(url_for("edit_page"))


    return render_template("edit.html",
        data=content,
        i18n=i18n,
        languages=languages,
        styles=styles
    )

def delete_info(content):
    id_to_delete = request.form['delete-info']
    info = content['info']
    if id_to_delete in info:
        del info[id_to_delete]
    json_write(file_path, info, "info")

def add_more_info(content):
    id = request.form['info-key']
    info = content['info']
    info[id] = "Default"
    json_write(file_path, info, "info")

def change_style(style):
    css = request.form.get('style', style)
    json_write(file_path,css,"style")

def change_language(language):
    lang = request.form.get('language', language)
    json_write(file_path,lang,"language")

def save_resume():
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
    bio = request.form['bio']
    json_write(file_path,bio,"bio")
    skill_professional = request.form.getlist("professional[]")
    skill_language = request.form.getlist("language[]")
    skill_office = request.form.getlist("office[]")
    skill = {
                    "professional":skill_professional,
                    "language":skill_language,
                    "office":skill_office
                }
    json_write(file_path,skill,"skill")
    education_dist = []
    for key, value in request.form.items():
        if key.startswith("education["):
            index = int(key.split('[')[1].split(']')[0])
            field = key.split('[')[2].split(']')[0]
            while len(education_dist) <= index:
                education_dist.append({})
            education_dist[index][field] = value
    json_write(file_path,education_dist,"education")
    experience_dist = []
    for key, value in request.form.items():
        if key.startswith("experience["):
            index = int(key.split('[')[1].split(']')[0])
            field = key.split('[')[2].split(']')[0]
            while len(experience_dist) <= index:
                experience_dist.append({})
            experience_dist[index][field] = value
    json_write(file_path,experience_dist,"experience")

if __name__ == "__main__":
    subprocess.run(["python", "init.py"])
    app.run(debug=True)