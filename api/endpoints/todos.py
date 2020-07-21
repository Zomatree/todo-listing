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

        row = await self.database.fetchrow("INSERT INTO todos VALUES($1, $2, $3, $4, $5) RETURNING *", id, title, description, done, self.user_id)

        await self.set_status(201)
        await self.finish(dict(row))


class Remove(endpoint.Endpoint):
    async def delete(self, id):
        result = await self.database.execute("DELETE FROM todos WHERE userid=$1 AND id=$2", self.user_id, id)
        if result == "DELETE 0":
            await self.set_status(400)
        else:
            await self.set_status(204)


def setup(**kwargs):
    return [
        (f'{kwargs["config"].API}/api/todos', Todos, kwargs),
        (f'{kwargs["config"].API}/api/todos/add', Add, kwargs),
        (f'{kwargs["config"].API}/api/todos/remove/[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}', Remove, kwargs)
    ]
