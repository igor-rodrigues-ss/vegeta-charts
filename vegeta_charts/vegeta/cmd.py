import os


def log(n_requests: int, duration: int, fpath_out: str):
    print(f"{n_requests} reqs per second during {duration}s. output: {fpath_out}")


def attack(n_requests: int, duration: int, fpath_out: str, request_fpath: str, debug=False):
    cmd = f'vegeta attack -duration={duration}s -rate={n_requests} -targets={request_fpath} | vegeta encode > {fpath_out}'
    
    log(n_requests, duration, fpath_out)

    if not debug:
        os.system(cmd)

