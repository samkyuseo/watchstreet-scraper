from fileinput import filename
import os
import json
from typing import Dict, List
from datetime import datetime
import logging

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from pathlib import Path


# Firestore samples: https://cloud.google.com/firestore/docs/samples/
# Firestore how to guides: https://cloud.google.com/firestore/docs/how-to


class JSONOutputParser:
    # Directories
    cwd = Path(os.getcwd())
    service_account = cwd / "service_account.json"
    output_dir = cwd / "output"
    log_dir = cwd / "logs"

    # Files
    raw_data_file = output_dir / f"raw-{datetime.today().strftime('%Y-%m-%d')}.json"
    parsed_data_file = (
        output_dir / f"parsed-{datetime.today().strftime('%Y-%m-%d')}.json"
    )
    error_data_file = log_dir / f"{datetime.today().strftime('%Y-%m-%d')}.json"

    # Datastores
    raw_data: List[Dict]
    parsed_data: Dict = {}
    error_data: List[Dict] = []

    # Firebase
    db: firestore._FirestoreClient

    def __init__(self) -> None:
        """Initialize a JSON Parser object

        1. Initialize connection to firestore
        2. Create raw_data dictionary from raw data json file
        3. Initialize the logger
        """
        try:
            # Use a service account
            cred = credentials.Certificate(self.service_account)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()

            # Open datafile to parse
            with open(self.raw_data_file, "r") as f:
                if f != None:
                    self.raw_data = json.load(f)

            # Init logger - just sticking with DEBUG, INFO, and ERROR
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s.%(msecs)03d %(levelname)-5s %(message)s",
                datefmt="%H:%M:%S",
                handlers=[
                    logging.FileHandler(
                        f"{self.log_dir / datetime.today().strftime('%Y-%m-%d')}.log",
                        mode="a+",
                    ),
                    logging.StreamHandler(),
                ],
            )
            logging.info("============ Fresh Run ============")  # signal a fresh run

        except Exception as e:
            logging.error(f"JSONParser init error: {e}")

    def parse(self) -> None:
        """Parse raw data and save it as a python dict member variable."""

        for watch in self.raw_data:
            # Useless if any of these are missing
            if (
                watch.get("brand") is None
                or watch.get("reference") is None
                or watch.get("price") is None
            ):
                continue
            # All " " => "_"
            # All "/" => "/"
            key = watch["brand"].lower().replace(" ", "_") + watch[
                "reference"
            ].lower().replace(" ", "_").replace("/", "_")
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
                    "price": int(watch.get("price").replace("$", "").replace(",", "")),
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

        with open(self.parsed_data_file, "w+") as f:
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
            try:
                doc_ref = watches_ref.document(id)
                if doc_ref.get().exists:
                    logging.debug(f"Watch {id} already exists.")
                    # Only adds unique price_data objects, if not unique, doesn't add them
                    res = doc_ref.update(
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
                            logging.debug(
                                f"Watch {id}: {spec} was null. Replaced with {watch[spec]}"
                            )
                else:
                    logging.debug(f"Setting new watch {id}")
                    doc_ref.set(watch)
            except Exception as e:
                logging.error(f"Error adding watch {id}")
                self.error_data.append({"error": str(e), "watch": {**watch}})

        # Dump any error_data into log file
        with open(self.error_data_file, "w+") as f:
            json.dump(
                {
                    "Number of errors": f"{len(self.error_data)}",
                    "error_data": f"{self.error_data}",
                },
                f,
            )


def main():
    op = JSONOutputParser()
    op.parse()
    # # op.export_to_file()
    op.upload_to_firebase()


if __name__ == "__main__":
    main()
