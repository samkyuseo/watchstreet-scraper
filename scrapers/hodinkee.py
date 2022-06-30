import requests
import json
import pprint

pp = pprint.PrettyPrinter()

url = "https://shop.hodinkee.com/products.json?limit=250"
data = json.loads(requests.get(url).content)

products = data["products"]
res = {}
fails = []
for p in products:
    try:
        handle = p.get("handle").lower()
        brand = (
            p.get("vendor").lower().replace(".", "").replace("& ", "").replace(" ", "-")
        )
        model = (
            [s for s in p.get("tags") if "model_name:" in s][0]
            .replace("model_name:", "")
            .replace(" ", "-")
            .lower()
        )
        sku = p.get("variants")[0].get("sku").lower()

        reference = handle.replace(brand, "").replace(sku, "")
        reference = reference[1:-1]
        reference = reference.replace(model + "-", "")
        print("https://shop.hodinkee.com/products/" + handle)
        print(brand)
        print(model)
        print(sku)
        print(reference)
        print()
        # print(brand)
        # print(sku)
        # print(reference)
        # print(model + "\n")
    except Exception as e:
        fails.append(
            {
                "error": e,
                "title": p["title"],
                "brand": p["vendor"],
                "model": [m for m in p["tags"] if "model_name:" in m],
                "link": "https://shop.hodinkee.com/products/" + p["handle"],
            }
        )

        # what about getting it based on the handle?
        # handle - brand - sku = reference?

print("Number of fails:" + str(len(fails)))
