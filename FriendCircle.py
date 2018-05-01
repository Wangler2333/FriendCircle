import re
import time
from congif import *
import pymongo
from appium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FriendCircle(object):
    def __init__(self):
        """"
        初始化信息：
        初始化手机信息，app信息
        初始化驱动配置，延时等待，MongoDB连接信息等
        """
        self.desired_caps = {
            "platformName": PLATFORM,
            "deviceName": DEVICE_NAME,
            "app":APP,
            "appPackage": APP_PACKAGE,
            "appActivity": APP_ACTIVITY,
            'newCommandTimeout': NEWCOMMANDTIMEOUT,
            # "noReset":True
        }
        self.driver = webdriver.Remote(DRIVER_SERVER, self.desired_caps)
        self.wait = WebDriverWait(self.driver, 300)
        self.client = pymongo.MongoClient(MONGO_URL)
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]

    def login(self):
        """
        完成微信的登陆操作包括：
        点击登陆按钮，手机号输入，输入密码提交等
        """
        # 点击登录按钮
        login = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/d2z')))
        login.click()
        # 手机号输入
        phone_number = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/ht')))
        phone_number.set_text('17681714536')
        # 点击下一步
        next = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/ak_')))
        next.click()
        # 输入密码
        # 由于在这一页面，密码输入框的定位中ID定位并不唯一，和手机号码显示框重复了，故此选用XPATH定位，并选择[1],以此区分
        password = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@resource-id="com.tencent.mm:id/ht"][1]')))
        password.set_text('Wx425.Dq.369')
        # 提交登录
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'com.tencent.mm:id/ak_')))
        submit.click()
        # 选择通讯录匹配并进入微信
        prompt = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/alk')))
        # 选择否并点击
        prompt.click()

    def discovery(self):
        """
        完成选项卡的切换，点击进入朋友圈
        """
        # 点击发现选项卡，与登录密码输入类似，底栏四个选项卡用ID定位并不唯一，直接用text定位，由于进入此函数前已经sleep(60)，直接点击即可
        tab = self.driver.find_element_by_android_uiautomator("text(\"发现\")")
        tab.click()
        # 点击进入朋友圈
        # friendcircle = self.wait.until(
        #     EC.presence_of_element_located((By.XPATH, '//*[resource-id="com.tencent.mm:id/a9d"][1]')))
        # 因发现一栏的功能可以开启关闭，用其他方法定位后加上筛选可能会出错故直接用text
        friendcircle = self.driver.find_element_by_android_uiautomator("text(\"朋友圈\")")
        friendcircle.click()

    def slide(self):
        """
        滑动朋友圈
        """
        # 一直向上滑动朋友圈
        while True:
            self.driver.swipe(500, 1800, 500, 1000)
            items = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@resource-id="com.tencent.mm:id/dei"]//android.widget.FrameLayout')))
            for item in items:
                try:
                    # 获取昵称，用find_element_by_id定位后用get_get_attribute('text')获取文本信息
                    nick = item.find_element_by_id("com.tencent.mm:id/apr").get_attribute("text")
                    # 获取正文
                    content = item.find_element_by_id("com.tencent.mm:id/ql").get_attribute("text")
                    # 获取日期
                    date = item.find_element_by_id("com.tencent.mm:id/dfp").get_attribute("text")
                    edit_time = self.date(date)
                    # 获取评论
                    if item.find_element_by_id("com.tencent.mm:id/dbk").get_attribute("text"):
                        comment = item.find_element_by_id("com.tencent.mm:id/dbk").get_attribute("text")
                    else:
                        comment = ""
                    data = {
                        "nick": nick,
                        "content": content,
                        "datetime": edit_time,
                        "comment": comment
                    }
                    self.save_to_mongo(data)
                except NoSuchElementException:
                    pass

    def date(self, date):
        """
        对动态发送时间进行处理
        :param date: 处理前发动态的时间
        :return: 处理后的标准时间
        """
        if re.match("\d+分钟前", date):
            mintune = re.match("(\d+)", date).group(1)
            date = time.strftime("%Y-%m-%d", time.localtime(time.time()) - float(mintune) * 60)
        if re.match("\d+小时前", date):
            hour = re.match("(\d+)", date).group(1)
            date = time.strftime("%Y-%m-%d", time.localtime(time.time()) - float(hour) * 60 * 60)
        if re.match("\d+天前", date):
            day = re.match("(\d+)", date).group(1)
            date = time.strftime("%H-%m-%d", time.localtime(time.time()) - float(day) * 24 * 60 * 60)
        if re.match("昨天", date):
            date = time.strftime("%H-%m-%d", time.localtime(time.time()) - 24 * 60 * 60)
        return date

    def save_to_mongo(self, data):
        if data:
            self.collection.update({"nick": data.get("nick"), "content": data.get("content")}, {'$set': data}, True)
            print("save to mongodb sucess", data)

    def main(self):
        # if not self.desired_caps.get("noReset"):
        self.login()
        # 微信初次登陆载入数据等待
        time.sleep(60)
        # 进入朋友圈
        self.discovery()
        # 滑动并爬取数据
        self.slide()


if __name__ == '__main__':
    friendcircle = FriendCircle()
    friendcircle.main()
