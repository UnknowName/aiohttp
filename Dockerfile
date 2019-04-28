FROM python:3.6-alpine
ENV APP_HOME=/opt/app \
    TZ=Asia/Shanghai \
    PATH=${APP_HOME}/bin:$PATH
ADD ./src /opt/app
WORKDIR /opt/app
RUN adduser -D -u 120002 -h /opt/app app \
    && sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories \
    && apk add gcc g++ make libffi-dev openssl-dev \
    && pip install --no-cache-dir -i https://pypi.douban.com/simple -r reque.txt\
    && rm -rf /var/cache/apk/*
ADD ./kubectl /usr/local/bin/
ADD ./.kube   /opt/app/.kube
RUN chown -R app:app /opt/app
USER app
EXPOSE 8082
CMD python main.py
