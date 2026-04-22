from fastapi.testclient import TestClient

from app.myAPI import app
from app.models import OpenAIFinalResult
from pathlib import Path

client = TestClient(app)


file_path = Path(__file__).resolve().parent / "sample_data" / "inputs" / "test_prompt.txt"


try:
    with open(file_path, "r", encoding="utf-8") as file:
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

# with open("output.txt", "w", encoding="utf-8") as file:
#     file.write(f"Status code: {response.status_code}\n\n")
#     file.write(result.final_text)