import json
from typing import Dict, List

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate("service_account.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


class JSONOutputParser:
    raw_data_dir: str
    parsed_data_dir: str

    raw_data: List[Dict]
    parsed_data: Dict = {}

    def __init__(
        self,
        raw_data_dir="outputs/output.json",
    ):
        self.raw_data_dir = raw_data_dir
        with open(raw_data_dir, "r") as f:
            if f != None:
                self.raw_data = json.load(f)

    def parse(self):
        for watch in self.raw_data:
            try:
                key = watch["brand"].lower() + watch["reference"].lower()
                # Values tied to reference number
                if self.parsed_data.get(key) == None:
                    self.parsed_data[key] = {
                        "model": watch.get("model", None),
                        "nickname": watch.get("nickname", None),
                        "case_size": watch.get("case_size", None),
                        "movement": watch.get("movement", None),
                        "caliber": watch.get("caliber", None),
                        "power_reserve": watch.get("power_reserve", None),
                        "gender": watch.get("gender", None),
                        "lug_width": watch.get("lug_width", None),
                        "max._wrist_size": watch.get("max._wrist_size", None),
                        "case_thickness": watch.get("case_thickness", None),
                        "price_data": [],
                    }
                self.parsed_data[key]["price_data"].append(
                    {
                        "price": watch.get("price", None),
                        "date": watch.get("date", None),
                        "condition": watch.get("condition", None),
                        "url": watch.get("url", None),
                        "box": watch.get("box", None),
                        "paper": watch.get("paper", None),
                        "manual": watch.get("manual", None),
                        "paper_date": watch.get("paper_date", None),
                        "approximate_age": watch.get("approximate_age", None),
                        "dial_color": watch.get("dial_color", None),
                        "year": watch.get("year", None),
                        "case_material": watch.get("case_material", None),
                        "bracelet": watch.get("bracelet", None),
                        "case_back": watch.get("case_back", None),
                    }
                )
            except Exception as e:
                print(f'Error: {e}, {watch.get("url", None)}')

    def export_to_file(self, parsed_data_dir="parsed_ouputs/parsed_output.json"):
        with open(parsed_data_dir, "w") as f:
            if f != None:
                json.dump(self.parsed_data, f)

    def export_to_database(self, parsed_data_dir="parsed_outputs/parsed_output.json"):
        with open(parsed_data_dir) as f:
            if f != None:
                pass


def main():
    op = JSONOutputParser("outputs/output.json")
    op.parse()
    op.export()


if __name__ == "__main__":
    main()
