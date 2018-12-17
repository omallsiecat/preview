import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from previews.routes import (
  PreviewRequests,
  HealthzEndpoint,
)
from flask_prom import monitor

app = Flask("preview")
CORS(app)
api = Api(app)

app.wsgi_app = monitor(app)

api.add_resource(PreviewRequests, "/")
api.add_resource(HealthzEndpoint, "/healthz")

if __name__ == "__main__":
  app.run(debug=os.environ.get("FLASK_DEBUG", False))
