from api.utils import endpoint
import ujson as json
import uuid


class Todos(endpoint.Endpoint):
    async def get(self):
        rows = await self.database.fetch("SELECT * WHERE userid=$1")
        await self.finish(json.dumps(list(map(dict, rows))))


class Add(endpoint.Endpoint):
    async def post(self):
        title = str(self.body.get("title"))
        if not title:
            await self.set_status(400)
            return await self.finish(json.dumps({"error": "Missing title"}))
            
        description = str(self.body.get("description"))
        if not description:
            await self.set_status(400)
            return await self.finish(json.dumps({"error": "Missing description"}))

        done = bool(self.body.get("done", False))

        id = uuid.uuid4()

        row = await self.body.fetchrow("INSERT INTO todos VALUES($1, $2, $3, $4, $5) RETURNING *", id, title, description, done, self.user_id)

        await self.set_status(201)
        await self.finish(json.dumps(dict(row)))


class Remove(endpoint.Endpoint):
    def delete(self, id):
        pass

def setup(**kwargs):
    return [
        (f'{kwargs["config"].API}/todos', Todos, kwargs),
        (f'{kwargs["config"].API}/todos/add', Add, kwargs),
        (f"{kwargs["config"].API}/todos/remove/[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}", Remove, kwargs)
    ]
