from flask import Flask, request, jsonify, send_from_directory

from werkzeug.utils import secure_filename
import os
import shutil
import webbrowser
import signal
import json

from Service import *
from temp import *
from entity import Image, Out, Info, CategoryManager, Note


class ImageApp:
    def __init__(self, info, out, category, note):
        self.app = Flask(__name__)
        self.img_dir = os.path.join(os.getcwd(), 'static/img')
        self.app.config['UPLOAD_FOLDER'] = 'static/img'
        self.setup_routes()
        self.info_json = info
        self.out_json = out
        self.cat = category
        self.note = note

    def setup_routes(self):
        app = self.app
        
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
                src_file = os.path.join(self.img_dir, filename)
                dst_file = os.path.join(self.img_dir, new_name)
                shutil.move(src_file, dst_file)
                tmp_image = Image(name=new_name)
                self.info_json.upload(tmp_image)
                self.info_json.save()
                return 'File uploaded successfully'


        @app.route('/')
        def hello_world():  # put application's code here
            return 'Hello World!'


        @app.route('/images_class', methods=['GET'])
        def get_images_class():
            try:
                
                files = os.listdir(self.img_dir)
                self.out_json.open()
                data = self.out_json.get_all()
                self.out_json.save()
                images = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) and file in data]
                return jsonify(images)
            except Exception as e:
                return str(e), 500

        @app.route('/images', methods=['GET'])
        def get_images():
            try:
                
                files = os.listdir(self.img_dir)
                data = self.info_json.same_day()
                images = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) and file in data]
                return jsonify(images)
            except Exception as e:
                return str(e), 500
            
        @app.route('/images_delete', methods=['GET'])
        def get_images_delete():
            try:
                
                files = os.listdir(self.img_dir)
                data = self.info_json.getImages("recycled")
                cmp = []
                for name in data:
                    cmp.append(name)
                images = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) and file in cmp]
                return jsonify(images)
            except Exception as e:
                return str(e), 500


        @app.route('/delete/<filename>', methods=['GET'])
        def delete_image(filename):
            try:
                tmp_image = Image(name=filename)
                self.info_json.recycle(tmp_image)    
                self.info_json.save()
                return 'File deleted successfully'
            except Exception as e:
                return str(e), 500
    
        @app.route('/kill/<filename>', methods=['GET'])
        def kill_image(filename):
            try:
                tmp_image = Image(name=filename)
                self.info_json.delete(tmp_image)    
                self.info_json.save()
                src_file = os.path.join(self.img_dir, filename)
                os.remove(src_file)
                return 'File totally deleted successfully'
            except Exception as e:
                return str(e), 500
    
        @app.route('/recover/<filename>', methods=['GET'])
        def recover_image(filename):
            try:
                tmp_image = Image(name=filename)
                self.info_json.unrecycle(tmp_image)
                self.info_json.save()
                return 'File recover successfully'
            except Exception as e:
                return str(e), 500
        
        @app.route('/categories')
        def get_categories():
            return jsonify(self.cat.get_categories())

        @app.route('/submit-category', methods=['POST'])
        def submit_category():
            data = request.get_json()
            category = data.get('category')
            data = self.info_json.getImages(category)
            self.out_json.open()
            self.out_json.clean()
            self.out_json.save_all(data)
            self.out_json.save()
            return jsonify({'message': f'get:{category}'})

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

        def is_char_digit(s):
            # 首先检查字符串是否为空，以避免索引错误
            if s:  # 确保字符串不为空
                return s[0:4].isdigit()  # 检查第一个字符是否是数字
            else:
                return False  # 如果字符串为空，则返回False

        @app.route('/check_submit/<ctx>', methods=['GET'])
        def check_submit(ctx):
            try:
                ### ctx 判断！！鲁棒性
                info = loadInfo()
                if is_char_digit(ctx):
                    out.open()
                    all = info["labels"]
                    for label in all:
                        for name in all[label]:
                            if ctx == name[0:10]:
                                out.add_image(name)
                    out.save()
                else:
                    data = info["labels"][ctx]
                    with open('out.json', 'w', encoding='utf-8') as file:
                        json.dump(data, file, ensure_ascii=False, indent=4)
                
                return 'open successfully'
            except Exception as e:
                return str(e), 500


        @app.route('/submit/<ctx>/<filename>', methods=['GET'])
        def submit(ctx,filename):
            try:
                labels = self.cat.get_categories()
                if ctx not in labels:
                    self.cat.add_category(ctx)
                tmp_image = Image(name=filename,label=ctx)
                self.info_json.changeLabel(tmp_image)
                self.info_json.save()
                return 'Change label successfully'
            except Exception as e:
                return str(e), 500
            
        @app.route('/note.html')
        def note_page():
            return send_from_directory('static', 'note.html')
        

        @app.route('/annotations/<filename>', methods=['GET'])
        def get_annotations(filename):
            annotations = self.note.load()
            annots = annotations.get(filename, [])
            return jsonify(annots)

        @app.route('/add_annotation', methods=['POST'])
        def add_annotation():
            annotations = self.note.load()
            data = request.get_json()
            filename = data['filename']
            text = data['annotation']
            annotation_id = str(len(annotations.get(filename, [])) + 1)  # 简单的ID生成逻辑
            if filename not in annotations:
                annotations[filename] = []
            annotations[filename].append({'id': annotation_id, 'text': text})
            self.note.new_data(annotations)
            self.note.save()
            return jsonify({'message': 'Annotation added successfully'})

        @app.route('/update_annotation/<annotation_id>', methods=['POST'])
        def update_annotation(annotation_id):
            annotations = self.note.load()
            data = request.get_json()
            text = data['text']
            for annot_list in annotations.values():
                for annot in annot_list:
                    if annot["id"] == annotation_id:
                        annot["text"] = text
                        self.note.new_data(annotations)
                        self.note.save()
                        return jsonify({'message': 'Annotation updated successfully'})
            return jsonify({'message': 'Annotation not found'}), 404

        @app.route('/delete_annotation/<annotation_id>', methods=['DELETE'])
        def delete_annotation(annotation_id):
            annotations = self.note.load()
            for annot_list in annotations.values():
                for annot in annot_list:
                    if annot["id"] == annotation_id:
                        annot_list.remove(annot)
                        self.note.new_data(annotations)
                        self.note.save()
                        return jsonify({'message': 'Annotation deleted successfully'})
            return jsonify({'message': 'Annotation not found'}), 404
        
        @app.route('/shutdown', methods=['POST'])
        def shutdown_server():
            os.kill(os.getpid(), signal.SIGTERM)
            return "Shutting down", 200




 
        
    def run(self):
        self.app.run()

if __name__ == '__main__':
    url = 'http://127.0.0.1:5000/static/index.html'
    webbrowser.open(url)
    info = Info()
    out = Out()
    note = Note()
    cat = CategoryManager(info.get_labels())
    image_app = ImageApp(info=info, out=out, category=cat, note=note)
    image_app.run()
