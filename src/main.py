#!/bin/env python3
import time
import urllib.parse

from aiohttp import web

import setting
from log import Log
from cmd import run_cmd
from wechat_utils import WechatCrypto, WechatXML, AsyncWechat


log = Log('__name__').get_loger()
log.info("Start at {}".format(time.asctime()))

async def hello(request):
    log.info(request.remote)
    start = time.time()
    args = request.query
    wechat_sign = args.get("msg_signature")
    msg_timestamp = args.get("timestamp")
    msg_nonce = args.get("nonce")
    wxclient = AsyncWechat(setting.WECHAT_CORPID, setting.WECHAT_SECRET)
    wxcrypt = WechatCrypto(setting.WECHAT_CORPID, 
                           setting.WECHAT_TOKEN, setting.WECHAT_AESKEY)
    if request.method == "GET":
        echostr = urllib.parse.unquote(args.get('echostr'))
        msg_sign = wxcrypt.get_signature(msg_timestamp,
                                         msg_nonce,
                                         echostr)
        if msg_sign != wechat_sign:
            log.warn("消息签名不一致")
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
                log.warn("消息签名不一致")
                return web.Response(status="403", text="deny")
            plain_msg = wxcrypt.decry_msg(encry_msg)
            # 解密后的内容，又是XML数据, 文本消息在Content里面
            msg = await WechatXML.parse_data(plain_msg, "Content")
            user = await WechatXML.parse_data(plain_msg, "FromUserName")
            if user in setting.ALLOW_USERS:
                log.info("user " + user + " run " + msg)
                cmd_output = await run_cmd(msg)
                await wxclient.send_msg([user], cmd_output) 
            else:
                log.info("User " + user + "not privilege")
                await wxclient.send_msg([user], "Permistion Deny")
        return web.Response(status="200", text="ok")
    else:
        log.info("Not Support method {}".format(args.method))
        return web.Response(status="405", text="Not allowed method")


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(
        [
            web.get('/wechat', hello),
            web.post('/wechat', hello),
        ]
    )
    web.run_app(app, port=8082)
