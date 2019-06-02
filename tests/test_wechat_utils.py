import asyncio
import unittest

from utils.wechat import WechatXML


def async_wrapper(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
        loop.close()
    return wrapper


class TestWechatXML(unittest.TestCase):
    @async_wrapper
    async def test_parse_data(self):
        xml_str = """
        <xml>
          <toUser>testUser</toUser>
          <context>test</context>
        </xml>
        """
        context = await WechatXML.parse_data(xml_str, "context")
        user = await WechatXML.parse_data(xml_str, "toUser")
        no = await WechatXML.parse_data(xml_str, "data")
        self.assertEqual(context, "test")
        self.assertEqual(user, "testUser")
        self.assertEqual(no, "")

    @async_wrapper
    async def test_two(self):
        print("test")


if __name__ == "__main__":
    unittest.main()
