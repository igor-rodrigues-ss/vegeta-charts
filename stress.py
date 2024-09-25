import os
import json

from dataclasses import dataclass

from figure import generate_report


LOAD_TIME_PERCENT = 0.1
DEBUG = False


@dataclass
class Load:
    load: int
    duration: int

    def __post_init__(self):
        self.load = int(self.load)
        self.duration = int(self.duration)


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


def req(n_requests, duration, fpath_out, access_token, url, method):
    if method.upper() == "POST":
        cmd = f'vegeta attack -header "Authorization: Bearer {access_token}" -targets=post-file.txt -duration={duration}s -rate={n_requests} | vegeta encode > {fpath_out}'
    else:
        cmd = f'echo {method.upper()} "{url}" | vegeta attack -header "Authorization: Bearer {access_token}" -duration={duration}s -rate={n_requests} | vegeta encode > {fpath_out}'

    log(n_requests, duration, fpath_out)

    if not DEBUG:
        os.system(cmd)


def ramp_up_calculation(test_duration: int, start_load: int, max_load: int):
    initial_load_time = test_duration * LOAD_TIME_PERCENT

    ramp_up_step_time = 1
    ramp_up_step_load = 10

    initial_load = Load(start_load, initial_load_time)
    ramp_up = RampUP(max_load, ramp_up_step_load, ramp_up_step_time)

    return initial_load, ramp_up


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

    output_path = f"result_{req_id}.json"

    with open(output_path, "w") as f:
        f.write(json.dumps(result))

    return output_path


def stress(test_duration, start_load, max_load, access_token, url, method, req_id):
    initial_load, ramp_up = ramp_up_calculation(test_duration, start_load, max_load)

    fpath_out = f"out_{req_id}_0.json"
    req(initial_load.load, initial_load.duration, fpath_out, access_token, url, method)

    seconds_counter = initial_load.duration

    outputs = []

    idx = 1

    for idx, next_load in enumerate(range(initial_load.load + ramp_up.step_load, ramp_up.max_load, ramp_up.step_load), start=1):
        fpath_out = f"out_{req_id}_{idx}.json"
        outputs.append({"rate": next_load, "path": fpath_out})

        req(next_load, ramp_up.step_duration, fpath_out, access_token, url, method)

        seconds_counter += ramp_up.step_duration

    sec_remain = test_duration - seconds_counter

    fpath_out = f"out_{req_id}_{idx + 1}.json"
    outputs.append({"rate": ramp_up.max_load, "path": fpath_out})

    req(ramp_up.max_load, sec_remain, fpath_out, access_token, url, method)

    result_path = join_outputs(outputs, req_id)

    generate_report(result_path)
