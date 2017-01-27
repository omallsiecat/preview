import os
import redis
import json
from bs4 import BeautifulSoup
import urllib
import re

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = redis.from_url(redis_url)


class Preview(object):
    def __init__(self, url, title="", desc="", icon=""):
        self.url = url
        self.title = title
        self.desc = desc
        self.icon = icon

    def fetch(self):
        """
        Fetches the url, parses the title, desc and icon
        for the website passed in
        """

        # Check cache for this object first
        cached_preview = redis.get(self.url)

        if cached_preview is not None:
            cached = json.loads(cached_preview.decode("utf-8"))
            self.title = cached["title"]
            self.desc = cached["desc"]
            self.icon = cached["icon"]
            return

        html = urllib.request.urlopen(self.url)

        soup = BeautifulSoup(
            html.read().decode("utf-8", "ignore"),
            "html.parser"
        )

        title_elems = [soup.findAll(attrs={
            attr: re.compile(r"title", re.I)
        }) for attr in ["name", "property"]]

        for i in range(1):
            if len(title_elems[i]) > 0:
                self.title = title_elems[i][0]["content"]
                break
            else:
                # Get the <title> as a string
                self.title = str(soup.title.string)

        titles = re.compile("[-–|:]+").split(self.title)

        self.title = titles[0].strip()

        # Get the desc from whatever we can find
        desc_elems = soup.findAll(attrs={"name": re.compile(r"Desc", re.I)})

        if len(desc_elems) > 0:
            self.desc = desc_elems[0]["content"]

        icon_link = soup.find("link", rel=re.compile(r"shortcut icon"))

        if icon_link is None:
            icon_link = soup.find("link", rel=re.compile(r"icon"))

        if icon_link is not None:
            # Check if icon link is global or relative
            icon_href = icon_link["href"]

            if icon_href.find("http") != -1:
                self.icon = icon_href
            else:
                self.icon = self.url + icon_href

    def to_dict(self):
        """
        Returns as a dictionary for clients
        """
        return dict(
            title=self.title,
            desc=self.desc,
            icon=self.icon
        )

    def cache(self, expiry=1800):
        """
        Serializes and caches the Preview object to Redis
        """
        serialized = json.dumps(self.to_dict())
        redis.setex(self.url, serialized.encode("utf-8"), expiry)


class TimeoutException(Exception):
    pass


def handler(signum, frame):
    raise TimeoutException
