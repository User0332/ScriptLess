from flask import Flask, jsonify, request
from .jsclasses import JavaScriptObject, Window
from .globals import *

def register_function(**kwargs):
	for name, func in kwargs.items():
		functions[name] = func

def create_server_handler(num: int) -> str:
	return f"""setInterval(
	() => {{
		fetch(
			"{SERVER_REQ_PAGE}{num}",
			{{
				method: "GET"
			}}
		)
		.then(
			resp => resp.json()
		)
		.then(
			json => {{
				if (json.code == '') return

				let error = ""
				let data = null

				try {{
					data = Function(json.code)()
				}} catch (e) {{
					error = e.toString()
				}}

				data = data || ""

				fetch(
					"{SERVER_REQ_PAGE}{num}",
					{{
						method: "POST",
						headers: {{
							"Content-Type": "application/json"
						}},
						body: JSON.stringify(
							{{
								data,
								error
							}}
						)
					}}
				)
			}}
		)
	}},
	100
)

window.addEventListener(
	"beforeunload", 
	e => {{
		fetch(
			"{SERVER_REQ_PAGE}{num}",
			{{
				method: "DELETE"
			}}
		)

		(e || window.event).returnValue = null;

		return null
	}}
)

const server = new Proxy({{}}, {{
		get(target, name, reciever) {{
			return () => {{
				fetch(
					"{SERVER_REQ_PAGE}{num}funcreq",
					{{
						method: "POST",
						headers: {{
							"Content-Type": "application/json"
						}},
						body: JSON.stringify(
							{{
								name: name
							}}
						)
					}}
				)
			}}
		}}
	}}
)

"""

def init(__app: Flask, server_req_path: str="/client-python") -> None:
	global app
	global SERVER_REQ_PAGE

	app = __app

	SERVER_REQ_PAGE = server_req_path

	
	@app.route(f"{SERVER_REQ_PAGE}<num>", methods=["GET", "POST", "DELETE"])
	def handle_req(num: str):
		try: num = int(num)
		except ValueError: return ""

		if (
			request.method == "POST" and
			request.is_json
		):

			data = request.json["data"]
			error: str = request.json.get("error", "")
			if error: raise ValueError(
				error
			)

			if type(data) is dict:
				return_values[num] = JavaScriptObject(data)
			else:
				return_values[num] = data	

		if request.method == "GET":
			return jsonify(
				{
					"code": page_code[num]
				}
			)

		if request.method == "DELETE":
			del page_code[num]
			del return_values[num]
			app.delete(f"{SERVER_REQ_PAGE}{num}")
			

		return jsonify({})

	@app.route(f"{SERVER_REQ_PAGE}<num>funcreq", methods=["POST"])
	def handle_post(num: str):
		try: num = int(num)
		except ValueError: return ""
		
		if request.is_json:
			name: str = request.json["name"]

			def _(*args): raise NameError(
				f"Function {name} does not exist!"
			)

			window = Window(num)

			functions.get(
				name,
				_
			)(
				window,
				window.document,
				window.location
			)

		return ""

def render(page: str) -> str:
	num: int = max(page_code)+1 if page_code else 0

	page_code[num] = ""
	return_values[num] = AWAITING_RETURN

	return f"<script>\n{create_server_handler(num)}\n</script>\n{page}"
