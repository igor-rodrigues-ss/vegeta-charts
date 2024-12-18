import json

from vegeta_charts.enums import TestType
from vegeta_charts.profile.spike import Spike
from vegeta_charts.profile.ramp_up import RampUp
from vegeta_charts.profile.iprofile import ITestProfile


class FlowFile:

    test_type_name = None
    remove_results: bool = True
    debug: bool = False

    def __init__(self):
        with open("flow.json") as f:
            try:
                self.flow_content = json.load(f)
            except Exception as exc:
                raise ValueError(f"Invalid flow file: {exc}")
        
        self.test_type_name = self.flow_content.get("profile", {}).get("type")

        self.remove_results = bool(self.flow_content.get("results", {}).get("remove_json", True))
        self.debug = bool(self.flow_content.get("config", {}).get("debug", False))

        self._validate()

    def _validate(self):
        if not self.test_type_name:
            raise ValueError("config.type is required on flow.json")

    def test_profile(self) -> ITestProfile:
        if self.test_type_name == TestType.RAMPUP.value:
            return RampUp(**self.flow_content["profile"]["params"])

        return Spike()
        
    def requests(self):
        return self.flow_content["requests"]