import requests
import random
import time
import json

headers = {"authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywidXNlcm5hbWUiOiJpZXRhcjMiLCJsZXZlbCI6Miwibmlja25hbWUiOiJcdTRlZTQiLCJleHAiOjE3NzIxMjg3NTN9.Q4WFCkxkxJ90k6FmXLPpnx27WA365k1Q7CAy6GQseyA"}
for i in range(3,20):
    data = {
        "chapter": f"第{i}章 {random.randint(1,1000)}",
        "content": "我是正文",
        "free": True,
    }
    r = requests.post(url="http://127.0.0.1:8080/api/content/create_content/2/", data=json.dumps(data), headers=headers)
    print(r.json())
    time.sleep(1)
