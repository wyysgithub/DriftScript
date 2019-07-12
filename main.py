import os
from PIL import Image
from PIL import ImageFile
import imagehash
import threading
import time


# 初始化图片

# os.system('adb shell screencap -p /sdcard/initPage.png')
# os.system('adb pull /sdcard/initPage.png .')
# img = Image.open("initPage.png")
# cropped = img.crop((300, 690, 420, 810))  # (left, upper, right, lower)
# cropped.save("initButton.png")


def getScreenWH():
    # 获取手机分辨率
    screen_size = os.popen('adb shell wm size').read()
    if not screen_size:
        print('adb指令无效！')
        print('先尝试使用adb devices指令，确认能查找到设备！')
    if screen_size != '720x1280':
        print('暂时只支持720x1280的手机！')
    return False

def touch():
    # 关闭广告
    os.system('adb shell input tap 641 61')

    # 打开转盘
    os.system('adb shell input tap 53 322')

    # 次数+5
    os.system('adb shell input tap 543 791')


# 截图函数
def screenCap():
    os.system('adb shell screencap -p /sdcard/nowPage.png')
    os.system('adb pull /sdcard/nowPage.png .')
    img = Image.open("nowPage.png")
    cropped = img.crop((300, 690, 420, 810))  # (left, upper, right, lower)
    cropped.save("nowButton.png")


# 通过图片hash值进行比较
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
    """
    max_dif: 允许最大hash差值, 越小越精确,最小为0
    推荐使用
    """
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
    """
    max_dif: 允许最大hash差值, 越小越精确,最小为0
    用于比较两个文件夹内的图片
    """
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


# 点击抽奖一次
def draw():
    # 点击抽奖
    os.system('adb shell input tap 368 910')
    print('已点击抽奖……等待7秒……')
    # 等待七秒
    time.sleep(7)
    # 判断是否可以直接领取
    screenCap()
    print('已截图，正在判断是否可以直接领取……')
    if (compare_image_with_hash('initButton.png', 'nowButton.png', 6)):
        # 可以直接确定 领取
        print('可以直接领取，已点击确定')
        os.system('adb shell input tap 365 745')

    else:
        # 不看广告翻倍，点击叉掉
        print('不能直接领取，点击叉掉')
        os.system('adb shell input tap 659 327')


def checkPoster():
    os.system('adb shell screencap -p /sdcard/poster.png')
    os.system('adb pull /sdcard/poster.png .')
    img = Image.open("poster.png")
    cropped = img.crop((180, 800, 520, 849))  # (left, upper, right, lower)
    cropped.save("nowPoster.png")
    print('已截图，正在判断广告是否放完……')
    if (compare_image_with_hash('initPoster.png', 'nowPoster.png', 6)):
        print('广告已经放完，点击关闭')
        # 关闭广告
        os.system('adb shell input tap 641 61')
    else:
        print('广告还未放完，过3秒后关闭')
        # 等3秒再关
        time.sleep(3)
        os.system('adb shell input tap 641 61')

# 看广告获取次数
def getCount():
    # 看广告加次数
    # 次数+5
    print('开始观看广告，获取转盘次数……')
    os.system('adb shell input tap 543 791')
    # 等20秒
    time.sleep(20)

    # 检测关闭广告是否播放完毕
    checkPoster()

# 总循环函数
def run():

    # 看广告加次数
    getCount()

    print('等待5秒开始抽奖……')
    time.sleep(5)

    # 开始抽奖五次
    draw()
    draw()
    draw()
    draw()
    draw()
    draw()

    global timer
    timer = threading.Timer(0.1, run)
    timer.start()


# 这里进行循环
try:
    timer = threading.Timer(0, run)
    timer.start()
except(KeyboardInterrupt, SystemExit):
    print(KeyboardInterrupt, SystemExit)
# screenCap()

# checkPoster()
