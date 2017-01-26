from flask_restful import Resource, reqparse
import re
import os
import validators
from previews.model import Preview


class PreviewRequests(Resource):
    """
    Handles all requests for link previews. Requires a url argument 'url'
    to be passed in. Must be a valid url, but may or may not contain http(s)
    """
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("url", type=str, help="Specify a url")

        args = parser.parse_args()

        url = args.get("url")

        if re.search(r"https?:\/\/", url) is None:
            url = "http://" + url

        if not validators.url(url):
            return dict(message="Invalid url"), 400

        preview = Preview(url)

        try:
            preview.fetch()
        except Exception as e:
            return dict(message="Failed to fetch"), 400

        preview.cache()

        return preview.to_dict(), 200
