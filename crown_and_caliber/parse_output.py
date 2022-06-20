import json
from typing import Dict, List

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from pathlib import Path

import os


class JSONOutputParser:
    cwd = Path(os.getcwd())
    service_account = cwd / "service_account.json"
    output_dir = cwd / "outputs"
    raw_data_file = output_dir / "raw_output.json"
    parsed_data_file = output_dir / "parsed_output.json"

    raw_data: List[Dict]
    parsed_data: Dict = {}

    db: firestore._FirestoreClient

    def __init__(self) -> None:
        """Initialize a JSON Parser object

        1. Initialize connection to firestore
        2. Create raw_data dictionary from raw data json file
        """
        try:
            # Use a service account
            cred = credentials.Certificate(self.service_account)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()

            with open(self.raw_data_file, "r") as f:
                if f != None:
                    self.raw_data = json.load(f)
        except Exception as e:
            print(f"Parser Init Error: {e}")

    def parse(self) -> None:
        """Parse raw data and save it as a python dict member variable."""
        for watch in self.raw_data:
            if watch.get("brand") is None or watch.get("reference") is None:
                continue

            key = watch["brand"].lower() + watch["reference"].lower()
            # Values tied to reference number
            if self.parsed_data.get(key) == None:
                self.parsed_data[key] = {
                    "brand": watch["brand"],
                    "reference": watch.get("reference"),
                    "model": watch.get("model"),
                    "nickname": watch.get("nickname"),
                    "case_size": watch.get("case_size"),
                    "movement": watch.get("movement"),
                    "caliber": watch.get("caliber"),
                    "power_reserve": watch.get("power_reserve"),
                    "gender": watch.get("gender"),
                    "lug_width": watch.get("lug_width"),
                    "max._wrist_size": watch.get("max._wrist_size"),
                    "case_thickness": watch.get("case_thickness"),
                    "price_data": [],
                }
            self.parsed_data[key]["price_data"].append(
                {
                    "price": watch.get("price"),
                    "date": watch.get("date"),
                    "condition": watch.get("condition"),
                    "url": watch.get("url"),
                    "box": watch.get("box"),
                    "paper": watch.get("paper"),
                    "manual": watch.get("manual"),
                    "paper_date": watch.get("paper_date"),
                    "approximate_age": watch.get("approximate_age"),
                    "dial_color": watch.get("dial_color"),
                    "year": watch.get("year"),
                    "case_material": watch.get("case_material"),
                    "bracelet": watch.get("bracelet"),
                    "case_back": watch.get("case_back"),
                }
            )

    def export_to_file(self) -> None:
        """Export parsed output to a file."""
        with open(self.parsed_data_file, "w") as f:
            if f != None:
                json.dump(self.parsed_data, f)

    def upload_to_firebase(self) -> None:
        """Upload parsed watch data to firebase.

        1. If it a new watch, then upload everything (specs + price data)
        2. If we've already seen it
            - Just update the price data array with unique price data points
            - Check for any null specs and try to hydrate
        """
        watches_ref = self.db.collection("watches")
        for id, watch in self.parsed_data.items():
            doc_ref = watches_ref.document(id)
            if doc_ref.get().exists:
                # Only adds unique price_data objects, if not unique, doesn't add them
                doc_ref.update(
                    {"price_data": firestore.ArrayUnion(watch["price_data"])}
                )
                # Check for any null fields that is not price data and hydrate them
                watch_specs = doc_ref.get().to_dict()
                for spec, value in watch_specs.items():
                    if (
                        spec != "price_data"
                        and value is None
                        and watch[spec] is not None
                    ):
                        doc_ref.update({f"{spec}": watch[spec]})
                        print(f"{id}: {spec} was null. Replaced with {watch[spec]}")
            else:
                print("we should never be here")
                doc_ref.set(watch)


def main():
    op = JSONOutputParser()
    op.parse()
    op.upload_to_firebase()


if __name__ == "__main__":
    main()
