from api.utils import endpoint


class NotFound(endpoint.BasicEndpoint):
    async def get(self):
        await self.render("404.html", url=self.request.uri)


def setup(**kwargs):
    return [('/.*', NotFound, kwargs)]
