#!/bin/python3

"""
python3 -m vegeta_super_sayian.main
"""

import os
import json

from vegeta_super_sayian.stress import stress
from vegeta_super_sayian.ptypes import RampUp, Request
from vegeta_super_sayian.process_manager import ProcessManager


def main():
    with open("flow.json") as f:
        config = json.load(f)
    
    if not os.path.exists("results"):
        os.mkdir("results")
    
    ramp_up = RampUp(**config["config"]["ramp_up"])

    del config["config"]["ramp_up"]

    requests = config["requests"]

    proc_stress = ProcessManager(stress)

    results = []

    for request_raw in requests:
        request = Request(**request_raw)

        results.append(f"result_{request.slug_id()}.json")

        proc_stress.start(ramp_up, request)

        if proc_stress.should_wait():
            proc_stress.wait()

    proc_stress.wait()


main()
