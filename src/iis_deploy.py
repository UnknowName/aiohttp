import os
import time
from queue import Queue, Empty

import aiohttp_jinja2
from aiohttp import web

LOG_QUEUE = Queue()
# LOG_QUEUE.put("test")
DOMAINS = {
    "www.a.com": [
        "128.0.255.27",
        "128.0.255.28"
    ],
    "www.b.com": [
        "128.0.255.27",
        "128.0.255.28"
    ]
}


@aiohttp_jinja2.template("iis_deploy.html")
async def index(request):
    if request.method == "GET":
        return {"domains": DOMAINS}


@aiohttp_jinja2.template("deploy_log.html")
async def deployment(request):
    global LOG_QUEUE
    if not LOG_QUEUE.empty():
        return {"message": "部署失败，因为当前有项目正在执行部署，可以稍后再试，上次部署日志:"}
    if request.method == 'POST':
        data = await request.multipart()
        field = await data.next()
        # 处理FROM表单不同列的数据
        domain = ""
        servers = list()
        while field:
            name = field.name
            if name != "filename":
                value = await field.read(decode=True)
                if name == "domain":
                    domain = value.decode("utf8")
                else:
                    servers.append(value.decode("utf8"))
            else:
                packet_folder = os.path.join(os.getcwd(), "packets")
                if not os.path.exists(packet_folder):
                    os.mkdir(packet_folder)
                filename = field.filename
                LOG_QUEUE.put("开始处理上传的文件")
                # 防止OOM，通过流方式将用户上传的文件写入本地目录
                size = 0
                with open(os.path.join(packet_folder, filename), 'wb') as f:
                    while True:
                        # 8192 bytes by default.
                        chunk = await field.read_chunk()
                        if not chunk:
                            break
                        size += len(chunk)
                        f.write(chunk)
            # 读取下一个field，直到为None
            field = await data.next()
        LOG_QUEUE.put(f"部署的站点: {domain}")
        LOG_QUEUE.put(f"部署的服务器: {servers}")
        LOG_QUEUE.put("上传文件处理完毕，开始生成部署工作流程")
        print(domain, servers)
        time.sleep(2)
        # 消息结束标志位
        LOG_QUEUE.put("EOF")
    return {"message": "部署动作已放入后台执行，以下是部署日志："}


async def deploy_log(request):
    global LOG_QUEUE
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    try:
        log = LOG_QUEUE.get(timeout=6)
    except Empty:
        print("Queue is empty yet")
        return ws
    while log != "EOF":
        time.sleep(1.5)
        await ws.send_str(log)
        log = LOG_QUEUE.get()
    return ws
