from types import FunctionType
from flask import Flask

AWAITING_RETURN: int = 257
SERVER_REQ_PAGE: str = None
app: Flask = None
functions: dict[FunctionType] = {}
page_code: dict = {}
return_values: dict = {}