from flask import Flask, request, jsonify

from werkzeug.utils import secure_filename
import os
import shutil

import json

from Service import *
from temp import *

app = Flask(__name__)
img_dir = os.path.join(os.getcwd(), 'static\\img')

# 设置上传文件的保存路径
UPLOAD_FOLDER = 'static\\img'
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
        name = selectName()
        new_name = name+".png"
        src_file = os.path.join(img_dir, filename)
        dst_file = os.path.join(img_dir, new_name)
        shutil.move(src_file, dst_file)
        uploadImage(new_name)
        return 'File uploaded successfully'


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/images_class', methods=['GET'])
def get_images_class():
    try:
        
        files = os.listdir(img_dir)
        with open('out.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        images = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) and file in data]
        print(images)
        return jsonify(images)
    except Exception as e:
        return str(e), 500

@app.route('/images', methods=['GET'])
def get_images():
    try:
        
        files = os.listdir(img_dir)
        info = loadInfo()
        data = info["labels"]["no labels"]
        print(data)
        images = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) and file in data]
        print(images)
        return jsonify(images)
    except Exception as e:
        return str(e), 500
    
@app.route('/images_delete', methods=['GET'])
def get_images_delete():
    try:
        
        files = os.listdir(img_dir)
        info = loadInfo()
        data = info["labels"]["recycled"]
        cmp = []
        for name in data:
            cmp.append(name[0])
        images = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) and file in cmp]
        return jsonify(images)
    except Exception as e:
        return str(e), 500


@app.route('/delete/<filename>', methods=['GET'])
def delete_image(filename):
    try:
        recycle(filename)
        return 'File deleted successfully'
    except Exception as e:
        return str(e), 500
    
@app.route('/kill/<filename>', methods=['GET'])
def kill_image(filename):
    try:
        delete_click(filename)
        src_file = os.path.join(img_dir, filename)
        os.remove(src_file)
        return 'File totally deleted successfully'
    except Exception as e:
        return str(e), 500
    
@app.route('/recover/<filename>', methods=['GET'])
def recover_image(filename):
    try:
        unrecycle(filename)        
        return 'File recover successfully'
    except Exception as e:
        return str(e), 500


def handle(ctx):
    if ctx == "all":
        writeOut
        # print(1)
        # with open('out.json', 'r', encoding='utf-8') as file:
        #     data = json.load(file)

        # # 修改数据
        # data.append("pexels-pok-rie-33563-2049422.jpg")

        # # 保存更改到文件
        # with open('out.json', 'w', encoding='utf-8') as file:
        #     json.dump(data, file, ensure_ascii=False, indent=4)
            
    elif ctx == "收藏":
        with open('out1.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 修改数据
        data.append("pexels-pok-rie-33563-2049422.jpg")

        # 保存更改到文件
        with open('out1.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    return ctx

@app.route('/check_submit/<ctx>', methods=['GET'])
def check_submit(ctx):
    try:
        ### ctx 判断！！鲁棒性
        info = loadInfo()
        data = info["labels"][ctx]
        with open('out.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        
       
        
        return 'open successfully'
    except Exception as e:
        return str(e), 500


@app.route('/submit/<ctx>/<filename>', methods=['GET'])
def submit(ctx,filename):
    try:
        
        ## 鲁棒性
        changeLabel(filename,ctx)
        
        return 'Change label successfully'
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run()
