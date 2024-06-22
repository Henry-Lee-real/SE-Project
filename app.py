from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import cv2
from werkzeug.utils import secure_filename
import os
import shutil
import webbrowser
import signal
import json
import re

from Service import *
from temp import *
from Class import Image, Status, Info, CategoryManager, Note


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
                return 'File uploaded successfully'


        @app.route('/')
        def hello_world():  # put application's code here
            return 'Hello World!'
        
        def get_class_image(category):
            files = os.listdir(self.img_dir)
            data = self.info_json.getImages(category)
            re_out = self.info_json.getImages("recycled")
            images = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) and file in data and file not in re_out]
            return images
        
        def get_private_image():
            files = os.listdir(self.img_dir)
            data = self.info_json.getImages("private")
            Pdata = []
            for file in data:
                Pdata.append('P'+file)
            images = [file for file in files if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) and file in Pdata]
            return images

        @app.route('/images_class', methods=['GET'])
        def get_images_class():
            try:
                Dict = self.out_json.open()
                first_key = next(iter(Dict))
                first_value = Dict[first_key]
                if first_key == "class":
                    images = get_class_image(first_value)
                if first_key == "empty":
                    images = get_class_image("no label")
                if first_key == "time2":
                    images = self.info_json.selectByTime(first_value[0], first_value[1])
                if first_key == "time1":
                    images = self.info_json.selectByTime(first_value[0], None)
                if first_key == "private":
                    images = get_private_image()
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
            
        @app.route('/process_data', methods=['POST'])
        def process_data():
            data = request.get_json()  # 解析JSON数据
            category = data.get('category')  # 获取类别
            filename = data.get('filename')  # 获取文件名
            # Dict = self.out_json.open()
            # first_key = next(iter(Dict))
            # if first_key == "private":
            #     if category == "kill"
            tmp_image = Image(name=filename,label=category)
            self.cat.add_category(category)
            self.info_json.changeLabel(tmp_image)
            return "ok"
        
        @app.route('/collect_image', methods=['POST'])
        def collect_image():
            # 获取JSON数据
            data = request.get_json()
            filename = data.get('filename')  
            tmp_image = Image(name=filename,label="loved")
            self.info_json.changeLabel(tmp_image)
            return "ok"
        
        def Guided_filter(input_img, eps = 0.01):
            p = input_img.astype(np.float32) / 255
            I = p
            height, width = I.shape[:2]

            r = 5
            q = np.zeros((height, width), dtype=np.float32)

            mean_I = cv2.blur(I, (r, r))
            mean_p = cv2.blur(p, (r, r))
            mean_Ip = cv2.blur(I * p, (r, r))
            mean_II = cv2.blur(I * I, (r, r))

            cov_Ip = mean_Ip - mean_I * mean_p
            var_I = mean_II - mean_I * mean_I

            a = cov_Ip / (var_I + eps)
            b = mean_p - a * mean_I

            mean_a = cv2.blur(a, (r, r))
            mean_b = cv2.blur(b, (r, r))

            q = mean_a * I + mean_b
            imgGuidedFilter = (q * 255).astype(np.uint8)
            

            return imgGuidedFilter

        
        @app.route('/noisy_image', methods=['POST'])
        def noisy_image():
            # 获取JSON数据
            data = request.get_json()
            filename = data.get('filename')  
            src_file = os.path.join(self.img_dir, filename)
            dst_file = os.path.join(self.img_dir, filename)
            img = cv2.imread(src_file)
            img = Guided_filter(img)
            cv2.imwrite(dst_file, img)
            return "ok"



        @app.route('/delete/<filename>', methods=['GET'])
        def delete_image(filename):
            try:
                Dict = self.out_json.open()
                first_key = next(iter(Dict))
                if first_key == "private":
                    kill_image(filename[1:])
                    kill_image(filename)
                    return 'File deleted successfully'
                tmp_image = Image(name=filename)
                self.info_json.recycle(tmp_image)
                out = self.info_json.check_empty_class()
                if out != []:
                    for label in out:
                        self.cat.remove_category(label)
                return 'File deleted successfully'
            except Exception as e:
                return str(e), 500
    
        @app.route('/kill/<filename>', methods=['GET'])
        def kill_image(filename):
            try:
                tmp_image = Image(name=filename)
                self.info_json.delete(tmp_image)    
                self.note.delete(tmp_image)
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
            Dict = {'class': category}
            self.out_json.change_status(Dict)
            close_private()
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
        
        def validate_and_transform(date_string):
            # 尝试将输入的字符串转换为日期对象
            try:
                # 格式化日期
                date1 = datetime.strptime(date_string[:10], "%Y-%m-%d")
            except ValueError:
                return None, "Invalid date format. Expected format: YYYY-MM-DD"
            try:
                # 格式化日期
                date2 = datetime.strptime(date_string[11:], "%Y-%m-%d")
            except ValueError:
                return None, "Invalid date format. Expected format: YYYY-MM-DD"

            # 创建一天开始和结束的时间字符串
            start_of_day = date1.strftime("%Y-%m-%d-00-00-00")
            end_of_day = date2.strftime("%Y-%m-%d-23-59-59")
            return [start_of_day, end_of_day], None  # 返回格式化的日期范围和无错误
        
        def validate_one(date_string):
            # 尝试将输入的字符串转换为日期对象
            try:
                # 格式化日期
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return None
            
        def validate_input(input_string):
            # 正则表达式匹配 "private" 后跟中文或英文冒号，然后是六位数字
            pattern = r'^private[：:]\d{6}$'
            if re.match(pattern, input_string):
                return True
            else:
                return False
        
        def close_private():
            for filename in os.listdir(self.img_dir):
                    file_path = os.path.join(self.img_dir, filename)
                    if filename.startswith('P') and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        os.remove(file_path)
        
        @app.route('/check_submit/<ctx>', methods=['GET'])
        def check_submit(ctx):
            try:
                data, error = validate_and_transform(ctx)
                if data:
                    close_private()
                    Dict = {'time2': data}
                    self.out_json.change_status(Dict)
                    return 'open successfully'
                
                data = validate_one(ctx)
                if data:
                    close_private()
                    Dict = {'time1': [data]}
                    self.out_json.change_status(Dict)
                    return 'open successfully'
                    
                if validate_input(ctx):
                    Dict = self.out_json.open()
                    first_key = next(iter(Dict))
                    if first_key == 'private':
                        self.info_json.change_password(ctx[8:])
                        return 'change password successfully'
                    data = self.info_json.getPrivate(ctx[8:])
                    if data == False:
                        return 'error'                
                    else:
                        Dict = {'private': 1}
                        self.out_json.change_status(Dict)
                        return 'open successfully'
                    
                if ctx == "close" or ctx == "CLOSE":
                    close_private()
                    self.out_json.clean()
                    return 'close successfully'
                                    
                
                return 'not correct'
            except Exception as e:
                return str(e), 500


        @app.route('/submit/<ctx>/<filename>', methods=['GET'])
        def submit(ctx,filename):
            try:
                if ctx == 'private':
                    tmp_image = Image(name=filename,label=ctx)
                    self.info_json.private(tmp_image)
                    return 'Change label successfully'
                labels = self.cat.get_categories()
                if ctx == "":
                    return 'Error input'
                if ctx not in labels:
                    self.cat.add_category(ctx)
                tmp_image = Image(name=filename,label=ctx)
                self.info_json.changeLabel(tmp_image)
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
    out = Status()
    note = Note()
    cat = CategoryManager(info.get_labels())
    image_app = ImageApp(info=info, out=out, category=cat, note=note)
    image_app.run()
