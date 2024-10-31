import os
import json

from vegeta_charts.flow import FlowFile
from vegeta_charts.ptypes import Request
from vegeta_charts.profile.iprofile import TestProfile
from vegeta_charts.vegeta import files as vegeta_files
from vegeta_charts.charts.figure import generate_report


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


def stress(test_profile: TestProfile, request: Request, flow_file: FlowFile):
    request_fpath, body_fpath = vegeta_files.create_request_file(request)

    outputs = test_profile.run(request, request_fpath, debug=flow_file.debug)

    result_path = join_outputs(outputs, request.slug_id())

    generate_report(result_path, request.id)
    
    if request_fpath and os.path.exists(request_fpath):
        os.remove(request_fpath)

    if body_fpath and os.path.exists(body_fpath):
        os.remove(body_fpath)

    if os.path.exists(result_path) and flow_file.remove_results:
        os.remove(result_path)
