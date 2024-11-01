#!/bin/python3

import os

from vegeta_charts import stress_test
from vegeta_charts.dto.flow import FlowFile
from vegeta_charts.dto.request import Request
from vegeta_charts.helpers.process_manager import ProcessManager


# TODO: adicionar escolha de gráficos
# TODO: validar caso todas as requisições falhe. (Nesses casos a geração de gáficos está falhando)
# TODO: colocar nos KOs somente status code 0
# TODO: request must be a list
# TODO: test_duration min must be 10 seconds


def main():
    if not os.path.exists("results"):
        os.mkdir("results")
    
    flow_file = FlowFile()

    proc_stress = ProcessManager(stress_test.run)

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
