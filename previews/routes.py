from flask_restful import Resource, reqparse
import re
import validators
from previews.model import Preview, handler
import signal


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

        if re.search(r"https?:\/\/", url) is None:
            url = "http://" + url

        if not validators.url(url):
            return {
                "message": {
                    "url": "invalid"
                }
            }, 400

        preview = Preview(url)

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(1)

        try:
            preview.fetch()
        except Exception:
            return {
                "message": {
                    "url": "Failed to fetch '{}'".format(url)
                }
            }, 400
        except IOError:
            return {
                "message": {
                    "timeout": "request took longer than 1 sec"
                }
            }, 400

        signal.alarm(0)

        preview.cache()

        return preview.to_dict(), 200
