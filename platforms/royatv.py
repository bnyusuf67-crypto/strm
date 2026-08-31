import requests
import re
import json

base_url = "https://live.kwikmotion.com/royatvlive/royatv.smil/"
url = "https://ticket.roya-tv.com/api/v5/fastchannel/1"

s = requests.Session()
resplink = s.get(url)
response_json = json.loads(resplink.text)
mastlnk = response_json["data"]["secured_url"]

content_response = requests.get(mastlnk)
content = content_response.text

lines = content.split("\n")
modified_content = ""
for line in lines:
    if line.startswith("royatv"):
        full_url = base_url + line
        modified_content += full_url + "\n"
    else:
        modified_content += line + "\n"

print(modified_content)
