from flask import Flask, request, jsonify

from werkzeug.utils import secure_filename
import os

import json

app = Flask(__name__)
img_dir = os.path.join(os.getcwd(), 'static/img')

# 设置上传文件的保存路径
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File uploaded successfully'


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/images', methods=['GET'])
def get_images():
    try:
        
        files = os.listdir(img_dir)
        with open('out.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        images = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) and file in data]
        print(images)
        return jsonify(images)
    except Exception as e:
        return str(e), 500


@app.route('/delete/<filename>', methods=['GET'])
def delete_image(filename):
    try:
        os.remove(os.path.join(img_dir, filename))
        return 'File deleted successfully'
    except Exception as e:
        return str(e), 500


def handle(ctx):
    if ctx == str(1):
        print(1)
        with open('out.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 修改数据
        data.append("pexels-pok-rie-33563-2049422.jpg")

        # 保存更改到文件
        with open('out.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            
    elif ctx == "收藏":
        with open('out1.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 修改数据
        data.append("pexels-pok-rie-33563-2049422.jpg")

        # 保存更改到文件
        with open('out1.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    return ctx


@app.route('/submit/<ctx>', methods=['GET'])
def submit(ctx):
    try:
        handle(ctx)
        return ctx
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run()
