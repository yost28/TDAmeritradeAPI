import requests

from config import client_id

endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/quotes".format("GOOG")

payload = {'apikey': client_id
           }

content = requests.get(url=endpoint, params=payload)

data =content.json()
print(data)