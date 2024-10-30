import os
import json

from vegeta_charts.helpers.helpers import create_target_file
from vegeta_charts.charts.figure import generate_report
from vegeta_charts.ptypes import Request
from vegeta_charts.flow import FlowFile


DEBUG = False


def log(n_requests, duration, fpath_out):
    print(f"{n_requests} reqs per second during {duration}s. output: {fpath_out}")


def attack(n_requests, duration, fpath_out: str, request: Request, target_file: str=""):
    authorization = request.headers['Authorization']

    if request.method in ("POST", "PUT", "DELETE"):
        cmd = f'vegeta attack -header "Authorization: {authorization}" -duration={duration}s -rate={n_requests} -targets={target_file} | vegeta encode > {fpath_out}'
    else:
        cmd = f'echo {request.method.upper()} "{request.url}" | vegeta attack -header "Authorization: {authorization}" -duration={duration}s -rate={n_requests} | vegeta encode > {fpath_out}'

    log(n_requests, duration, fpath_out)

    if not DEBUG:
        os.system(cmd)


def join_outputs(fpaths: list[dict], req_id: str):
    result = []

    for item in fpaths:
        fpath = item["path"]

        with open(fpath) as f:
            for raw_line in f.readlines():
                line = json.loads(raw_line)
                line["latency_ms"] = round((line["latency"] / 1000000), 3)
                line["rate"] = item["rate"]
                result.append(line)

        os.remove(fpath)

    output_path = f"results/result_{req_id}.json"

    with open(output_path, "w") as f:
        f.write(json.dumps(result))

    return output_path


def stress(test_profile, request: Request, flow_file: FlowFile):

    target_file = ""
    target_file_json = ""

    if request.method.upper() in ("POST", "PUT", "PATCH"):
        target_file, target_file_json = create_target_file(request)

    outputs = test_profile.run(attack, request, target_file)

    result_path = join_outputs(outputs, request.slug_id())

    generate_report(result_path, request.id)
    
    if target_file and os.path.exists(target_file):
        os.remove(target_file)

    if target_file_json and os.path.exists(target_file_json):
        os.remove(target_file_json)

    if os.path.exists(result_path) and flow_file.remove_results:
        os.remove(result_path)
