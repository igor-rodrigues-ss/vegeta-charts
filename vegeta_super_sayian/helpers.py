import secrets
import json
from vegeta_super_sayian.ptypes import Request


def create_target_file(request: Request):
    id = secrets.token_hex(nbytes=8)
    
    target_file = f"/tmp/{id}_{request.slug_id()}.txt"
    target_file_json = f"/tmp/{id}_{request.slug_id()}.json"

    with open(target_file_json, "w") as fb:
        fb.write(json.dumps(request.body))

    with open(target_file, "w") as f:
        f.write(f"{request.method.upper()} {request.url}\n")
        f.write("Content-Type: application/json\n")
        f.write(f"@{target_file_json}")
    

    return target_file, target_file_json

