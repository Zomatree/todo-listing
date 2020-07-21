from api.utils import endpoint


class Index(endpoint.BasicEndpoint):
    async def get(self):
        await self.render("index.html")


def setup(**kwargs):
    return [('/', Index, kwargs)]
