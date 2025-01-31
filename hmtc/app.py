import solara.server.flask
from flask import Flask, g, make_response, request

app = Flask(__name__)
app.register_blueprint(solara.server.flask.blueprint, url_prefix="/")


@app.route("/hello")
def hello_world():
    return "Hi whoever you are! Do you see this?"


if __name__ == "__main__":
    app.debug = True  # Enable debug mode for template auto-reload
    app.run(use_reload=True)
