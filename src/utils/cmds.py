from threading import Thread
from subprocess import run, STDOUT, PIPE
from asyncio.coroutines import iscoroutinefunction


class BaseCommand(Thread):
    def __init__(self, cmd: str, notify_func, users: list):
        Thread.__init__(self)

        self._cmd = cmd
        self._func = notify_func
        self._users = users

    @staticmethod
    def execute_cmd(cmd: str) -> str:
        stdout = run(cmd, shell=True, stdout=PIPE, stderr=STDOUT).stdout
        try:
            return stdout.decode("utf8")
        except UnicodeDecodeError:
            return stdout.decode("gbk")

    def run(self) -> None:
        cmd_output = self.execute_cmd(self._cmd)
        if iscoroutinefunction(self._func):
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._func(self._users, cmd_output))
            loop.close()
        else:
            self._func(self._users, cmd_output)


class RecycleCommand(BaseCommand):
    _RECYCLE_TEMPLATE = """---
    - hosts:
      - {host}
      gather_facts: False
      tasks:
      - name: Restart {domain} IIS WebApplicationPool
        win_iis_webapppool:
          name: {domain}
          state: restarted
    """

    def _create_task_yaml(self, host: str, domain: str) -> str:
        task_str = self._RECYCLE_TEMPLATE.format(host=host, domain=domain)
        yaml_name = "{}_{}.yml".format(host, domain)
        with open(yaml_name, "w") as f:
            f.write(task_str)
            return yaml_name

    def convert_cmd(self, origin_cmd: str) -> str:
        if origin_cmd.startswith("recycle"):
            cmd, host, app = origin_cmd.split(" ")
            domain = '{}.sissyun.com.cn'.format(app)
            filename = self._create_task_yaml(host, domain)
            return "ansible-playbook {}".format(filename)
        return origin_cmd

    def run(self):
        ansible_cmd = self.convert_cmd(self._cmd)
        cmd_output = self.execute_cmd(ansible_cmd)
        if iscoroutinefunction(self._func):
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._func(self._users, cmd_output))
            loop.close()
        else:
            self._func(self._users, cmd_output)


class ServicesCommand(BaseCommand):
    _command_template = """---
    - host: {host}
      tasks:
      - name: Restart docker-compose service {service_name}
        shell: cd /data/${service_name}&&docker-compose restart
    """


class _SystemCommandThread(BaseCommand):
    """Execute System Command"""
    pass


class _RunWindowsProcess(BaseCommand):
    """Run a windows .exe file"""
    _template_fmt = r"""---
    - host: 
      - {host}
      tasks:
      - name: Stop old process
        win_command: powershell.exe Stop-Process -Name ApplicationName
          
      - name: Run new process
        win_command: application.exe 
        args:
          chdir: D:\iisroot\
    """


class ParseCommand(object):
    def __init__(self, wechat_msg: str, notify_func, notify_users: list):
        try:
            cmd, host, service = wechat_msg.split(" ")
            self.cmd = cmd
            self.host = host
            self.service = service
        except ValueError:
            self.cmd = wechat_msg
        self.notify_func = notify_func
        self.notify_users = notify_users

    def get_cmd_thread(self):
        if self.cmd == "recycle":
            print("执行回收IIS命令")
        elif self.cmd == "restart":
            print("执行服务相关命令")
        elif self.cmd == "run":
            print("执行启动Windows进程服务")
        else:
            print("默认执行系统的命令")
            return _SystemCommandThread(self.cmd, self.notify_func, self.notify_users)


if __name__ == '__main__':
    """"
    async def func(x, y):
        print(x, y)
    cmd_thread = RecycleCommand("recycle o2o10 shop", func, ["tkggvfhpce2"])
    cmd_thread.start()
    """
    origin = ParseCommand("service rabbitmq-prod")
    if origin:
        print(True)

