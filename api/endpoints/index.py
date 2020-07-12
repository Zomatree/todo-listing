from api.utils import endpoint


class Index(endpoint.Endpoint):
    async def get(self):
        await self.render("index.html")


def setup(**kwargs):
    return [('/', Index, kwargs)]
