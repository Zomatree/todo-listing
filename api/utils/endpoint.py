from abc import ABC

import tornado.web
import ujson as json


class Endpoint(tornado.web.RequestHandler, ABC):

    def __init__(self, *args, **kwargs):
        self.database = None
        self.config = None
        self.body = {}
        self.token = {}
        self.user_id = None

        super().__init__(*args, **kwargs)

    async def prepare(self):
        content_type = self.request.headers.get("Content-Type")

        if self.request.method == 'GET':
            if self.request.body:
                self.set_status(400)
                await self.finish({"error": "GET requests cannot contain a body"})
                return
            return

        elif self.request.method in ('POST', 'PUT', 'PATCH'):
            if "application/json" in content_type:
                try:
                    self.body = body = json.loads(self.request.body)
                except:
                    self.body = body = {}

            else:
                body = self.request.body_arguments
                for a, b in body.items():
                    body[a] = b[0].decode()

            if 'application/json' not in content_type:
                self.set_status(415)
                await self.finish({"error": f"Content-Type must be one of: [\"application/json\"], received: {content_type or 'null'}"})
                return

            if not self.request.body:
                self.set_status(400)
                await self.finish({"error": f"{self.request.method} requests require JSON form data"})
                return

    def initialize(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            