from .globals import *

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