import os
PLATFORM = 'Android'
DEVICE_NAME = 'SM_N9500'
APP = os.path.abspath('.') + '/com.tencent.mm_6.6.2.apk'
APP_PACKAGE = 'com.tencent.mm'
APP_ACTIVITY = 'com.tencent.mm.ui.LauncherUI'
NEWCOMMANDTIMEOUT = "100"
DRIVER_SERVER = 'http://localhost:4723/wd/hub'
TIMEOUT = 500
USERNAME = ''
PASSWORD = ''
FLICK_START_X = 300
FLICK_START_Y = 300
FLICK_DISTANCE = 700
# 数据库连接设置
MONGO_URL = 'localhost'
MONGO_DB = 'FriendCircle'
MONGO_COLLECTION = 'FriendCircle'