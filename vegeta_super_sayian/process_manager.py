from multiprocessing import Process, cpu_count


MAX_POOL = cpu_count()


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