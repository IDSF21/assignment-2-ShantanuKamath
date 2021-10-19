import http.client
import json

conn = http.client.HTTPSConnection("api-formula-1.p.rapidapi.com")

headers = {
    'x-rapidapi-host': "api-formula-1.p.rapidapi.com",
    'x-rapidapi-key': "7e627ff4bemsh076cf2f715b08f9p1ede64jsnb7e5375d9a8f"
    }

conn.request("GET", "/drivers?search=Lewis%20Hamilton", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
json_obj = json.loads(data.decode("utf-8"))
return  json_obj['response'][0]['image']
