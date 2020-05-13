import os
import redis
import imgix
import json
import gzip
from bs4 import BeautifulSoup
from urllib.request import (
    Request,
    urlopen,
)
import re

USER_AGENT = "Ada Preview Bot"
IMAGE_LINK_MAX_WIDTH = 768

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = redis.from_url(redis_url)

if os.getenv("IMGIX_KEY") is not None:
    builder = imgix.UrlBuilder(
        "ada-previewer.imgix.net",
        use_https=True,
        sign_key=os.getenv("IMGIX_KEY")
    )
else:
    raise ValueError("Please set IMGIX_KEY in your environment variables")


class Preview(object):
    def __init__(self, url, title="", desc="", icon="", image=""):
        self.url = url
        self.title = title
        self.desc = desc
        self.icon = icon
        self.image = image

    def fetch(self, timeout=1):
        """
        Fetches the url, parses the title, desc and icon
        for the website passed in
        """

        q = Request(self.url)
        q.add_header('User-Agent', USER_AGENT)
        html = urlopen(q, timeout=timeout)

        encoding = html.getheader("Content-Encoding")

        content = html.read()

        if encoding == "gzip":
            content = gzip.decompress(content)

        soup = BeautifulSoup(
            content.decode("utf-8", "ignore"),
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

        titles = re.compile("[-–|:•]+").split(self.title)

        self.title = titles[0].strip()

        # Get the desc from whatever we can find
        desc_elems = soup.findAll("meta", attrs={"name": re.compile(r"Desc", re.I)})

        for meta_elem in desc_elems:
            if meta_elem.attrs["content"]:
                self.desc = meta_elem.attrs["content"]
                break

        if len(self.desc.split()) > 30:
            self.desc = " ".join(self.desc.split()[0:29]).strip()

            self.desc = self.desc.strip("…")
            self.desc = self.desc.strip(".")
            self.desc += "..."

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

        # Fetch Open Graph Image
        image = soup.find("meta", property="og:image")

        if image is None:
            # Use favicon if no image is specified
            self.image = self.icon

        if image is not None:
            # Check if image link is global or relative
            image_link = image["content"]

            if image_link.find("http") != -1:
                self.image = image_link
            else:
                self.image = self.url + image_link

            self.image = builder.create_url(
                self.image,
                {'max-w': IMAGE_LINK_MAX_WIDTH}
            )

    def to_dict(self):
        """
        Returns as a dictionary for clients
        """
        return dict(
            title=self.title,
            desc=self.desc,
            icon=self.icon,
            image=self.image
        )

    def cache(self, expiry=1800):
        """
        Serializes and caches the Preview object to Redis
        """
        serialized = json.dumps(self.to_dict())
        redis.setex(self.url, serialized.encode("utf-8"), expiry)
