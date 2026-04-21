from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

_root = Path(__file__).resolve().parent
_env = _root / ".env"
if not _env.is_file():
    raise SystemExit(
        f"Missing {_env.name} next to this script.\n"
        "Copy .env.example to .env and put your real OPENAI_API_KEY there.\n"
        "(Only .env is loaded — .env.example is just a template for GitHub.)"
    )
load_dotenv(_env)

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Give me a fun fact about space."}
    ]
)

print(response.choices[0].message.content)
