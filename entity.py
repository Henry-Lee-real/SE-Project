import json
from datetime import datetime
import os
import base64

class Image:
    def __init__(self, name, note="", label="no label"):
        self.name = name
        self.label = label


# 读取所有图片信息
def loadInfo_note():
    with open("note.json", "r") as infoFp:
        info = json.load(infoFp)
    return info


# 更新info
def updateInfo_note(info):
    with open('note.json', 'w') as infoFp:
        json.dump(info, infoFp)
    return True

class Note:
    def __init__(self):
        self.data = loadInfo_note()

    def save(self):
        if updateInfo_note(self.data):
            return True
        return False

    def load(self):
        return self.data
    
    def delete(self,image):
        self.data.pop(image.name)
    
    def new_data(self,data):
        self.data = data
    
class Out:
    def __init__(self):
        self.path = "out.json"
        self.data = []
        self.status = False
    
    def open(self):
        if self.status:
            return False
        with open(self.path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
            self.status = True
            return True
        
    def add_image(self, image):
        if self.status:
            self.data.append(image)
            return True
        
    def save_all(self, data):
        if self.status:
            self.data = data
            return True
        
    def get_all(self):
        return self.data
    
    def clean(self):
        if self.status:
            self.data = []
            return True
    
    def save(self):
        if self.status == False:
            return False
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)
            self.data = []
            self.status = False
        return True
    



# 读取所有图片信息
def loadInfo():
    with open("info.json", "r") as infoFp:
        info = json.load(infoFp)
    return info


# 更新info
def updateInfo(info):
    with open('info.json', 'w') as infoFp:
        json.dump(info, infoFp)
    return True


def is_over_30_days(time1, time2):
    time_format = '%Y-%m-%d-%H-%M-%S'
    date1 = datetime.strptime(time1, time_format)
    date2 = datetime.strptime(time2, time_format)
    date_diff = abs((date2 - date1).days)
    return date_diff > 30


# 对info的控制类
class Info:
    def __init__(self):
        self.data = loadInfo()

    def save(self):
        if updateInfo(self.data):
            return True
        return False

    # 上传图片
    def upload(self, image):
        self.data['labels'][image.label].append(image.name)
        self.data['info']['total'] += 1
        return True

    # 根据用户选择的label输出图片，默认为no label
    def getImages(self, label):
        if label is None:
            label = 'no label'
        imgs = self.data['labels'][label]
        return imgs

    # 改变某张图片的label
    def changeLabel(self, img):
        if img.label == 'loved':
            if img.name not in self.data['labels']['loved']:
                self.data['labels']['loved'].append(img.name)
            return True
        labels = self.data['info']['labels']
        
        if img.label not in labels:
            self.data['info']['labels'].append(img.label)
            self.data['labels'][img.label] = []
        
        if img.name not in self.data['labels'][img.label]:
            self.data['labels'][img.label].append(img.name)
        for lab in labels:
            if lab != 'loved' and lab != "recycled" and lab != img.label:
                if img.name in self.data['labels'][lab]:
                    self.data['labels'][lab].remove(img.name)
                return True

    # # 改变注释
    # def changeNote(self, img):
    #     self.data['note'][img.name] = img.note
    #     return True

    # 根据时间筛选,格式需为"%Y-%m-%d-%H-%M-%S"
    def selectByTime(self, time1, time2):
        labels = self.data['info']['labels'].copy()
        labels.remove('private')
        labels.remove('recycled')
        imgs = []
        if time2:
            time1 = datetime.strptime(time1, "%Y-%m-%d-%H-%M-%S")
            time2 = datetime.strptime(time2, "%Y-%m-%d-%H-%M-%S")
            for label in labels:
                images = self.data['labels'][label]
                for img in images:
                    print(2)
                    img_time = img.replace(".png", "")
                    print(1)
                    img_obj = datetime.strptime(img_time, "%Y-%m-%d-%H-%M-%S")
                    if time1 <= img_obj <= time2:
                        imgs.append(img)

        else:
            for label in labels:
                images = self.data['labels'][label]
                for img in images:
                    img_time = img.replace(".png", "")
                    img_obj = datetime.strptime(img_time, "%Y-%m-%d-%H-%M-%S")
                    if img_obj.strftime("%Y-%m-%d") == time1:
                        imgs.append(img)
        # imgs = sorted(imgs, key=lambda x: datetime.strptime(x, "%Y-%m-%d-%H-%M-%S"), reverse=True)
        return imgs

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
        return True

    # 撤销回收
    def unrecycle(self, img):
        for name in self.data['labels']['recycled']:
            if name == img.name:
                self.data['labels']['recycled'].pop(name)
                self.data['labels']['no label'].append(name)
                return True
        return False

    # 彻底删除
    def delete(self, img):
        for name in self.data['labels']['recycled']:
            if img.name == name:
                self.data['labels']['recycled'].pop(name)
                self.data['info']['total'] -= 1
                return True

    # 检测回收站内的图片是否超过30天，在每次实例化的时候调用，返回应被删除的图片名
    def RecycleCheck(self):
        now = datetime.now()
        t = now.strftime("%Y-%m-%d-%H-%M-%S")
        delete = []
        for name in self.data['labels']['recycled']:
            past_time = self.data['labels']['recycled'][name]
            if is_over_30_days(past_time, t):
                delete.append(name)
                self.data['labels']['recycled'].remove((name, past_time))
        return delete
    
    
    def same_day(self):
        out = []
        now = datetime.now()
        t = now.strftime("%Y-%m-%d-%H-%M-%S")#XXXX-XX-XX
        All = self.data['labels']
        for label in All:
            if label == "recycled" or label == "private":
                continue
            for image in All[label]:
                if image[5:10] == t[5:10]:
                    out.append(image)
        return out
    
    def get_labels(self):
        out = []
        All = self.data['labels']
        for label in All:
            if label == "recycled" or label == "private":
                continue
            out.append(label)
        return out
    
    # 返回隐私空间的图片
    def getPrivate(self, password):
        if password != self.data['info']['password']:
            return False
        imgs = self.data['labels']['private']
        images = []
        for img in imgs:
            path = os.path.join(self.data['info']['path'], img)
            path_ = os.path.join(self.data['info']['path'], 'P'+img)
            with open(path, "r") as fp:
                data = fp.read()
                result = ''
                for i in data:
                    result += chr(ord(i) - 5)
                result = base64.b64decode(result)
            with open(path_, 'wb') as file:
                file.write(result)
            images.append(img)
        return images

    # 加入隐私空间
    def private(self, img):
        img.label = 'private'
        self.changeLabel(img)
        path = os.path.join(self.data['info']['path'], img.name)
        with open(path, "rb") as fp:
            data = fp.read()
            source = base64.b64encode(data).decode()
            result = ''
            for i in source:
                result += chr(ord(i) + 5)
        os.remove(path)
        with open(path, 'w') as file:
            file.write(result)
        return True

    # 移出隐私空间
    def privateRemove(self, img):
        img.label = 'no label'
        self.changeLabel(img)
        path = os.path.join(self.data['info']['path'], img.name)
        with open(path, "r") as fp:
            data = fp.read()
            result = ''
            for i in data:
                result += chr(ord(i) - 5)
            result = base64.b64decode(result)
        os.remove(path)
        with open(path, 'wb') as file:
            file.write(result)
        return True
        
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