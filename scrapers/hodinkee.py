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
        title = p["title"]
        brand = p["vendor"]
        model = [m for m in p["tags"] if "model_name:" in m][0].replace(
            "model_name:", ""
        )
        print(title)
        print(brand)
        print(model + "\n")
    except:
        fails.append(
            {
                "title": p["title"],
                "brand": p["vendor"],
                "model": [m for m in p["tags"] if "model_name:" in m],
                "link": "https://shop.hodinkee.com/products/" + p["handle"],
            }
        )

# pp.pprint(fails)
