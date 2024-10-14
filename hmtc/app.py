import solara.server.flask
from flask import Flask, g, make_response, request
from pyinstrument import Profiler

app = Flask(__name__)
app.register_blueprint(solara.server.flask.blueprint, url_prefix="/")


@app.route("/hello")
def hello_world():
    return "Hi Earth"


# i think this is just measuring the conversion of the .py files
# to .vue files, but i'm not sure
@app.before_request
def before_request():
    if "profile" in request.args:
        g.profiler = Profiler()
        g.profiler.start()


@app.after_request
def after_request(response):
    if not hasattr(g, "profiler"):
        return response
    g.profiler.stop()
    output_html = g.profiler.output_html()
    return make_response(output_html)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
