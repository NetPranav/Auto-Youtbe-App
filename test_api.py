import os
from openai import OpenAI

api_key = "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"
base_url = "https://integrate.api.nvidia.com/v1"

client = OpenAI(base_url=base_url, api_key=api_key)

try:
    print("Testing meta/llama3-8b-instruct...")
    completion = client.chat.completions.create(
        model="meta/llama3-8b-instruct",
        messages=[{"role":"user","content":"Hello"}],
        max_tokens=10
    )
    print("Response:", completion.choices[0].message.content)
except Exception as e:
    print("Error:", e)

try:
    print("\nTesting glm-5.2...")
    completion = client.chat.completions.create(
        model="glm-5.2",
        messages=[{"role":"user","content":"Hello"}],
        max_tokens=10
    )
    print("Response:", completion.choices[0].message.content)
except Exception as e:
    print("Error:", e)
