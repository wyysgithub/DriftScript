# DriftScript
用python写的全民漂移游戏脚本

## 游戏逻辑
1. 在抽奖页面点击+5，会开始播放15秒广告；
2. 广告播放完毕，需要点击关闭广告才能回抽奖页面，并增加抽奖次数5次；
3. 点击开始，转盘会转5~7秒，然后页面显示抽奖结果；
4. 抽奖结果会有两种情况，一是可以直接点击领取的，二是需要再次观看广告再领取的，也可以点击关闭重新抽奖；

## 效果预想
1. 抽奖次数不够自动播放广告增加抽奖次数；
2. 自动点击抽奖，并领取奖励；
3. 遇到要观看广告才能领取的奖励，点击关掉，重新抽（这里主要是为了省时）

## 代码实现
用到的库：
```Python
import os
from PIL import Image
from PIL import ImageFile
import imagehash
import threading
import time
```
#### 1. 各种模拟点击用adb指令实现； `os.system('adb shell input tap 641 61')`  
其中，641 61 是点击位置的xy坐标。怎么查看点击位置坐标可以参考我的这篇博客：
https://blog.csdn.net/qq_23521659/article/details/95475787
#### 2. 图片裁切与识别；通过图片hash值进行比较：

首先截图上传：
```Python
    os.system('adb shell screencap -p /sdcard/nowPage.png')
    os.system('adb pull /sdcard/nowPage.png .')
```
然后裁切：
```Python
    img = Image.open("nowPage.png")
    cropped = img.crop((300, 690, 420, 810))  # (left, upper, right, lower)
    cropped.save("nowButton.png")
```  
识别函数如下：

```Python
def get_hash_dict(dir):
    hash_dict = {}
    image_quantity = 0
    for _, _, files in os.walk(dir):
        for i, fileName in enumerate(files):
            with open(dir + fileName, 'rb') as fp:
                hash_dict[dir + fileName] = imagehash.average_hash(Image.open(fp))
                image_quantity += 1
    return hash_dict, image_quantity
    
def compare_image_with_hash(image_file_name_1, image_file_name_2, max_dif=0):
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    hash_1 = None
    hash_2 = None
    with open(image_file_name_1, 'rb') as fp:
        hash_1 = imagehash.average_hash(Image.open(fp))
    with open(image_file_name_2, 'rb') as fp:
        hash_2 = imagehash.average_hash(Image.open(fp))
    dif = hash_1 - hash_2
    if dif < 0:
        dif = -dif
    if dif <= max_dif:
        return True
    else:
        return False
        
def compare_image_dir_with_hash(dir_1, dir_2, max_dif=0):
  
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    hash_dict_1, image_quantity_1 = get_hash_dict(dir_1)
    hash_dict_2, image_quantity_2 = get_hash_dict(dir_2)

    if image_quantity_1 > image_quantity_2:
        tmp = image_quantity_1
        image_quantity_1 = image_quantity_2
        image_quantity_2 = tmp

        tmp = hash_dict_1
        hash_dict_1 = hash_dict_2
        hash_dict_2 = tmp

    result_dict = {}

    for k in hash_dict_1.keys():
        result_dict[k] = None

    for dif_i in range(0, max_dif + 1):
        have_none = False

        for k_1 in result_dict.keys():
            if result_dict.get(k_1) is None:
                have_none = True

        if not have_none:
            return result_dict

        for k_1, v_1 in hash_dict_1.items():
            for k_2, v_2 in hash_dict_2.items():
                sub = (v_1 - v_2)
                if sub < 0:
                    sub = -sub
                if sub == dif_i and result_dict.get(k_1) is None:
                    result_dict[k_1] = k_2
                    break
    return result_dict  
```
#### 3. 延时使用`time.sleep(7)`；
#### 4. 循环实现：  

```Python
# 总循环函数
def run():

    ...

    global timer
    timer = threading.Timer(0.1, run)
    timer.start()


# 这里进行循环
try:
    timer = threading.Timer(0, run)
    timer.start()
except(KeyboardInterrupt, SystemExit):
    print(KeyboardInterrupt, SystemExit)
```
