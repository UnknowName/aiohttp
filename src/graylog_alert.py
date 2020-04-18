from datetime import datetime, timedelta

from aiohttp import web

import setting
from utils.dding import AsyncDDing

DDING_NOTIFY = {
    'dev': AsyncDDing(setting.DDING_ROBOT_TOKEN_DEV),
    'o2o': AsyncDDing(setting.DDING_ROBOT_TOKEN_O2O),
    'pay': AsyncDDing(setting.DDING_ROBOT_TOKEN_PAY)
}

DEFAULT_ROBOT = AsyncDDing(setting.DDING_ROBOT_TOKEN_DEV)


async def graylog(request):
    if request.method == "POST":
        msg = await request.json()
        # Graylog的Alert中添加自定义的KEY，
        event_key = msg.get("event", {}).get("key", "")
        event_msg = msg.get("event", {}).get("message", "")
        dding_robot = DDING_NOTIFY.get(event_key, DEFAULT_ROBOT)
        # 3.0 老版本字段
        result_msg = msg.get("check_result")
        if not result_msg:
            # 3.1/3.2 新版本
            result_msg = msg.get("backlog")
        if isinstance(result_msg, list):
            err_logs = result_msg
        else:
            err_logs = result_msg.get("matching_messages")
        message = "日志系统检测到异常: {}\n以下是最近二条的异常详情：\n".format(event_msg)
        for err_log in err_logs:
            err_time = utc2sh(err_log.get("timestamp"))
            err_msg = err_log.get("message")
            err_from = err_log.get("source")
            log_item = "Time: {0}\nErrorLog: {1}\nFrom: {2}\n".format(err_time, err_msg, err_from)
            message += log_item + ('-' * 20) + "\n"
        await dding_robot.send_msg(message)
    return web.Response(status=200, text=request.method)


def utc2sh(time_str: str) -> str:
    """UTC time Change to Asia/Shanghai time"""
    utc_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    add_hour = timedelta(hours=8)
    sh_time = utc_time + add_hour
    return sh_time.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    print(utc2sh("2019-05-16T02:05:13.623Z"))
