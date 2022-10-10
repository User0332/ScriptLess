import scriptless
from scriptless.utils import isjsobj
from scriptless.jsclasses import WebAPIBase, Window, Document, Location
from flask import Flask, render_template

app = Flask(__name__)
app.debug = True

scriptless.init(app)

def change_heading(window: Window, document: Document, location: Location):
	heading = document.getElementById("heading")
	
	style = heading.execute_js(f"return {heading._code}.style")

	if not isjsobj(style): return

	color = "blue" if style.color == "red" else "red"

	heading.execute_js(
		f'{heading._code}.style="color: {color};"'
	)

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