import os

WECHAT_AESKEY = os.getenv("WECHAT_AESKEY", False)

WECHAT_CORPID = os.getenv("WECHAT_CORPID", False)

WECHAT_SECRET = os.getenv("WECHAT_SECRET", False)

WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", False)

# Simple Access Control
WECHAT_ALLOW_USERS = os.getenv("WECHAT_ALLOW_USERS", "").split(",")

# Send wechat msg
WECHAT_NOTIFY_USERS = os.getenv("WECHAT_NOTIFY_USERS", "").split(",")

# DingDing Robot Token
DDING_ROBOT_TOKEN = os.getenv("DDING_TOKEN", False)


class EnvError(Exception):
    pass


SMB_USERNAME = "test"

SMB_PASSWORD = "test"


if not WECHAT_AESKEY:
    raise EnvError("WECHAT_AESKEY  environment not set")

if not WECHAT_CORPID:
    raise EnvError("WECHAT_CORPID  environment not set")

if not WECHAT_SECRET:
    raise EnvError("WECHAT_SECRET environment not set")

if not WECHAT_TOKEN:
    raise EnvError("WECHAT_TOKEN environment not set")

if not DDING_ROBOT_TOKEN:
    raise EnvError("DDING_TOKEN environment not set")


if __name__ == '__main__':
    print(WECHAT_ALLOW_USERS)
