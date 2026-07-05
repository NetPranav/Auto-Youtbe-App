import requests

headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

resp = requests.get("https://integrate.api.nvidia.com/v1/models", headers=headers)
if resp.status_code == 200:
    models = [m['id'] for m in resp.json()['data']]
    images = [m for m in models if 'stability' in m.lower() or 'sdxl' in m.lower() or 'diffusion' in m.lower()]
    print(f"Image models: {images}")
else:
    print(f"Response: {resp.text}")
