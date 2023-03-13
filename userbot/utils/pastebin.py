import re

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError


class PasteBin:

    NEKOBIN_URL = "https://nekobin.com/"
    KATBIN_URL = "https://katb.in/"
    SPACEBIN_URL = "https://spaceb.in/"
    _nkey = _kkey = _skey = retry = None
    service_match = {
        "-n": "nekobin",
        "-k": "katbin",
        "-s": "spacebin",
    }

    def __init__(self, data: str = None):
        self.http = aiohttp.ClientSession()
        self.data = data
        self.retries = 3

    def __bool__(self):
        return bool(self._nkey or self._kkey or self._skey)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        await self.http.close()

    async def __call__(self, service="nekobin"):
        if service == "nekobin":
            await self._post_nekobin()
        elif service == "katbin":
            await self._post_katbin()
        elif service == "spacebin":
            await self._post_spacebin()
        else:
            raise KeyError(f"Unknown service input: {service}")

    async def _get_katbin_token(self):
        token = None
        async with self.http.get(self.KATBIN_URL) as req:
            if req.status != 200:
                return token
            content = await req.text()
            for i in re.finditer(r'name="_csrf_token".+value="(.+)"', content):
                token = i.group(1)
                break
        return token

    async def _post_nekobin(self):
        if self._nkey:
            return
        try:
            async with self.http.post(
                self.NEKOBIN_URL + "api/documents", json={"content": self.data}
            ) as req:
                if req.status == 201:
                    res = await req.json()
                    self._nkey = res["result"]["key"]
                else:
                    self.retry = "katbin"
        except ClientConnectorError:
            self.retry = "katbin"

    async def _post_katbin(self):
        if self._kkey:
            return
        token = await self._get_katbin_token()
        if not token:
            return
        try:
            async with self.http.post(
                self.KATBIN_URL,
                data={"_csrf_token": token, "paste[content]": self.data},
            ) as req:
                if req.status != 200:
                    self.retry = "spacebin"
                else:
                    self._kkey = str(req.url).split(self.KATBIN_URL)[-1]
        except ClientConnectorError:
            self.retry = "spacebin"

    async def _post_spacebin(self):
        if self._skey:
            return
        try:
            async with self.http.post(
                self.SPACEBIN_URL + "api/v1/documents",
                json={"content": self.data, "extension": "txt"},
            ) as req:
                if req.status == 201:
                    res = await req.json()
                    self._skey = res["payload"]["id"]
                else:
                    self.retry = "nekobin"
        except ClientConnectorError:
            self.retry = "nekobin"

    async def post(self, serv: str = "nekobin"):
        """Post the initialized data to the pastebin service."""
        if self.retries == 0:
            return

        await self.__call__(serv)

        if self.retry:
            self.retries -= 1
            await self.post(self.retry)
            self.retry = None

    @property
    def link(self) -> str:
        """Return the view link"""
        if self._nkey:
            return self.NEKOBIN_URL + self._nkey
        if self._kkey:
            return self.KATBIN_URL + self._kkey
        if self._skey:
            return self.SPACEBIN_URL + self._skey
        return False
