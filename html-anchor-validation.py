#!/usr/bin/env python3
"""
Validates all links in the specified page URL.

Usage:
  url_link_validation.py {url}
  url_link_validation.py -vt {url}
  url_link_validation.py https://cs.co/ise-guides

"""
__author__ = "Thomas Howard"
__email__ = "thomas@cisco.com"
__license__ = "MIT - https://mit-license.org/"

from bs4 import BeautifulSoup
import argparse
import asyncio
import aiohttp
import aiohttp_client_cache
import datetime
import os.path  # file paths & existence
import pandas as pd
import requests
import sys
import time
import urllib.parse

CACHE_DIR = "./.cache"
CACHE_EXPIRATION = datetime.timedelta(days=30)  # -1 = Never, 0 = no write, N seconds, timedelta, datetime
ICONS = {
    "CACHE": "↯",  # ⧉
    "INFO": "ⓘ",
    "NEW": "🌟",
    "GOOD": "✅",
    "FAIL": "❌",
    "WARN": "🔺",
    "TODO": "🚧",
    "MISSING": "👻",
    "UNKNOWN": "❔",
    "BUG": "🐞",
    "REDIR": "◥",  # ➚ ➱ ➲ ⇱ ⇲ ⤶ ⤷ ⤸ ⤹ ↻
}

HTTP_STATUS_ICONS = {
    # Informational responses (100 – 199)
    100: "",  # Continue
    101: "",  # Switching Protocols
    102: "",  # Processing (WebDAV)
    103: "",  # Early Hints
    # Successful responses (200 – 299)
    200: "✅",  # OK
    201: "🌟",  # Created
    202: "🚧",  # Accepted
    203: "",  # Non-Authoritative Information
    204: "👻",  # No Content
    205: "⟲",  # Reset Content
    206: "⬒",  # Partial Content
    207: "",  # Multi-Status (WebDAV)
    208: "",  # Already Reported (WebDAV)
    226: "",  # IM Used (HTTP Delta encoding)
    # Redirection messages (300 – 399)
    300: "⇶",  # Multiple Choices
    301: "◥",  # Moved Permanently
    302: "⌖",  # Found
    303: "",  # See Other
    304: "",  # Not Modified
    305: "⌦",  # Use Proxy Deprecated
    306: "",  # unused
    307: "◥",  # Temporary Redirect
    308: "◥",  # Permanent Redirect
    # Client error responses (400 – 499)
    400: "❌",  # Bad Request
    401: "🔒",  # Unauthorized
    402: "💰",  # Payment Required Experimental
    403: "⛔",  # Forbidden
    404: "👻",  # Not Found
    405: "❌",  # Method Not Allowed
    406: "❌",  # Not Acceptable
    407: "",  # Proxy Authentication Required
    408: "⏳",  # Request Timeout
    409: "",  # Conflict
    410: "👻",  # Gone
    411: "⟺",  # Length Required
    412: "",  # Precondition Failed
    413: "⟺",  # Payload Too Large
    414: "⬳",  # URI Too Long
    415: "💾",  # Unsupported Media Type
    416: "⧰",  # Range Not Satisfiable
    417: "",  # Expectation Failed
    418: "🫖",  # I'm a teapot
    421: "⧕",  # Misdirected Request
    422: "",  # Unprocessable Content (WebDAV)
    423: "🔒",  # Locked (WebDAV)
    424: "",  # Failed Dependency (WebDAV)
    425: "🚧",  # Too Early Experimental
    426: "⬆",  # Upgrade Required
    428: "⛓",  # Precondition Required
    429: "⇶",  # Too Many Requests
    431: "⟺",  # Request Header Fields Too Large
    451: "⚖",  # Unavailable For Legal Reasons
    # Server error responses (500 – 599)
    500: "💥",  # Internal Server Error
    501: "🚧",  # Not Implemented
    502: "💢",  # Bad Gateway
    503: "💢",  # Service Unavailable
    504: "⏳",  # Gateway Timeout
    505: "",  # HTTP Version Not Supported
    506: "",  # Variant Also Negotiates
    507: "💾",  # Insufficient Storage (WebDAV)
    508: "",  # Loop Detected (WebDAV)
    510: "",  # Not Extended
    511: "⛿",  # Network Authentication Required
}


