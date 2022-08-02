from flask import Flask, jsonify, request
from secrets import token_urlsafe

class JavaScriptObject:
	def __init__(self, prototype: dict={}) -> None:
		self.__dict__  = prototype

class Element(JavaScriptObject): pass

class HTMLElement(Element): pass

class HTMLCollection(JavaScriptObject, list): pass

class Document(JavaScriptObject):
	# Read only Attributes
	@property
	def activeElement(self) -> HTMLElement:
		pass

	@property
	def characterSet(self) -> str:
		pass # call client

	@property
	def childElementCount(self) -> int:
		return len(self.children)

	@property
	def children(self) -> HTMLCollection:
		pass # call client

	# Read and Write Attributes
	@property
	def body(self) -> HTMLElement:
		pass # call client

	@body.setter
	def body(self, value: HTMLElement):
		pass # call client

class Location(JavaScriptObject):
	# Read only Attributes
	@property
	def origin(self) -> str:
		pass

	@property
	def ancestorOrigins(self) -> list[str]:
		pass

	@ancestorOrigins.setter
	def ancestorOrigins(self, value: list[str]):
		pass

	@property
	def href(self) -> str:
		return execute_js("return window.location.href")

	@href.setter
	def href(self, value: str):
		execute_js(f"window.location.href = '{value}'")
		
	@property
	def protocol(self) -> str:
		pass

	@protocol.setter
	def protocol(self, value: str):
		pass

	@property
	def host(self) -> str:
		pass

	@host.setter
	def host(self, value: str):
		pass

	@property
	def hostname(self):
		pass

	@hostname.setter
	def hostname(self, value: str):
		pass

	@property
	def port(self) -> str:
		pass
	
	@port.setter
	def port(self, value: str):
		pass

	@property
	def pathname(self) -> str:
		pass

	@pathname.setter
	def pathname(self, value: str):
		pass

	@property
	def search(self) -> str:
		pass


	@search.setter
	def search(self, value: str):
		pass

	@property
	def hash(self) -> str:
		pass

	@hash.setter
	def hash(self, value: str):
		pass

class Window(JavaScriptObject):
	def __init__(self):
		self.document: Document = Document()
		self.location: Location = Location()
		self.window: Window = self

def generate_token() -> str:
	return token_urlsafe(20)

def get_server_handler() -> str:
	return f"""setInterval(
	() => {{
		fetch(
			"{SERVER_REQ_PAGE}",
			{{
				method: "GET"
			}}
		)
		.then(
			resp => resp.json()
		)
		.then(
			json => {{
				console.log(json)
				if (json.code == '') return

				let val = Function(json.code)()

				if (val == undefined) val = null

				fetch(
					"{SERVER_REQ_PAGE}",
					{{
						method: "POST",
						headers: {{
							"Content-Type": "application/json"
						}},
						body: JSON.stringify(
							{{
								data: val
							}}
						)
					}}
				)
			}}
		)
	}},
	100
)
"""

def init(__app: Flask, server_req_path: str="/client-python0") -> None:
	global app
	global SERVER_REQ_PAGE

	app = __app

	SERVER_REQ_PAGE = server_req_path

	@app.route(SERVER_REQ_PAGE, methods=["GET", "POST"])
	def handle_req():
		global RETURN_VALUE

		if (
			request.method == "POST" and
			request.is_json
		):

			data = request.json["data"]

			if type(data) is dict:
				RETURN_VALUE = JavaScriptObject(data)
			else:
				RETURN_VALUE = data	

		if request.method == "GET":
			return jsonify(
				{
					"code": CODE
				}
			)

		return ""

def execute_js(code: str) -> JavaScriptObject:
	global CODE
	global RETURN_VALUE

	CODE = code

	while RETURN_VALUE is AWAITING_RETURN: pass

	CODE = ""
	ret = RETURN_VALUE

	RETURN_VALUE = AWAITING_RETURN

	return ret

def render(page: str) -> str:
	return f"<script>\n{get_server_handler()}\n</script>\n{page}"

AWAITING_RETURN: int = 257
RETURN_VALUE = AWAITING_RETURN
CODE: str = ""
SERVER_REQ_PAGE: str = None
app: Flask = None
window = Window()
document = window.document
location = window.location
