import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from previews.routes import (
  PreviewRequests,
  HealthzEndpoint,
)

app = Flask(__name__)
CORS(app)
api = Api(app)

api.add_resource(PreviewRequests, "/")
api.add_resource(HealthzEndpoint, "/healthz")

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", False))
