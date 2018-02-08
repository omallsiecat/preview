# -*-coding:UTF-8-*-
import unittest
from previews.model import Preview
from previews.routes import adds_http
import redis
import os
import json
import imgix

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = redis.from_url(redis_url)

if os.getenv("IMGIX_KEY") is not None:
    builder = imgix.UrlBuilder("ada-previewer.imgix.net", use_https=True, sign_key=os.getenv("IMGIX_KEY"))
else:
    raise ValueError("Please set IMGIX_KEY in your environment variables")

IMAGE_LINK_MAX_WIDTH = 768


class PreviewUnitTests(unittest.TestCase):
    def setUp(self):
        # TODO: shorten test descriptions once branch issue3 is merged
        self.good_urls = [
            {
                "url": "https://slack.com",
                "desc": "Slack is where work flows. It's where the people you need, the information you share, and the tools you use come together to get things done.",
                "icon": "https://a.slack-edge.com/436da/marketing/img/meta/favicon-32.png",
                "image": builder.create_url("https://a.slack-edge.com/436da/marketing/img/meta/slack_hash_128.png", {'max-w': IMAGE_LINK_MAX_WIDTH}),
                "title": "Where work happens"
            },
            {
                "url": "http://productioncommunity.publicmobile.ca/t5/Announcements/Update-on-support/m-p/114863",
                "desc": "Hello Community, I want to give you an update on where we are at right now, since the last time I did so was last week. First, I want...",
                "icon": "https://rsxze77497.i.lithium.com/html/assets/PublicMobile_Favicon.ico?A019DE33B730A1F6B2A0A91F5E58D31F",
                "image": builder.create_url("https://rsxze77497.i.lithium.com/t5/image/serverpage/image-id/2606iE0F88EDF60CDAA7B?v=1.0", {'max-w': IMAGE_LINK_MAX_WIDTH}),
                "title": "Update on support"
            },
            {
                "url": "https://letterboxd.com/",
                "desc": "Letterboxd is a social network for sharing your taste in film. Use it as a diary to record your opinion about films as you watch them, or just to...",
                "icon": "https://s3.ltrbxd.com/static/img/icons/196.a7eef26f.png",
                "image": builder.create_url("https://s3.ltrbxd.com/static/img/avatar.c8a4053e.png", {'max-w': IMAGE_LINK_MAX_WIDTH}),
                "title": "Letterboxd"
            },
            {
                "url": "https://www.nytimes.com/",
                "desc": "The New York Times: Find breaking news, multimedia, reviews & opinion on Washington, business, sports, movies, travel, books, jobs, education, real estate, cars & more at nytimes.com.",
                "icon": "https://static01.nyt.com/favicon.ico",
                "image": builder.create_url("https://static01.nyt.com/images/icons/t_logo_291_black.png", {'max-w': IMAGE_LINK_MAX_WIDTH}),
                "title": "The New York Times"
            }
        ]

        self.missing_http = {
            "before": "google.com",
            "after": "http://google.com"
        }

        self.not_a_site = "https://fsdfsdfkmdslfndsjfndsjfgnsdkjnf.com"

        self.preview_dict = {
            "url": "https://slack.com/",
            "returns": {
                "desc": "Slack is where work flows. It's where the people you need, the information you share, and the tools you use come together to get things done.",
                "icon": "https://a.slack-edge.com/436da/marketing/img/meta/favicon-32.png",
                "image": builder.create_url("https://a.slack-edge.com/436da/marketing/img/meta/slack_hash_128.png", {'max-w': IMAGE_LINK_MAX_WIDTH}),
                "title": "Where work happens"
            }
        }

    def tests_good_previews(self):
        """Tests that preview function returns expected attributes"""

        for url in self.good_urls:
            preview = Preview(url["url"])
            preview.fetch()

            self.assertEqual(url["title"], preview.title)
            self.assertEqual(url["desc"], preview.desc)
            self.assertEqual(url["icon"], preview.icon)

    def adds_http(self):
        """Tests that url missing http has it added in"""

        self.assertEqual(adds_http(self.missing_http["before"]), self.missing_http["after"])

    def tests_non_site(self):
        """Tests that a url for a non-site raises an Exception"""
        preview = Preview(self.not_a_site)

        with self.assertRaises(Exception):
            preview.fetch()

    def tests_to_dict(self):
        """Tests the to_dict method"""

        preview = Preview(self.preview_dict["url"])
        preview.fetch()

        self.assertEqual(self.preview_dict["returns"], preview.to_dict())

    def tests_caching(self):
        """Tests that caching of previews works"""
        url = self.preview_dict

        preview = Preview(url["url"])
        preview.fetch()
        preview.cache(expiry=5)

        cached_preview = redis.get(url["url"])

        cached = json.loads(cached_preview.decode("utf-8"))

        title = cached["title"]
        desc = cached["desc"]
        icon = cached["icon"]
        image = cached["image"]

        self.assertEqual(preview.title, title)
        self.assertEqual(preview.desc, desc)
        self.assertEqual(preview.icon, icon)
        self.assertEqual(preview.image, image)
