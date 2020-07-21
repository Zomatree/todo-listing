import tornado.web
import ujson as json
from . import tokens


class BasicEndpoint(tornado.web.RequestHandler):
    def initialize(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


class Endpoint(BasicEndpoint):
    def __init__(self, *args, **kwargs):
        self.database = None
        self.snowflake = None
        self.config = None
        self.body = {}
        self.token = {}
        self.user_id = None

        super().__init__(*args, **kwargs)

    async def check_user(self):
        # print(self.request.headers)
        auth = self.request.headers.get('Authorization')
        if auth is None:
            self.set_status(415)
            await self.finish({"error":'"Authorization" header is required'})
            return False

        try:
            user_id = tokens.get_user_id(auth)
        except (KeyError, tokens.jwt.DecodeError):
            self.set_status(401)
            await self.finish({"error":"invalid authorization token"})
            return
        token_secret = await self.database.fetchval("SELECT token FROM accounts WHERE userid=$1;", user_id)
        if not token_secret:
            self.set_status(401)
            await self.finish({"error":"invalid authorization token"})
            return False

        try:
            tokens.jwt.decode(auth, token_secret.encode())
        except tokens.jwt.InvalidSignatureError:
            self.set_status(401)
            await self.finish({"error":"invalid authorization token"})
            return False
        self.user_id = user_id
        return True

    async def prepare(self):
        if not await self.check_user():
            return
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

            if self.request.path == '/api/v1/auth/register':
                self.body = {'username': body.get('username'),
                             'email': body.get('email'),
                             'password': body.get('password')}
                return

            elif self.request.path == '/api/v1/auth/login':
                self.body = {'email': body.get('email'),
                             'password': body.get('password')}
                return

            if 'application/json' not in content_type:
                self.set_status(415)
                await self.finish({"error": "Content-Type must be one of: [\"application/json\"], received: "+(content_type or 'null')})
                return

            if not self.request.body:
                self.set_status(400)
                await self.finish({"error": "%s requests require JSON form data" % self.request.method})
                return