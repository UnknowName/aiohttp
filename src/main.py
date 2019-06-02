import time
import urllib.parse
from subprocess import run, STDOUT, PIPE

from aiohttp import web

import setting
from utils.log import Log
from middleware import add_notify
from graylog_alert import graylog
from utils.wechat import WechatCrypto, WechatXML


async def wechat(request):
    wx_notify = request.get("notify")
    args = request.query
    wechat_sign = args.get("msg_signature")
    msg_timestamp = args.get("timestamp")
    msg_nonce = args.get("nonce")
    wxcrypt = WechatCrypto(setting.WECHAT_CORPID, 
                           setting.WECHAT_TOKEN, setting.WECHAT_AESKEY)
    if request.method == "GET":
        echostr = urllib.parse.unquote(args.get('echostr', ""))
        msg_sign = wxcrypt.get_signature(msg_timestamp,
                                         msg_nonce,
                                         echostr)
        if msg_sign != wechat_sign:
            log.warning("消息签名不一致")
            return web.Response(status=405, text="novalied signature")
        echostr = wxcrypt.decry_msg(echostr)
        return web.Response(status=200, text=echostr)
    elif request.method == "POST":
        if request.can_read_body:
            data = b''
            while True:
                byte = await request.content.read(1024)
                if not byte:
                    break
                data += byte
            # 微信的原始完整加密XML数据，包含agentid等信息
            xml_data = str(data, encoding="utf8")
            # 只过滤加密的用户消息
            encry_msg = await WechatXML.parse_data(xml_data, "Encrypt")
            if wechat_sign != wxcrypt.get_signature(msg_timestamp,
                                                    msg_nonce, 
                                                    encry_msg):
                log.warning("消息签名不一致")
                return web.Response(status=403, text="deny")
            plain_msg = wxcrypt.decry_msg(encry_msg)
            # 解密后的内容，又是XML数据, 文本消息在Content里面
            msg = await WechatXML.parse_data(plain_msg, "Content")
            user = await WechatXML.parse_data(plain_msg, "FromUserName")
            if user in setting.WECHAT_ALLOW_USERS:
                log.info("user {user} run {cmd}".format(user=user, cmd=msg))
                cmd_output = await run_cmd(msg)
                await wx_notify([user], cmd_output)
            else:
                log.info("User {user} not privilege".format(user=user))
                await wx_notify([user], "Permission Deny")
        return web.Response(status=200, text="ok")
    else:
        log.info("Not Support method {}".format(args.method))
        return web.Response(status=405, text="Not allowed method")


async def run_cmd(cmd: str) -> str:
    stdout = run(cmd, shell=True, stdout=PIPE, stderr=STDOUT).stdout
    return stdout.decode("utf8")


if __name__ == "__main__":
    log = Log('__name__').get_loger()
    log.info("Start at {}".format(time.asctime()))
    app = web.Application(middlewares=[add_notify])
    app.add_routes(
        [
            web.get('/wechat', wechat),
            web.post('/wechat', wechat),
            # Graylog Alert
            web.get('/graylog', graylog),
            web.post('/graylog', graylog)
        ]
    )
    web.run_app(app, port=8080)
