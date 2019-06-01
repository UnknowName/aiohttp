RECYCLE_TEMPLATE = """---
- hosts:
  - {host}
  tasks:
  - name: Restart {domain} IIS WebApplicationPool
    win_iis_webapppool:
      name: {domain}
      state: restart
"""


async def create_task_yaml(host: str, domain: str) -> str:
    task_str = RECYCLE_TEMPLATE.format(host=host, domain=domain)
    with open("task.yaml", "w") as f:
        f.write(task_str)
    return ""

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    task = loop.create_task(create_task_yaml("172.18.11.10", "www.domain.com"))
    loop.run_until_complete(task)
    loop.close()

