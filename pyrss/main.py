import asyncio
import aiohttp
from dataclasses import dataclass
from lxml import etree
from typing import List


@dataclass
class Article:
    title: str
    description: str
    date: str


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
    elements = []
    for item in xml.iter('item'):
        elements.append(Article(
            item.find("title"),
            item.find("description"),
            item.find("pubDate")
        ))

    return elements


async def main():
    urls = [
        "https://www.yahoo.com/news/rss/world",
        "https://hnrss.org/newest",
        "https://www.yahoo.com/news/rss/sports"
    ]
    async with aiohttp.ClientSession() as session:
        return await asyncio.wait([parse_content(url, session) for url in urls])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(asyncio.gather(main()))
    loop.close()

    for item in result[0][0]:
        print(item)
        for x in item.result():
            print(x)
