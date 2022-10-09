from types import FunctionType
from flask import Flask, jsonify, request
from secrets import token_urlsafe

AWAITING_RETURN: int = 257
SERVER_REQ_PAGE: str = None
app: Flask = None
functions: dict[FunctionType] = {}
page_code: dict = {}
return_values: dict = {}

class JavaScriptObject:
	def __init__(self, prototype: dict={}) -> None:
		self.__dict__  = prototype

class WebAPIBase(JavaScriptObject):
	def __init__(self, pagenum: int):
		self._pagenum = pagenum

	def execute_js(self, code: str) -> JavaScriptObject:
		page_code[self._pagenum] = code

		while return_values[self._pagenum] is AWAITING_RETURN: pass # wait for return value

		return_value: JavaScriptObject = return_values[self._pagenum] # get return value
		
		return_values[self._pagenum] = AWAITING_RETURN # reset return value
		
		page_code[self._pagenum] = "" # clear req


		return return_value

class Element(WebAPIBase):
	def __init__(self, pagenum, code):
		super().__init__(pagenum)
		self._code = code

	@property
	def innerText(self) -> str:
		return self.execute_js(f"return {self._code}.innerText")

	@innerText.setter
	def innerText(self, value) -> None:
		self.execute_js(f"{self._code}.innerText = {value!r}")
		

class HTMLElement(Element): pass

class HTMLCollection(WebAPIBase, list): pass

class Document(WebAPIBase):
	def getElementById(self, id: str) -> Element:
		return Element(
			self._pagenum,
			f"document.getElementById({id!r})"
		)

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

class Location(WebAPIBase):
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
		return self.execute_js("return window.location.href")

	@href.setter
	def href(self, value: str):
		self.execute_js(f"window.location.href = '{value}'")
		
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

class Window(WebAPIBase):
	def __init__(self, pagenum: int):
		super().__init__(pagenum)
		self.document: Document = Document(pagenum)
		self.location: Location = Location(pagenum)
		self.window: Window = self

def generate_token() -> str:
	return token_urlsafe(20)

def register_function(**kwargs):
	for name, func in kwargs.items():
		functions[name] = func

def create_server_handler(num: int) -> str:
	window = Window(num)

	@app.route(f"{SERVER_REQ_PAGE}{num}", methods=["GET", "POST", "DELETE"])
	def handle_req():
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
			

		return ""

	@app.route(f"{SERVER_REQ_PAGE}{num}funcreq", methods=["POST"])
	def handle_post():
		if request.is_json:
			name: str = request.json["name"]

			def _(*args): raise NameError(
				f"Function {name} does not exist!"
			)

			functions.get(
				name,
				_
			)(
				window,
				window.document,
				window.location
			)

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

				try {{
					let data = Function(json.code)()
				}} catch (e) {{
					error = e.toString()
				}}

				if (data == undefined) data = null

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

def render(page: str) -> str:
	num: int = max(page_code)+1 if page_code else 0

	page_code[num] = ""
	return_values[num] = AWAITING_RETURN

	return f"<script>\n{create_server_handler(num)}\n</script>\n{page}"
