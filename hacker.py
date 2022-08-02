import secrets
import requests
import json

data: str = json.dumps(
	{
		"name": "secret_var",
		"token": secrets.token_urlsafe(20)
	}
)

headers = {
	"Content-Type": "application/json"
}


resp: requests.Response = requests.post(
	"http://127.0.0.1:5000/client-python0",
	data,
	headers=headers
)

try: print(resp.json())
except json.decoder.JSONDecodeError:
	print(resp.status_code)