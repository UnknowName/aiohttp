from threading import Thread
from subprocess import run, STDOUT, PIPE
from asyncio.coroutines import iscoroutinefunction


class _BaseCommand(Thread):
    # 这个类属性后面需要被继承的各类重写
    _command_template = "{}{}"

    def __init__(self, cmd: str, host: str, service: str, notify_func, users: list):
        Thread.__init__(self)

        self._cmd = cmd
        self.host = host
        self.service = service
        self._func = notify_func
        self._users = users

    def _create_task_yml(self) -> str:
        task_str = self._command_template.format(host=self.host, service=self.service)
        yaml_name = "{}_{}.yml".format(self.host, self.service)
        with open(yaml_name, "w") as f:
            f.write(task_str)
            return yaml_name

    def _get_cmd(self) -> str:
        if self.host and self.service:
            play_book = self._create_task_yml()
            return "ansible-playbook {}".format(play_book)
        return self._cmd

    @staticmethod
    def execute_cmd(cmd: str) -> str:
        stdout = run(cmd, shell=True, stdout=PIPE, stderr=STDOUT).stdout
        try:
            return stdout.decode("utf8")
        except UnicodeDecodeError:
            return stdout.decode("gbk")

    def run(self) -> None:
        cmd = self._get_cmd()
        cmd_output = self.execute_cmd(cmd)
        if iscoroutinefunction(self._func):
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._func(self._users, cmd_output))
            loop.close()
        else:
            self._func(self._users, cmd_output)


class _RecycleCommandThread(_BaseCommand):
    _command_template = r"""
    ---
    - hosts:
      - {host}
      gather_facts: False
      tasks:
      - name: Restart {service} IIS WebApplicationPool
        win_iis_webapppool:
          name: {service}.sissyun.com.cn
          state: restarted
    """


class _ServicesCommandThread(_BaseCommand):
    _command_template = r"""
    ---
    - host:
      - {host}
      gather_facts: False
      tasks:
      - name: Restart docker-compose service {service}
        shell: cd /data/{service} && docker-compose restart
    """


class _SystemCommandThread(_BaseCommand):
    """Execute System Command"""
    pass


class _RunWindowsProcessThread(_BaseCommand):
    """Run a windows .exe file"""
    _command_template = r"""
    ---
    - host: 
      - {host}
      gather_facts: False
      tasks:
      - name: Stop old process
        win_command: powershell.exe  Stop-Process -Name SiXunMall.RabbitMq.WinServer.exe
          
      - name: Run new process
        win_command: SiXunMall.RabbitMq.WinServer.exe
        args:
          chdir: E:\Program Files\微商店3.0队列\
    """


class ParseCommand(object):
    def __init__(self, wechat_msg: str, notify_func, notify_users: list):
        try:
            cmd, host, service = wechat_msg.split(" ")
            # 这个_cmd是用来判断命令的类型
            self.cmd = cmd
            self.service = service
            self.host = host
        except ValueError:
            self.cmd = wechat_msg
        self.notify_func = notify_func
        self.notify_users = notify_users

    def get_cmd_thread(self):
        if self.cmd == 'recycle':
            return _RecycleCommandThread(self.cmd, self.host, self.service, self.notify_func, self.notify_users)
        elif self.cmd == 'restart':
            return _ServicesCommandThread(self.cmd, self.host, self.service, self.notify_func, self.notify_users)
        elif self.cmd == 'run':
            return _RunWindowsProcessThread(self.cmd, self.host, self.service, self.notify_func, self.notify_users)
        else:
            print("默认执行系统的命令")
            return _SystemCommandThread(self.cmd, "", "", self.notify_func, self.notify_users)


if __name__ == '__main__':
    async def func(x, y):
        print(x, y)
    cmd_thread = ParseCommand("restart rabbit1 rabbitmq-prod", func, ["tkggvfhpce2"]).get_cmd_thread()
    cmd_thread.start()