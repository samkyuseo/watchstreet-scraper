import requests
import json


url = "https://shop.hodinkee.com/products.json?limit=250"

data = json.loads(requests.get(url).content)

products = data["products"]
res = {}
for p in products:
    reference = p["title"].split(" ")[-1]
    vendor = p["vendor"]
    key = vendor.lower().replace(" ", "_") + reference.lower().replace(
        " ", "_"
    ).replace("/", "_")
    print(key)
    print(p["title"])
    print(p["handle"])
    print()
