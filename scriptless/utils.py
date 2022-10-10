from secrets import token_urlsafe
from .jsclasses import JavaScriptObject, WebAPIBase

def generate_token() -> str: return token_urlsafe(20)
def iswebobj(obj: object) -> bool: return isinstance(obj, WebAPIBase)
def isjsobj(obj: object) -> bool: return type(obj) == JavaScriptObject