import asyncio
import collections
import sys
import glob
from importlib import import_module
import ujson as json

import asyncpg
import tornado.ioloop
import tornado.platform.asyncio
import tornado.httpserver
import tornado.web


if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

with open("config.json") as f:
    config_dict = json.load(f)
    config = collections.namedtuple("config", config_dict.keys())
    config = config(*config_dict.values())


class Todo(tornado.web.Application):
    def __init__(self):
        
        self.loop = tornado.ioloop.IOLoop.current()
        self.database = None
        self.config = config

        self.loop.run_sync(self.startup)

        self.attrs = {"database": self.database, "config": self.config}
        file_names = glob.iglob('api/endpoints/**/*', recursive=True)
        
        all_endpoints = []

        for endpoint in file_names:
            if not endpoint.endswith(".py"):
                continue

            endpoint = endpoint.replace("/", ".").replace("\\", ".")[:-3]
            all_endpoints.append(import_module(endpoint).setup(**self.attrs))
            print(f"Loaded {endpoint}")

        self.endpoints = [endpoint for endpoints in all_endpoints for endpoint in endpoints]
        super().__init__(self.endpoints, template_path="api/templates", static_path="api/static")

    async def startup(self):
        self.database = await asyncpg.create_pool(**config.DATABASE_INFO)

    def start(self):
        print(f"WebServer is running at {config.URL}.")
        http_server = tornado.httpserver.HTTPServer(self, xheaders=True)
        http_server.bind(config.PORT)

        http_server.start()
        self.loop.start()

    def stop(self):
        self.loop.stop()


if sys.platform == 'win32':
    import win32api

    def handler(a, b=None):
        webserver.stop()
        sys.exit(1)
    win32api.SetConsoleCtrlHandler(handler, True)

webserver = Todo()
webserver.start()