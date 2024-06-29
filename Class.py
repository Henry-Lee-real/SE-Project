import json
from datetime import datetime
import os
import base64

class Image:
    def __init__(self, name, label="no label"):
        self.name = name
        self.label = label
        
class JsonFileHandler:
    def __init__(self, filepath):
        self.filepath = filepath

    def load_data(self):
        """Load data from a JSON file."""
        try:
            with open(self.filepath, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}  # Return an empty dictionary if the file doesn't exist

    def save_data(self, data):
        """Save data to a JSON file."""
        with open(self.filepath, 'w') as file:
            json.dump(data, file, indent=4)
            return True


class Note:
    def __init__(self):
        self.data_handler = JsonFileHandler("note.json")
        self.data = self.data_handler.load_data()

    def save(self):
        return self.data_handler.save_data(self.data)

    def load(self):
        return self.data
    
    def delete(self, image):
        if image.name in self.data:
            self.data.pop(image.name)
            self.save()  # Save changes after modification

    def new_data(self, data):
        self.data = data
        self.save()  # Save changes after setting new data

class Status:
    def __init__(self):
        self.data_handler = JsonFileHandler("out.json")
        self.data = {'empty':0}
    
    def open(self):
        self.data = self.data_handler.load_data()
        return self.data

    def change_status(self, status):
        self.data = status
        return self.save()
    
    def clean(self):
        self.data = {'empty':0}
        return self.save()
    
    def save(self):
        return self.data_handler.save_data(self.data)




class Time:
    def is_over_30_days(self, time1, time2):
        time_format = '%Y-%m-%d-%H-%M-%S'
        date1 = datetime.strptime(time1, time_format)
        date2 = datetime.strptime(time2, time_format)
        date_diff = abs((date2 - date1).days)
        return date_diff > 30
    
    def selectByTime(self, time1, time2, info):
        data = info.load()
        labels = data['info']['labels'].copy()
        labels.remove('private')
        labels.remove('recycled')
        print(labels)
        imgs = []
        if time2:
            time1 = datetime.strptime(time1, "%Y-%m-%d-%H-%M-%S")
            time2 = datetime.strptime(time2, "%Y-%m-%d-%H-%M-%S")
            for label in labels:
                images = data['labels'][label]
                for img in images:
                    img_time = img.replace(".png", "")
                    img_obj = datetime.strptime(img_time, "%Y-%m-%d-%H-%M-%S")
                    if time1 <= img_obj <= time2:
                        imgs.append(img)

        else:
            for label in labels:
                print(label)
                images = data['labels'][label]
                for img in images:
                    img_time = img.replace(".png", "")
                    img_obj = datetime.strptime(img_time, "%Y-%m-%d-%H-%M-%S")
                    if img_obj.strftime("%Y-%m-%d") == time1:
                        imgs.append(img)
        return imgs
    
    def same_day(self, info):
        data = info.load()
        out = []
        now = datetime.now()
        t = now.strftime("%Y-%m-%d-%H-%M-%S")#XXXX-XX-XX
        All = data['labels']
        for label in All:
            if label == "recycled" or label == "private":
                continue
            for image in All[label]:
                if image[5:10] == t[5:10]:
                    out.append(image)
        return out
    
    # 检测回收站内的图片是否超过30天，在每次实例化的时候调用，返回应被删除的图片名
    def RecycleCheck(self, info):
        data = info.load()
        now = datetime.now()
        t = now.strftime("%Y-%m-%d-%H-%M-%S")
        delete = []
        for name in data['labels']['recycled']:
            past_time = data['labels']['recycled'][name]
            if self.is_over_30_days(past_time, t):
                delete.append(name)
                data['labels']['recycled'].remove((name, past_time))
        return data#info.update()



