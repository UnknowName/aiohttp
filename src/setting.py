#!/bin/env python3


WECHAT_AESKEY = "6qkdMrq68nTKduznJYO1A37W2oEgpkMUvkttRToqhUt"

WECHAT_CORPID = "wx4586a09d8a238d66"

WECHAT_SECRET = "70iY5xGoRepqx2L6PqX2P6WjgRAQ9ZnCSvtO5T0YUXE"

WECHAT_TOKEN = "hJqcu3uJ9Tn2gXPmxx2w9kkCkCE2EPYo"

# Kubernetes Info
# default-token=$(kubectl get secret |grep default-token | awk '{print $1}')
# kubectl describe ${default-token}|grep ^token |awk '{print $NF}'
# K8S_TOKEN = ""

# K8S_APISERVER = "https://192.168.1.1:8443"

# Simple Access Control
ALLOW_USERS = ['tkggvfhpce2', 'angel-tencent']
