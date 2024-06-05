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
    return


# 写out.json
def writeOut(input):
    with open('out.json', 'w') as outFp:
        json.dump(input, outFp)
    return


# 根据用户选择的label输出图片，默认为no label
def getImages(label=None):
    if label is None:
        label = 'no label'
    info = loadInfo()
    pictures = info['labels'][label]
    writeOut(pictures)
    return


# 改变某张图片的label
def changeLabel(name, label):
    info = loadInfo()
    labels = list(info['labels'])
    info['labels'][label].append(name)
    for lab in labels:
        if lab != 'loved' and lab != 'recycled' and lab != label:
            images = info['labels'][lab]
            for img in images:
                if img == name:
                    info['labels'][lab].remove(name)
    return


# 上传图片，默认为no label
def uploadImage(name, label=None):
    if label is None:
        label = 'no label'
    info = loadInfo()
    info['labels'][label].append(name)
    updateInfo(info)
    return


# 设置名字
def selectName():
    name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return name


# 如果没给time2，就是固定时间点筛选；如果给了time2，则是时间段筛选，且time1<time2
# 要求格式为%Y-%m-%d %H:%M:%S
def selectByTime(time1, time2=None):
    info = loadInfo()
    labels = list(info['labels'])
    imgs = []
    if time2:
        time1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
        time2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
        for label in labels:
            if label != 'loved' and label != 'recycled':
                images = info['labels'][label]
                for img in images:
                    img_obj = datetime.strptime(img, "%Y-%m-%d %H:%M:%S")
                    if time1 <= img_obj <= time2:
                        imgs.append(img)

    else:
        for label in labels:
            if label != 'loved' and label != 'recycled':
                images = info['labels'][label]
                for img in images:
                    img_obj = datetime.strptime(img, "%Y-%m-%d %H:%M:%S")
                    if img_obj.strftime("%Y-%m-%d") == time1:
                        imgs.append(img)
    imgs = sorted(imgs, key=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), reverse=True)
    writeOut(imgs)
    return



