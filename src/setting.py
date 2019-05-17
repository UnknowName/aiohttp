import os

WECHAT_AESKEY = os.getenv("WECHAT_AESKEY", False)

WECHAT_CORPID = os.getenv("WECHAT_CORPID", False)

WECHAT_SECRET = os.getenv("WECHAT_SECRET", False)

WECHAT_TOKEN = os.getenv("WECHAT_TOKEN", False)

# Kubernetes Info
# default-token=$(kubectl get secret |grep default-token | awk '{print $1}')
# kubectl describe ${default-token}|grep ^token |awk '{print $NF}'
# K8S_TOKEN = ""

# K8S_APISERVER = "https://192.168.1.1:8443"

# Simple Access Control
ALLOW_USERS = ['tkggvfhpce2', 'angel-tencent']

# Send wechat msg
NOTIFY_USERS = ['tkggvfhpce2']


class EnvError(Exception):
    pass


if not WECHAT_AESKEY:
    raise EnvError("WECHAT_AESKEY  environment not set")

if not WECHAT_CORPID:
    raise EnvError("WECHAT_CORPID  environment not set")

if not WECHAT_SECRET:
    raise EnvError("WECHAT_SECRET environment not set")

if not WECHAT_TOKEN:
    raise EnvError("WECHAT_TOKEN environment not set")


if __name__ == '__main__':
    print(os.getenv("WECHAT_AESKEY"))
