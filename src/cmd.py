#!/usr/bin/env python3

from subprocess import run, STDOUT, PIPE


RISK_COMMANDS = ["rm", "reboot", "shutdown", "exit"]

def check_cmd(command: str) -> bool:
    pass
     

async def run_cmd(command: str) -> str:
    std = run(command, shell=True, stdout=PIPE, stderr=STDOUT).stdout
    return std.decode("utf8")
