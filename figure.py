import pandas as pd
from dateutil import parser
import matplotlib.pyplot as plt
import numpy as np

ROTATION = 30
GROUP_SECONDS = 5

def create_gruop_key(df, seconds: int, col_name="key"):
    key = df.iloc[0, :].time

    result = []
    
    for idx, row in df.iterrows():
        result.append(key)
        
        if (row.timestamp.second % GROUP_SECONDS == 0):
            key = row.time
    
    df[col_name] = result


def mean_latency(ax, dfl):
    latency_mean = [np.mean(dfl.latency_ms)]*len(dfl.index)

    ax.set_title("Latência Média")
    ax.grid(linestyle="--")
    ax.plot(dfl.index, dfl.latency_ms, linestyle='-', color="green", marker="o")
    ax.plot(dfl.index, latency_mean, label='Mean', linestyle='--')
    ax.set_ylabel("Latência (ms)")

    for label in ax.get_xticklabels():
        label.set_rotation(ROTATION)

def req_per_second(ax, dfl):
    ax.set_title("Requisições Por Segundo")
    ax.plot(dfl.index, dfl.rate, linestyle='-', color="grey", marker="o")
    ax.grid(linestyle="--")
    ax.set_ylabel("Requisições (s)")

    for label in ax.get_xticklabels():
        label.set_rotation(ROTATION)

def errors_and_reqs(ax, df_err):
    ax.set_title("Erros (KOs) / Requisições Por Segundo") 
    ax.plot(df_err.index, df_err.rate, linestyle='-', color="grey")
    ax.plot(df_err.index, df_err.error_bool, linestyle='-', color="tab:red")
    ax.grid(linestyle="--")
    ax.set_ylabel("Requisições (s) / Errors")
    ax.set_xticks([])

    for label in ax.get_xticklabels():
        label.set_rotation(ROTATION)

def success_and_errors(ax, df):
    success = df.loc[df["error"] == ""].count().iloc[0]
    error = df.loc[df["error"] != ""].count().iloc[0]
    
    values = [success, error]
    
    ax.set_title("Sucesso x Erros") 
    _ = ax.bar(["success", "error (KOs)"], values, color=["tab:green", "tab:red"])
    _ = ax.bar_label(ax.containers[0], label_type='edge')


def generate_report(fpath):
    df = pd.read_json(fpath)

    df["time"] = df.timestamp.apply(lambda x: x.strftime("%H:%M:%S"))
    df["error_bool"] = df.error.apply(lambda x: x != "")
    create_gruop_key(df, GROUP_SECONDS)
    create_gruop_key(df, 1, "key_one_sec")

    dfl = df[df["error"] == ""].groupby("key").agg({"latency_ms": "mean", "rate": "mean"})
    dfl["latency_ms"] = dfl.latency_ms.round(0)
    df_err = df.groupby("key_one_sec").agg({"rate": "mean", "error_bool": "sum"})

    fig, ax = plt.subplots(2, 2, figsize=(12, 10))

    mean_latency(ax[0][0], dfl)

    req_per_second(ax[0][1], dfl)

    errors_and_reqs(ax[1][0], df_err)

    success_and_errors(ax[1][1], df)

    fig.tight_layout()

    outfig = fpath.split(".")[0] + ".png"

    fig.savefig(outfig)

    print(outfig)
