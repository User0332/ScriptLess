import scriptless
from flask import Flask, render_template
from scriptless import window

app = Flask(__name__)
app.debug = False

scriptless.init(app)

@app.route('/')
def index():
	return scriptless.render(
		render_template("index.html")
	)

@app.route("/otherpage")
def other():
	window.location.href = "/redirected"
	return scriptless.render(
		"other page"
	)

@app.route("/redirected")
def redirected():
	return scriptless.render(
		f"redirected to this page [{window.location.href}]"
	)
	
if __name__ == "__main__":
	app.run()