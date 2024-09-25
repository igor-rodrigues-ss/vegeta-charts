import json

from multiprocessing import Process

from stress import stress


MAX_POOL = 8


class ProcessManager:
    processes = []

    def __init__(self, func) -> None:
        self.func = func

    def start(self, *args):
        proc = Process(target=self.func, args=args)
        self.processes.append(proc)
        proc.start()

    def should_wait(self):
        return len(self.processes) == MAX_POOL

    def wait(self):
        for proc in self.processes:
            proc.join()

        self.processes = []


def main():
    with open("config.json") as f:
        config = json.load(f)

    access_token = config["access_token"]
    test_duration = config["ramp_up"]["test_duration"]
    start_load = config["ramp_up"]["start_load"]
    max_load = config["ramp_up"]["max_load"]

    requests = config["requests"]

    proc_stress = ProcessManager(stress)

    results = []

    for request in requests:
        # fpath = stress(test_duration, start_load, max_load, access_token, request["url"], request["method"], request["id"])

        req_id = request["id"]
        results.append(f"result_{req_id}.json")

        proc_stress.start(test_duration, start_load, max_load, access_token, request["url"], request["method"], request["id"])

        if proc_stress.should_wait():
            proc_stress.wait()

    proc_stress.wait()


main()
