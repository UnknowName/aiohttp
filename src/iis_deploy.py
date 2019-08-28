import aiohttp_jinja2
from aiohttp import web

DOMAINS = {
    "www.a.com": [
        "128.0.255.27",
        "128.0.255.28"
    ],
    "www.b.com": [
        "128.0.255.27",
        "128.0.255.28"
    ]
}


@aiohttp_jinja2.template("iis_deploy.html")
async def deployment(request):
    if request.method == 'POST':
        print("post")
        return web.Response(status=200, text="Ok")
    elif request.method == 'GET':
        return {"domains": DOMAINS}
