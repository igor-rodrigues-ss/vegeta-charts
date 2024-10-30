import os
import json

from vegeta_charts.helpers.helpers import create_request_file
from vegeta_charts.charts.figure import generate_report
from vegeta_charts.ptypes import Request
from vegeta_charts.flow import FlowFile


DEBUG = False


def log(n_requests, duration, fpath_out):
    print(f"{n_requests} reqs per second during {duration}s. output: {fpath_out}")


def attack(n_requests, duration, fpath_out: str, target_file: str):
    cmd = f'vegeta attack -duration={duration}s -rate={n_requests} -targets={target_file} | vegeta encode > {fpath_out}'
    
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
    request_fpath, body_fpath = create_request_file(request)

    outputs = test_profile.run(attack, request, request_fpath)

    result_path = join_outputs(outputs, request.slug_id())

    generate_report(result_path, request.id)
    
    if request_fpath and os.path.exists(request_fpath):
        os.remove(request_fpath)

    if body_fpath and os.path.exists(body_fpath):
        os.remove(body_fpath)

    if os.path.exists(result_path) and flow_file.remove_results:
        os.remove(result_path)
