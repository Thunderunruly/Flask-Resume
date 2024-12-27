from flask import Flask, render_template
import json
import os

app = Flask(__name__)

@app.route("/")
def home():
    file_path = 'files/resume.json'

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)

    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    
    return render_template("index.html",
        data=content
    )

@app.route("/edit", method=["GET","POST"])
def edit_page():
    file_path = 'files/resume.json'

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({}, file, ensure_ascii=False, indent=4)

    with open(file_path, 'r', encoding='utf-8') as file:
        content = json.load(file)
    
    return render_template("edit.html",
        data=content
    )

if __name__ == "__main__":
    app.run(debug=True)