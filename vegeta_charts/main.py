#!/bin/python3

import os
import json

from vegeta_charts.flow import FlowFile
from vegeta_charts.stress import stress
from vegeta_charts.ptypes import Request
from vegeta_charts.helpers.process_manager import ProcessManager


def main():
    if not os.path.exists("results"):
        os.mkdir("results")
    
    flow_file = FlowFile()

    proc_stress = ProcessManager(stress)

    results = []

    for request_raw in flow_file.requests():
        request = Request(**request_raw)

        results.append(f"result_{request.slug_id()}.json")

        proc_stress.start(flow_file.test_profile(), request, flow_file)

        if proc_stress.should_wait():
            proc_stress.wait()

    proc_stress.wait()


if __name__ == "__main__":
    main()
