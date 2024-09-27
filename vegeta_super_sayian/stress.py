import os
import json

from dataclasses import dataclass

from vegeta_super_sayian.figure import generate_report
from vegeta_super_sayian.helpers import create_target_file
from vegeta_super_sayian.ptypes import RampUp, Request

DEBUG = False


@dataclass
class RampUP:
    max_load: int
    step_load: int
    step_duration: int

    def __post_init__(self):
        self.max_load = int(self.max_load)
        self.step_load = int(self.step_load)
        self.step_duration = int(self.step_duration)


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


def stress(ramp_up: RampUp, request: Request):
    initial_load = ramp_up.calculate()

    target_file = ""
    target_file_json = ""

    if request.method.upper() in ("POST", "PUT", "PATCH"):
        target_file, target_file_json = create_target_file(request)

    fpath_out = f"/tmp/out_{request.slug_id()}_0.json"

    attack(initial_load.load, initial_load.duration, fpath_out, request, target_file)

    seconds_counter = initial_load.duration

    outputs = []

    idx = 1

    for idx, next_load in enumerate(range(initial_load.load + ramp_up.step_load(), ramp_up.max_load, ramp_up.step_load()), start=1):
        fpath_out = f"/tmp/out_{request.slug_id()}_{idx}.json"
        outputs.append({"rate": next_load, "path": fpath_out})

        attack(next_load, ramp_up.step_duration(), fpath_out, request, target_file)

        seconds_counter += ramp_up.step_duration()

    sec_remain = ramp_up.test_duration - seconds_counter

    fpath_out = f"/tmp/out_{request.slug_id()}_{idx + 1}.json"

    outputs.append({"rate": ramp_up.max_load, "path": fpath_out})

    attack(ramp_up.max_load, sec_remain, fpath_out, request, target_file)

    result_path = join_outputs(outputs, request.slug_id())

    generate_report(result_path, request.id)
    
    if target_file and os.path.exists(target_file):
        os.remove(target_file)
    
    if target_file_json and os.path.exists(target_file_json):
        os.remove(target_file_json)