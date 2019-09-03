import os
import time
import asyncio
from queue import Queue, Empty


import jinja2
import aiohttp_jinja2
from aiohttp import web

import setting


LOG_QUEUE = Queue()
BACKUP_FILENAME = "backup.ps1"
UPDATE_FILENAME = "update.ps1"
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
NGINXS = ["128.0.255.2", "128.0.255.3"]


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
                """
                packet_folder = os.path.join(os.getcwd(), "packets")
                if not os.path.exists(packet_folder):
                    os.mkdir(packet_folder)
                """
                filename = field.filename
                LOG_QUEUE.put("开始处理上传的文件")
                # 防止OOM，通过流方式将用户上传的文件写入本地目录
                size = 0
                # zip_file = os.path.join(p, filename)
                with open(filename, 'wb') as f:
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
        LOG_QUEUE.put("上传文件处理完毕，正在生成部署用到的相关文件")
        # 这里不判断要部署的机器，前端只允许一半一半地部署
        # 通过模板生成备份脚本
        backup_date = time.strftime('%Y%m%d_%H')
        await render(
            'backup.ps1.ja2', BACKUP_FILENAME,
            smb_username=setting.SMB_USERNAME,
            smb_password=setting.SMB_PASSWORD,
            domain=domain, servers=servers, date=backup_date,
        )
        LOG_QUEUE.put("备份脚本生成完成")
        await render('update.ps1.ja2', UPDATE_FILENAME, zip_file=filename, domain=domain)
        LOG_QUEUE.put("更新脚本生成完成")
        task_playbook = await render(
            'tasks.yaml.ja2', "task.yaml", update_file=filename,
            domain=domain, nginxs=NGINXS, servers=servers
        )
        LOG_QUEUE.put("部署playbook生成完成。开始执行相关tasks")
        await system_cmd("ansible-playbook", task_playbook)
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


async def render(template_name: str, filename: str,  **kwargs):
    env_yml = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), 'templates'))
    )
    template = env_yml.get_template(template_name)
    with open(filename, 'w') as f:
        f.write(template.render(kwargs))
        return filename


async def system_cmd(cmd: str, *args) -> None:
    global LOG_QUEUE
    process = await asyncio.subprocess.create_subprocess_exec(
        cmd,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    # wait subprocess execute over
    await process.wait()
    stdout, stderr = await process.communicate()
    output = stdout if stdout else stderr
    for line in output.decode("utf8").split("\n"):
        LOG_QUEUE.put(line)
