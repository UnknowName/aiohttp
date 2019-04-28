#!/bin/env python3

import os
import json
import time
import pickle
import base64
import socket
import struct
import hashlib
import xml.etree.ElementTree as ET

import aiohttp
from Crypto.Cipher import AES

class WechatError(Exception):
    pass


class WechatXML(object):
    def __init__(self):
        pass

    @staticmethod
    async def parse_data(xml_data: str, attr: str) -> str:
        try:
            root = ET.fromstring(xml_data)
            text = root.find(attr).text
        except Exception:
            text = ""
        return text

    def build_xml(self, msg: str) -> bytes:
        pass


class WechatCrypto(object):
    def __init__(self, corp_id: str, token: str, aes_key: str) -> None:
        self.corp_id = corp_id
        self.token = token
        self.aes_key = aes_key

    def _pad(self, msg: bytes, size: int = 32) -> bytes:
        """填充消息，后续加密"""
        msg_len = len(msg)
        pad_byte = size - (msg_len % size)
        if msg_len % size == 0:
            pad_byte = size
        return msg + (chr(pad_byte) * pad_byte)

    def _unpad(self, padded_msg: bytes) -> bytes:
        """解包微信加密消息"""
        # 获取加密算法的填充值
        pad_len = padded_msg[-1]
        # 16字节随机填充+4字节的消息长度
        len_byte = padded_msg[16:20]
        # 四字节的长度转换成Python的整型
        msg_len = socket.ntohl(struct.unpack("I", len_byte)[0])
        # 截取消息
        msg = padded_msg[20:msg_len+20]
        return msg
        
    def get_signature(self, timestamp: str, nonce: str, encry_msg: str) -> str:
        "获取消息签名,echostr必须是urldocode后的字符串"
        # echo_decode = urllib.parse.unquote(echostr)
        try:
            sort_str = ''.join(sorted([self.token, timestamp, nonce, encry_msg]))
            echo_sign = hashlib.sha1(sort_str.encode("utf8")).hexdigest()
        except Exception:
            echo_sign = ""
        return echo_sign

    def decry_msg(self, crypto_msg: str) -> str:
        "解密微信消息"
        base64_msg = base64.b64decode(crypto_msg)
        aes_key = base64.b64decode(self.aes_key + '=')
        iv = aes_key[:16]
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        encry_msg = cipher.decrypt(base64_msg)
        return str(self._unpad(encry_msg), encoding="utf8")


class AsyncWechat(object):
    token_fmt = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={secret}'
    send_fmt = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}'

    def __init__(self, corp_id: str, secret: str):
        self.token_url = self.token_fmt.format(corp_id=corp_id, secret=secret)

    @property
    async def _fetch_token(self):
        async with aiohttp.request("GET", self.token_url) as resp:
            json_data = await resp.json()
            return json_data.get("access_token")

    async def _cache_token(self, token: str):
        expiry_time = time.time() + (2 * 60 * 60)
        cache_dic = dict(token=token, expiry_time=expiry_time)
        with open('token.cache', 'wb') as f:
            pickle.dump(cache_dic, f)
            return True

    async def get_token(self):
        if os.path.exists('token.cache'):
            with open('token.cache', 'rb') as f:
                token_dic = pickle.load(f)
                if token_dic.get("expiry_time", time.time()) < time.time():
                    token = await self._fetch_token
                    await self._cache_token(token=token)
                    return token
                else:
                    return token_dic.get("token")
        else:
            try:
                token = await self._fetch_token
            except Exception as e:
                print(e)
            else:
                await self._cache_token(token)
                return token

    async def send_msg(self, to_user: list, msg: str):
        msg_data = dict(
            touser='|'.join(to_user), 
            msgtype='text', agentid=0, 
            text=dict(content=msg)
        )
        token = await self.get_token()
        try:
            async with aiohttp.request("POST", 
                                       self.send_fmt.format(token=token),
                                       json=msg_data) as resp:
                await resp.json()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    import setting
    import asyncio
    loop = asyncio.get_event_loop()
    wx = AsyncWechat(setting.WECHAT_CORPID, setting.WECHAT_SECRET)
    loop.run_until_complete(wx.send_msg(['tkggvfhpce2'], 'hello,world'))
    loop.close()
