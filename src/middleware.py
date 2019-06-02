from aiohttp import web

import setting
from utils.wechat import AsyncWechat

wx = AsyncWechat(setting.WECHAT_CORPID, setting.WECHAT_SECRET)


@web.middleware
async def add_notify(request, handler):
    request['notify'] = wx.send_msg
    response = await handler(request)
    return response
