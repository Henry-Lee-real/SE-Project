import json
from datetime import datetime


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
        self.data['note'][image.name] = image.note
        self.data['info']['total'] += 1
        return True

    # 根据用户选择的label输出图片，默认为no label
    def getImages(self, img):
        label = img.label
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
        if img.name not in self.data['labels'][img.label]:
            self.data['labels'][img.label].append(img.name)
        for lab in labels:
            if lab != 'loved' and lab != "recycled" and lab != img.label:
                if img.name in self.data['labels'][lab]:
                    self.data['labels'][lab].remove(img.name)
        return True

    # 改变注释
    def changeNote(self, img):
        self.data['note'][img.name] = img.note
        return True

    # 根据时间筛选,格式需为"%Y-%m-%d-%H-%M-%S"
    def selectByTime(self, time1, time2):
        labels = self.data['info']['labels'].copy()
        labels.remove('loved')
        labels.remove('recycled')
        imgs = []
        if time2:
            time1 = datetime.strptime(time1, "%Y-%m-%d-%H-%M-%S")
            time2 = datetime.strptime(time2, "%Y-%m-%d-%H-%M-%S")
            for label in labels:
                images = self.data['labels'][label]
                for img in images:
                    img_time = img.replace(".png", "")
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
        imgs = sorted(imgs, key=lambda x: datetime.strptime(x, "%Y-%m-%d-%H-%M-%S"), reverse=True)
        return imgs

    # 回收照片
    def recycle(self, img):
        now = datetime.now()
        t = now.strftime("%Y-%m-%d-%H-%M-%S")
        self.data['labels']['recycled'].append((img.name, t))
        for label in self.data['labels']:
            if label == 'recycled':
                continue
            else:
                if img.name in self.data['labels'][label]:
                    self.data['labels'][label].remove(img.name)
        return True

    # 撤销回收
    def unrecycle(self, img):
        for (name, past_time) in self.data['labels']['recycled']:
            if name == img.name:
                self.data['labels']['recycled'].remove((name, past_time))
                self.data['labels']['no label'].append(name)
        return True

    # 彻底删除
    def delete(self, img):
        for (name, past_time) in self.data['labels']['recycled']:
            if img.name == name:
                self.data['labels']['recycled'].remove((name, past_time))
        return True

    # 检测回收站内的图片是否超过30天，在每次实例化的时候调用，返回应被删除的图片名
    def RecycleCheck(self):
        now = datetime.now()
        t = now.strftime("%Y-%m-%d-%H-%M-%S")
        delete = []
        for (name, past_time) in self.data['labels']['recycled']:
            if is_over_30_days(past_time, t):
                delete.append(name)
                self.data['labels']['recycled'].remove((name, past_time))
        return delete
