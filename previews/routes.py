from flask_restful import Resource, reqparse
import re
import validators
from previews.model import Preview
import os
import redis
import json

from raven import Client as SentryClient
sentry = SentryClient(os.getenv("SENTRY_DSN"))


redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = redis.from_url(redis_url)


def adds_http(url):
    if re.search(r"https?:\/\/", url) is None:
        url = "http://" + url

    return url


class PreviewRequests(Resource):
    """
    Handles all requests for link previews. Requires a url argument 'url'
    to be passed in. Must be a valid url, but may or may not contain http(s)
    """
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("url", required=True, type=str, help="need a url")

        args = parser.parse_args()

        url = args.get("url")
        url = adds_http(url)

        if not validators.url(url):
            return {
                "message": {
                    "url": "invalid"
                }
            }, 400

        # Check the cache to see if we already have this sucker
        cached_preview = redis.get(url)

        if cached_preview is not None:
            cached = json.loads(cached_preview.decode("utf-8"))
            return cached, 200

        preview = Preview(url)

        try:
            preview.fetch()
        except Exception:
            sentry.captureException()
            return {
                "message": {
                    "url": "Failed to fetch '{}'".format(url)
                }
            }, 400

        preview.cache()

        return preview.to_dict(), 200
