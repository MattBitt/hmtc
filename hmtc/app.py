import solara.server.flask
from flask import Flask

app = Flask(__name__)
app.register_blueprint(solara.server.flask.blueprint, url_prefix="/")


@app.route("/hello")
def hello_world():
    return "Hi Earth"


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