class Private:
    # 返回隐私空间的图片
    def getPrivate(self, password, info):
        data = info.load()
        if password != data['info']['password']:
            return False
        imgs = data['labels']['private']
        images = []
        for img in imgs:
            path = os.path.join(data['info']['path'], img)
            path_ = os.path.join(data['info']['path'], 'P'+img)
            with open(path, "r") as fp:
                data_ = fp.read()
                result = ''
                for i in data_:
                    result += chr(ord(i) - 5)
                result = base64.b64decode(result)
            with open(path_, 'wb') as file:
                file.write(result)
            images.append(img)
        return images

    # 加入隐私空间
    def private(self, img, info):
        data = info.load()
        img.label = 'private'
        info.changeLabel(img)
        path = os.path.join(data['info']['path'], img.name)
        with open(path, "rb") as fp:
            data_ = fp.read()
            source = base64.b64encode(data_).decode()
            result = ''
            for i in source:
                result += chr(ord(i) + 5)
        os.remove(path)
        with open(path, 'w') as file:
            file.write(result)
        return data #info.update()

    # 移出隐私空间
    def privateRemove(self, img, info):
        data = info.load()
        img.label = 'no label'
        info.changeLabel(img)
        path = os.path.join(data['info']['path'], img.name)
        with open(path, "r") as fp:
            data_ = fp.read()
            result = ''
            for i in data_:
                result += chr(ord(i) - 5)
            result = base64.b64decode(result)
        os.remove(path)
        with open(path, 'wb') as file:
            file.write(result)
        return data #info.update()

# 对info的控制类
class Info:
    def __init__(self):
        self.file_handler = JsonFileHandler("info.json")
        self.data = self.file_handler.load_data()

    def save(self):
        return self.file_handler.save_data(self.data)
    
    def load(self):
        return self.data
    
    def update(self, data):
        self.data = data
        return self.save()

    #上传一张图片
    def upload(self, image):
        labels = self.data.setdefault('labels', {})
        labels.setdefault(image.label, []).append(image.name)
        self.data['info']['total'] = self.data.get('info', {}).get('total', 0) + 1
        return self.save()
    
    
    #获得一张图片
    def getImages(self, label='no label'):
        return self.data.get('labels', {}).get(label, [])
    
    def change_password(self, password):
        self.data['info']['password'] = password
        return self.save()


    #改变类别
    def changeLabel(self, img):
        if img.label == 'loved':
            if img.name not in self.data['labels']['loved']:
                self.data['labels']['loved'].append(img.name)
            self.save()
            return True
        labels = self.data['info']['labels']
        
        if img.label not in labels:
            self.data['info']['labels'].append(img.label)
            self.data['labels'][img.label] = []
        
        if img.name not in self.data['labels'][img.label]:
            self.data['labels'][img.label].append(img.name)
        for lab in labels:
            if lab != "recycled" and lab != img.label:
                if img.name in self.data['labels'][lab]:
                    self.data['labels'][lab].remove(img.name)
        self.save()
        return True
    
    # 回收照片
    def recycle(self, img):
        now = datetime.now()
        t = now.strftime("%Y-%m-%d-%H-%M-%S")
        self.data['labels']['recycled'][img.name] = t
        for label in self.data['labels']:
            if label == 'recycled':
                continue
            else:
                if img.name in self.data['labels'][label]:
                    self.data['labels'][label].remove(img.name)
        self.save()
        return True

    # 撤销回收
    def unrecycle(self, img):
        for name in self.data['labels']['recycled']:
            if name == img.name:
                self.data['labels']['recycled'].pop(name)
                self.data['labels']['no label'].append(name)
                self.save()
                return True
        return False

    # 彻底删除
    def delete(self, img):
        for name in self.data['labels']['recycled']:
            if img.name == name:
                self.data['labels']['recycled'].pop(name)
                self.data['info']['total'] -= 1
                self.save()
                return True
        for name in self.data['labels']['private']:
            if img.name == name:
                self.data['labels']['private'].remove(name)
                self.data['info']['total'] -= 1
                self.save()
                return True

    def get_labels(self):
        out = []
        All = self.data['labels']
        for label in All:
            if label == "recycled" or label == "private":
                continue
            out.append(label)
        return out
    
    def check_empty_class(self):
        out = []
        labels = self.data['info']['labels'].copy()
        labels.remove('private')
        labels.remove('recycled')
        labels.remove('loved')
        labels.remove('no label')
        for label in labels:
            if self.data['labels'][label] == []:
                self.data['labels'].pop(label)
                self.data['info']['labels'].remove(label)
                out.append(label)
        self.save()
        return out
            
        
        
class CategoryManager:
    def __init__(self, labels):
        self.categories = labels  # 初始分类列表

    def get_categories(self):
        return self.categories

    def add_category(self, name):
        if name not in self.categories:
            self.categories.append(name)

    def remove_category(self, name):
        if name in self.categories:
            self.categories.remove(name)