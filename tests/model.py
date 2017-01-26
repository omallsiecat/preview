#-*-coding:UTF-8-*-
import unittest
from previews.model import Preview

class PreviewUnitTests(unittest.TestCase):
    def setUp(self):
        self.urls = {
            "https://usecanvas.com/": {
                "desc": "",
                "icon": "https://usecanvas.com/images/favicon.ico",
                "title": "Canvas"
            },
            "http://productioncommunity.publicmobile.ca/t5/Announcements/Update-on-support/m-p/114863": {
                "desc": "Hello Community, I want to give you an update on where we are at right now, since the last time I did so was last week. First, I want to start off by",
                "icon": "http://rsxze77497.i.lithium.com/html/assets/PublicMobile_Favicon.ico?A019DE33B730A1F6B2A0A91F5E58D31F",
                "title": " Update on support - Community"
            },
            "https://letterboxd.com/": {
                "desc": "Letterboxd is a social network for sharing your taste in film. Use it as a diary to record your opinion about films as you watch them, or just to keep track of films you’ve seen in the past. Rate, review and tag films as you add them. Find and follow your friends to see what they’re enjoying. Keep a watchlist of films you’d like to see, and create lists/collections on any topic.",
                "icon": "https://s4.ltrbxd.com/static/img/icons/196.d0437325.png",
                "title": "Letterboxd • Your life in film"
            },
            "https://google": None,
            "https:google.com": None,
            "https://.com": None,
        }

    def tests_previews(self):
        """Tests that preview function returns expected attributes"""

        for url in self.urls:
            preview = Preview(url).fetch()

            self.assertEqual(url["title"], preview.title)
            self.assertEqual(url["desc"], preview.desc)
            self.assertEqual(url["icon"], preview.icon)
