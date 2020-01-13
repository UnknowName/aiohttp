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


class _DockerCommandThread(_BaseCommand):
    _command_template = ""

    def _get_cmd(self) -> str:
        if self._cmd == "log":
            cmd_str = "docker logs --tail 20 finance-{service_name}".format(service_name=self.service)
        elif self._cmd == "restart":
            cmd_str = "docker restart finance-{service_name}".format(service_name=self.service)
        else:
            cmd_str = ""
        return "ssh root@{host} '{command}'".format(host=self.host, command=cmd_str)


class _RecycleCommandThread(_BaseCommand):
    _command_template = r"""
    - hosts:
      - "{host}"
      gather_facts: False
      tasks:
      - name: Restart {service} IIS WebApplicationPool
        win_iis_webapppool:
          name: {service}.sissyun.com.cn
          state: restarted
    """


class _ServicesCommandThread(_BaseCommand):
    _command_template = r"""
    - hosts:
      - "{host}"
      gather_facts: False
      tasks:
      - name: Restart docker-compose service {service}
        shell: cd /data/{service} && docker-compose restart
    """


class _RestartSiteCommandThread(_BaseCommand):
    _command_template = r"""
    - hosts:
      - "{host}"
      gather_facts: False
      tasks:
      - name: stop website {service}
        win_shell: Stop-Website -Name {service}
      - name: start website {service}
        win_shell: Start-Website -Name {service} 
    """


class _SystemCommandThread(_BaseCommand):
    """Execute System Command"""
    pass


class _RunWindowsProcessThread(_BaseCommand):
    """Run a windows .exe file"""
    _command_template = r"""
    - hosts: 
      - "{host}"
      gather_facts: False
      tasks:
      - name: Stop old process
        win_shell: Stop-Process -Force -name "SiXunMall.RabbitMq.WinServer"
        ignore_errors: True
        
      - name: Sleep 5 seconds
        pause:
          seconds: 5
          
      - name: Run new process
        win_command: cmd.exe /c START SiXunMall.RabbitMq.WinServer.exe&
        args:
          chdir: E:\Program Files\微商店3.0队列\
        async: 10
        ignore_errors: True
    """


class _ClusterCommand(_BaseCommand):
    _command_template = r"""
        - hosts:
          - "{host}"
          gather_facts: False
          serial: 1
          
          tasks:
          - name: Restart {host} Clusters
            # In Fact,service is action like up/down/restart
            shell: cd /data/{host} && docker-compose {service}
            async: 90
            poll: 45
        """


class ParseCommand(object):
    def __init__(self, wechat_msg: str, notify_func, notify_users: list):
        try:
            cmd, host, service = wechat_msg.split(" ")
            self.cmd = cmd
            # kubectl先特殊处理
            if cmd == "kubectl":
                self.cmd = wechat_msg
            self.service = service
            self.host = host
        except ValueError:
            self.cmd = wechat_msg
        self.notify_func = notify_func
        self.notify_users = notify_users

    def get_cmd_thread(self):
        if self.cmd == 'recycle':
            return _RecycleCommandThread(self.cmd, self.host, self.service, self.notify_func, self.notify_users)
        elif self.cmd == 'restart' or self.cmd == "log":
            # return _ServicesCommandThread(self.cmd, self.host, self.service, self.notify_func, self.notify_users)
            return _DockerCommandThread(self.cmd, self.host, self.service, self.notify_func, self.notify_users)
        elif self.cmd == 'run':
            return _RunWindowsProcessThread(self.cmd, self.host, self.service, self.notify_func, self.notify_users)
        elif self.cmd == 'cluster':
            # When cluster command start, the last args is the action
            # Like restart/up/down
            action = self.service
            return _ClusterCommand("", self.host, action, self.notify_func, self.notify_users)
        elif self.cmd == 'website':
            return _RestartSiteCommandThread(self.cmd, self.host, self.service, self.notify_func, self.notify_users)
        else:
            print("执行系统命令: {}".format(self.cmd))
            return _SystemCommandThread(self.cmd, "", "", self.notify_func, self.notify_users)


if __name__ == '__main__':
    async def func(x, y):
        print(x, y)
    cmd_thread = ParseCommand("website o2o10 shopapi", func, ["tkggvfhpce2"]).get_cmd_thread()
    cmd_thread.start()