def bs4ff_a_has_href_and_target_not_self(tag) -> bool:
    """
    BS4 tag filter function to ignore self-referential links.
    Returns True if the tag matches, False otherwise.

    :param tag (bs4.element.Tag) : a BeautifulSoup4 tag.
    """
    return tag.has_attr("href") and tag.has_attr("target") and tag["target"] != "_self"


async def get_all_bs4_tags(url: str = None, filter=None) -> list:
    """
    Returns a list of BeautifulSoup Tags (`bs4.element.Tag`).

    :param url (str) : a string representing a URL.
    :param filter (callable) : a BeautifulSoup4 tag filter function(tag)->bool.
    """
    with requests.Session() as session:
        response = session.get(url, allow_redirects=True)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.find_all(filter)  # tag filter function


async def get_unique_urls_from_anchor_tags(url: str, tags: list = []) -> dict:
    """
    Returns a dict mapping href string to anchor attributes and status:
        'Name' : the anchor tag inner text (linl name)
        'URL' : the anchor tag `href` attribute
        'Target': the anchor tag `target` attribute

    :param url (str) : a string representing a URL.
    :param tags (list[bs4.Tag]) : a BeautifulSoup4 tag filter function(tag)->bool.
    """
    urls = {}
    for tag in tags:
        # Fix missing URL elements using base URL
        parsed_url = urllib.parse.urlsplit(tag.get("href"), allow_fragments=False)
        if parsed_url.scheme == "" or parsed_url.netloc == "":
            joined_url = urllib.parse.urljoin(url, tag.get("href"))
            print(f"🛠 Fix URL: {tag.get('href')} ==> {joined_url}", file=sys.stderr)
            tag["href"] = joined_url

        # Save extracted links to urls dict
        urls[tag.get("href")] = {
            # 'Tag' : tag.name,
            "Name": tag.text.strip(),
            # 'Title' : tag.get('title', ''),
            "URL": tag.get("href"),
            # 'Class' : tag.get('class', ''),
            # 'ID' : tag.get('id', ''),
            "Target": tag.get("target", ""),
            # 'Rel' : tag.get('rel', ''),
            # 'Style' : tag.get('style', ''),
        }
    return urls


async def get_unique_tag_attrs(tags: list = []) -> None:
    """
    Prints a set of unique tag attributes from the list of tags specified.
    This may help understand interesting available attributes.

    :param tags ([bs4.Tag]) : a list of bs4.Tag objects.
    """
    unique_tag_attrs = set()
    [unique_tag_attrs.update(tag.attrs.keys()) for tag in tags]
    return unique_tag_attrs


# async def get_url_data (session=None, urlq:asyncio.Queue=None):
async def get_url_data(session=None, urlq: asyncio.Queue = None):
    """
    Asyncio task handler that updates the `url_data` in the urlq with information from the HTTP HEAD method.

    :param session (aiohttp.ClientSession) : an aiohttp.ClientSession to use
    :param urlq (asyncio.Queue) : the queue of `url_data` to monitor.
    """
    while True:
        url_data = await urlq.get()  # Get an item from the queue
        # print(f"🧵 {name} | q:{urlq.qsize()} | {url_data['URL']}", file=sys.stderr)
        # urls = await get_page_links(session, parent_url)
        # async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(url_data["URL"], allow_redirects=True)
            print(
                f"{ICONS['GOOD'] if response.ok else ICONS['FAIL']} | {response.status} | {url_data['Name']} | {response.url}",
                file=sys.stdout,
            )
            # print(f"{ICONS['INFO']}: {response.from_cache}, {response.created_at}, {response.expires}, {response.is_expired}", file=sys.stderr)
            if len(response.history) > 1:
                url_data["Redir"] = response.history[-1].url
            url_data["Icon"] = HTTP_STATUS_ICONS[response.status]
            url_data["Status"] = response.status
            url_data["Content-Type"] = response.headers.get("Content-Type", "")
            # url_data['Pragma'] = response.headers.get('Pragma', '')
        except Exception as e:
            print(f"{ICONS['FAIL']}: {e}", file=sys.stderr)
            url_data["Icon"] = "🆘"
            url_data["Status"] = 666
            url_data["Error"] = e
        urlq.task_done()  # Notify queue the item is processed


