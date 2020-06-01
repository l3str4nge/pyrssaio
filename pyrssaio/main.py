import asyncio
from asyncio import Future

import sys

import aiohttp
from lxml import etree
from typing import List, Tuple, Set

from pyrssaio.models import Article
from pyrssaio.utils import register_model


FutureResults = Tuple[Set[Future], Set[Future]]


async def fetch_content(url: str, session: aiohttp.ClientSession, **kwargs) -> str:
    resp = await session.request(method="GET", url=url, **kwargs)
    resp.raise_for_status()
    print(f"Got response {resp.status} for URL {url}")
    return await resp.text()


async def parse_content(url: str, session: aiohttp.ClientSession, **kwargs) -> List[Article]:
    try:
        text = await fetch_content(url, session, **kwargs)
    except aiohttp.ClientError as e:
        print(e)
        return []

    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    return await xml2obj(etree.fromstring(text.encode("utf-8"), parser=parser))


async def xml2obj(xml: etree) -> List[Article]:
    return [sys.modules['pyrssaio.models'].Article(item) for item in xml.iter('item')]


async def main(urls: List[str]) -> FutureResults:
    async with aiohttp.ClientSession() as session:
        return await asyncio.wait([parse_content(url, session) for url in urls])


def consume(urls: List[str]) -> FutureResults:
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(asyncio.gather(main(urls)))
    loop.close()

    for item in result[0][0]:
        yield from item.result()


if __name__ == '__main__':
    class TestArticle(Article):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.test()

        def test(self):
            print("TEST")
            
    register_model(TestArticle)
    _urls = [
        "https://www.yahoo.com/news/rss/world",
        "https://hnrss.org/newest",
        "https://www.yahoo.com/news/rss/sports"
    ]
    content = consume(_urls)
    for item in content:
        print(item.test())
