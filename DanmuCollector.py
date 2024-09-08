import json
import sys
import os

script_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(script_path)
sys.path.append("")
sys.path.append(script_path)
print(sys.path)

from DBUtils import DBUtils
from bilibili_api import live, sync
from bilibili_api import settings
from bilibili_api import Credential
from bilibili_api import login, user, video


# zhuangjiyuan 1361615
# huolongguo 23585383
# xiaoguazi 13217800
class danmakuCollector:
    room_id = ""
    def runservice(self, roomid):
        credential = Credential(sessdata="9319153b%2C1740667346%2C46ffe%2A81CjD9jDdb06fsEBfcaqHcQREHDguBsv3aEpuc-rfr1-Gw4dXbSf_G4op8C27Zdu4cF8cSVlBxeDlRZldEaEppYVFyWjlyYVdBVnZuWVh4R1VQeDFzRFRLdDQ0NGo1d1NMbVZzOGNwLURLT20wLU0yWVBaU0FXSXQ1c2txblV5LUNTMlNNY29uT3hnIIEC", bili_jct="361044bfc80da064e2b981874f3c032e", buvid3="9986B0C8-DD05-F7DD-1E8D-249C74B57E5451847-022102910-ywPg47KRff27knayyWf7Pg%3D%3D", dedeuserid="544384417", ac_time_value="97868f9fd0cc802eafb5b84455cfa881")
        settings.timeout = 10
        settings.http_client = settings.HTTPClient.HTTPX # settings.HTTPClient.AIOHTTP #
        # settings.proxy = "http://127.0.0.1:2802"
        room = live.LiveDanmaku(roomid, credential=credential)
        self.room_id = roomid

        @room.on('DANMU_MSG')
        async def on_danmaku(event):
            try:
                extra = event["data"]["info"][0][15]["extra"]
                # print(f'extra: {extra}')
                extranode = json.loads(extra)
                content = extranode['content']
                print(content)
                try:
                    db = DBUtils()
                    sql1 = f'SELECT endpoint, platform, roomid, productid, nodeid FROM immortal.playstream where platform="bilibili" and roomid="{self.room_id}" order by `create` desc limit 1;'
                    resulttable = db.doQuery(sql1)
                    endpoint = resulttable[0][0]
                    platform = resulttable[0][1]
                    roomid = resulttable[0][2]
                    productid = resulttable[0][3]
                    nodeid = resulttable[0][4]
                    sql = f"insert into immortal.danmustream (`endpointid`,`Platform`, `roomid`, `productid`, `nodeid`, `Content`) VALUES ('{endpoint}', '{platform}', '{roomid}', '{productid}', '{nodeid}', '{content}')"
                    db.doCommand(sql)
                except Exception as exe:
                    print(exe)
                    raise
            except Exception as ex:
                pass

        @room.on('SEND_GIFT')
        async def on_gift(event):
            print(event)

        def loginfunc():
            print("请登录：")
            credential = login.login_with_qrcode_term()  # 在终端扫描二维码登录
            # credential = login.login_with_qrcode() # 使用窗口显示二维码登录
            try:
                credential.raise_for_no_bili_jct()  # 判断是否成功
                credential.raise_for_no_sessdata()  # 判断是否成功
            except:
                print("登陆失败。。。")
                exit()
            print("欢迎，", sync(user.get_self_info(credential))['name'], "!")

        def viewVideo():
            async def main():
                # 实例化 Credential 类
                # credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)
                # 实例化 Video 类
                v = video.Video(bvid="BV1XL411A7nv", credential=credential)
                # 获取视频信息
                info = await v.get_info()
                # 打印视频信息
                print(info)
                # 给视频点赞
                # await v.like(True)
            sync(main())

        return room

if __name__ == '__main__':
    roomid = sys.argv[1]
    service = danmakuCollector()
    room = service.runservice(roomid)
    sync(room.connect())
