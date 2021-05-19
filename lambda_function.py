import json
import urllib3

def lambda_handler(event, context):
    http = urllib3.PoolManager()
    for record in event['Records']:
        print("test start")
        payload = record["body"]
        print(str(payload))
        r = http.request('POST', 'https://{{api_url}}',
        body=payload, headers={'Content-Type': 'application/json'})
        if r.status != 200:
            context.fail(json.stringify(r.data))
