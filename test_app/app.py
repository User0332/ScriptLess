import scriptless
from scriptless import WebAPIBase, Window, Document, Location
from flask import Flask, render_template

app = Flask(__name__)
app.debug = False

scriptless.init(app)

def change_heading(window: Window, document: Document, location: Location):
	heading = document.getElementById("heading")
	
	heading.innerText+=" hi"

scriptless.register_function(
	changeHeading=change_heading
)

@app.route('/')
def index():
	return scriptless.render(
		render_template("index.html")
	)

@app.route("/otherpage")
def other():
	return scriptless.render(
		"other page"
	)

@app.route("/redirected")
def redirected():
	return scriptless.render(
		"redirected here!"
	)
	
if __name__ == "__main__":
	app.run()