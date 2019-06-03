from datetime import datetime, timedelta

from aiohttp import web

import setting


async def graylog(request):
    wx_notify = request.get("notify")
    if request.method == "POST":
        msg = await request.json()
        result_msg = msg.get("check_result")
        err_logs = result_msg.get("matching_messages")
        message = "日志系统检测到异常，以下是最近的异常详情：\n"
        for err_log in err_logs:
            err_time = utc2sh(err_log.get("timestamp"))
            err_msg = err_log.get("message")
            if not hasattr(err_log, "Thread"):
                err_upstrem = err_log.get("upstream_addr")
                log_item = "Time: {0}\nErrorLog: {1}\nFROM: {2}\n".format(err_time, err_msg, err_upstream)
            else:
                err_from = err_log.get("source")
                log_item = "Time: {0}\nErrorLog: {1}\nFROM: {2}\n".format(err_time, err_msg, err_from)
            message += log_item + ('-' * 20) + "\n"
        await wx_notify(setting.WECHAT_NOTIFY_USERS, message)
    return web.Response(status=200, text=request.method)


def utc2sh(time_str: str) -> str:
    """UTC time Change to Asia/Shanghai time"""
    utc_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    add_hour = timedelta(hours=8)
    sh_time = utc_time + add_hour
    return sh_time.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    print(utc2sh("2019-05-16T02:05:13.623Z"))
