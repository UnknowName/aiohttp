RECYCLE_TEMPLATE = """---
- hosts:
  - {host}
  gather_facts: False
  tasks:
  - name: Restart {domain} IIS WebApplicationPool
    win_iis_webapppool:
      name: {domain}
      state: restart
"""


async def create_task_yaml(host: str, domain: str) -> bool:
    task_str = RECYCLE_TEMPLATE.format(host=host, domain=domain)
    filename = "{}_{}.yml".format(host, domain)
    with open(filename, "w") as f:
        f.write(task_str)
        return filename


async def convert_cmd(origin_cmd: str) -> str:
    """Convert customize cmd to system cmd"""
    if origin_cmd.startswith("recycle"):
        cmd, host, app = origin_cmd.split(" ")
        domain = '{}.sissyun.com.cn'.format(app)
        filename = await create_task_yaml(host, domain)
        return "ansible-playbook {} -vv".format(filename)
    return origin_cmd


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    # task = loop.create_task(create_task_yaml("172.18.11.10", "www.domain.com"))
    task = loop.create_task(convert_cmd("recycle o2o28 shop"))
    loop.run_until_complete(task)
    print(task.result())
    loop.close()