async def main():
    """
    Run script with async functions.
    """
    argp = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    argp.add_argument("url", action="store", type=str, help="the URL to validate")
    argp.add_argument("-f", "--force", action="store_true", default=False, help="Force a fetch", required=False)
    argp.add_argument("-t", "--timer", action="store_true", default=False, help="Time the process", required=False)
    argp.add_argument("-v", "--verbosity", action="count", default=0, help="Verbosity")
    args = argp.parse_args()
    if args.verbosity:
        print(f"ⓘ args: {args}", file=sys.stderr)
    if args.timer:
        start_time = time.time()

    # Map { href : {dict} } for tracking URL attributes
    urls_data = {}

    # Extract tags from document and return
    response = requests.get(args.url, allow_redirects=True)  # resolve any base URL redirects
    soup = BeautifulSoup(response.text, "html.parser")
    tags = soup.find_all(bs4ff_a_has_href_and_target_not_self)  # Tag filter function
    urls_data = await get_unique_urls_from_anchor_tags(response.url, tags)  # unique-ify and resolve any base URL redirects

    # Summarize document tags
    if args.verbosity:
        print(f"ⓘ Found {len(urls_data)} unique URLs from {len(tags)} tags", file=sys.stderr)
    if args.verbosity:
        print(f"ⓘ Unique tag attributes: {sorted(await get_unique_tag_attrs(tags))}", file=sys.stderr)

    # Create worker tasks to process the queue concurrently and add to the urls_data
    url_data_queue = asyncio.Queue()  # Create a queue for the URL workload
    # tasks = [asyncio.create_task(head_url_data(url_data_queue)) for ii in range(1,6)]
    cache = aiohttp_client_cache.FileBackend(cache_name=CACHE_DIR, use_temp=False)
    async with aiohttp_client_cache.CachedSession(
        cache=cache, expire_after=CACHE_EXPIRATION
    ) as session:  # cache only valid for this session run
        if args.force:
            await session.cache.clear()
        tasks = [asyncio.create_task(get_url_data(session, url_data_queue)) for ii in range(1, 6)]
        [url_data_queue.put_nowait(url_data) for url_data in urls_data.values()]
        await url_data_queue.join()  # process the queue until finished

    # Load urls_data into DataFrame for easy CSV conversion
    df = pd.DataFrame(urls_data.values())
    if args.verbosity:
        print(df.columns)
    df["Status"] = df["Status"].astype("Int64")
    if args.verbosity:
        print(df.dtypes)
    df = df.sort_values(["Status", "URL"], ascending=[False, True])
    df = df[["Icon", "Status", "Name", "URL", "Target", "Redir", "Content-Type", "Error"]]  # Re-order columns
    df.to_csv("urls.csv", index=False)
    if args.verbosity:
        print(df, file=sys.stdout)
    print(
        df[["Icon", "Status", "URL"]]
        .groupby("Status")
        .count()
        .sort_values(["Status"], ascending=False)
        .rename({"URL": "Count"}, axis="columns")
    )
    if args.timer:
        print(f"⏲ {'{0:.3f}'.format(time.time() - start_time)} seconds", file=sys.stderr)


if __name__ == "__main__":
    """
    Run as local script from command line.
    """
    asyncio.run(main())
