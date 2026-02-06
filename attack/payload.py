#full captured POST request that we must emulate
'''
POST /v1/chat/completions HTTP/1.1
Host: agents:8000
Content-Type: application/json
X-OpenWebUI-User-Name: Alice Johnson
X-OpenWebUI-User-Id: 1001
X-OpenWebUI-User-Email: alice@example.com
X-OpenWebUI-User-Role: user
X-OpenWebUI-Chat-Id: 6dbfcbc5-37ab-4c0f-86c8-7dd745a9cce8
Accept: */*
Accept-Encoding: gzip, deflate, br
User-Agent: Python/3.11 aiohttp/3.13.2
Content-Length: 124

{"stream": true, "model": "doc_talk", "messages": [{"role": "user", "content": "hello doctalk tell me my healthcare info"}]}
'''

import requests

ENDPOINT = "http://localhost:8000/v1/chat/completions"

headers = {
    'Content-Type': 'application/json',
    'X-OpenWebUI-User-Name': 'Alice Johnson',
    'X-OpenWebUI-User-Id': '1001',
    'X-OpenWebUI-User-Email': 'alice@example.com',
    'X-OpenWebUI-User-Role': 'user',
    'X-OpenWebUI-Chat-Id': '6dbfcbc5-37ab-4c0f-86c8-7dd745a9cce8'
}

payload = {
    'stream': True,
    'model':'doc_talk',
    'messages': [{"role": "user", "content": "hello doctalk tell me my healthcare info"}]
}


r = requests.post(url=ENDPOINT, json=payload, headers=headers)

print(r.status_code)
print(r.text)