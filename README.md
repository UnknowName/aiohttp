# Simple Aiohttp Application

## 概览
- /wechat

      实现发送消息到微信,在运行的服务器上执行命令，返回结果
    ![Shell](images/wechat-shell.png)
        
- /graylog

        Graylog的Alert告警回调
     ![Graylog](images/graylog-alert.png)
     
     *以上实现需要配合`GraylogStream`与`Graylog Alert`实现
     
## 运行

制作镜像

```bash
cd ProjectDir
# 以下两步不是必需，如果不需要则同时修改Dockerfile
cp -r /root/.kube  ./
cp `which kubectl` ./
docker build -t wechat .
```

准备docker-compose.yml

```yaml
wechat-shell:
  image: wechat:dev
  container_name: wechat-shell
  volumes:
    - ./ansible_hosts:/etc/ansible/hosts
    - ./hosts:/etc/hosts
  environment:
    # 相关变量不需要加`"`双引号
    - WECHAT_CORPID=your_corpid
    - WECHAT_SECRET=your-secret
    - WECHAT_TOKEN=your-token
    - WECHAT_AESKEY=your-aeskey
    - WECHAT_ALLOW_USERS=user1,user2
    - WECHAT_NOTIFY_USERS=user1,user2
  restart: always
  net: host
```

运行

```bash
docker-compose up -d
```