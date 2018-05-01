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
            "platformName": "Android",
            "deviceName": "SM_N9500",
            "appPackage": "com.tencent.mm",
            "appActivity": ".ui.LauncherUI"
        }
        self.driver = webdriver.Remote('http://loacalhost:4723/wd/hub', self.desired_caps)
        self.wait = WebDriverWait(self.driver, 500)
        self.client = pymongo.MongoClient('localhost')
        self.db = self.client['FriendCircle']
        self.collection = self.db['FriendCircle']

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
        phone_number.set_text('188888888')
        # 点击下一步
        next = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/ak_')))
        next.click()
        # 输入密码
        # 由于在这一页面，密码输入框的定位中ID定位并不唯一，和手机号码显示框重复了，故此选用XPATH定位，并选择[1],以此区分
        password = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@resource-id="com.tencent.mm:id/ht"][1]')))
        password.set_text('password')
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
        # 点击发现选项卡，与登录密码输入类似，底栏四个选项卡用ID定位并不唯一，故用XPATH并选择[3]
        tab = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@resource-id="com.tencent.mm:id/c_z"][3]')))
        tab.click()
        # 点击进入朋友圈
        friendcircle = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[resource-id="android:id/title][1]')))
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
                # 获取图片
                pictures = item.find_element_by_accessibility_id("图片")
                all_pic = []
                for picture in pictures:
                    all_pic.append(picture.get_attribute('text'))
                # 获取日期
                date = item.find_element_by_id("com.tencent.mm:id/dfp").get_attribute("text")
            except NoSuchElementException:
                pass





