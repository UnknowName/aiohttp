import os

import aiohttp_jinja2
from aiohttp import web

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
async def deployment(request):
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
        print("用户文件流量处理完毕，开始准备生成执行AnsiblePlaybook")
        print(domain, servers)
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        return ws
    elif request.method == 'GET':
        return {"domains": DOMAINS}
    return web.Response(status=200, text="Ok")
