import aiohttp


class AsyncDDing(object):
    _send_fmt = "https://oapi.dingtalk.com/robot/send?access_token={token}"

    def __init__(self, token: str) -> None:
        self.send_api = self._send_fmt.format(token=token)

    async def send_msg(self, msg: str) -> str:
        msgs = {
            'msgtype': 'text',
            'text': {
                'content': msg
            }
        }
        async with aiohttp.request('POST', self.send_api, json=msgs) as resp:
            return await resp.json()
