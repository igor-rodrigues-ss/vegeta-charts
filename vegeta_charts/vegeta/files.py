import json
import secrets

from vegeta_charts.ptypes import Request


def _create_body_file(id: str, request: Request) -> str:
    body_fpath = f"/tmp/body_{id}_{request.slug_id()}.json"

    with open(body_fpath, "w") as fb:
        fb.write(json.dumps(request.body))

    return body_fpath
    

def create_request_file(request: Request):
    id = secrets.token_hex(nbytes=8)
    
    request_fpath = f"/tmp/{id}_{request.slug_id()}.txt"
    body_fpath = ""

    with open(request_fpath, "w") as f:
        f.write(f"{request.method.upper()} {request.url}\n")
        
        if request.headers:
            for key, value in request.headers.items():
                f.write(f"{key}: {value}\n")
        
        if request.body:
            body_fpath = _create_body_file(id, request)

            f.write(f"@{body_fpath}")

    return request_fpath, body_fpath
