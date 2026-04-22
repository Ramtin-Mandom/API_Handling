from fastapi.testclient import TestClient

from myAPI import app
from models import OpenAIFinalResult

client = TestClient(app)

try:
    with open("test_prompt.txt", "r", encoding="utf-8") as file:
        prompt = file.read()
except FileNotFoundError:
    raise FileNotFoundError("test_prompt.txt not found in the current directory.")

response = client.post(
    "/openai-request",
    json={"text": prompt}
)

# Check status
assert response.status_code == 200

# Parse response
result = OpenAIFinalResult(**response.json())

# Print + save output
print(result.final_text)

with open("output.txt", "w", encoding="utf-8") as file:
    file.write(f"Status code: {response.status_code}\n\n")
    file.write(result.final_text)