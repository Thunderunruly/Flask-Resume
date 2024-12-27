from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

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
            return redirect(url_for("edit_page"))
        if form_id == 'style_form':
            css = request.form.get('style', style)
            json_write(file_path,css,"style")
            return redirect(url_for("edit_page"))

    return render_template("edit.html",
        data=content,
        i18n=i18n,
        languages=languages,
        styles=styles
    )

if __name__ == "__main__":
    app.run(debug=True)