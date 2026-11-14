"""Local Qwen adapter for the prompt-template comparison runner."""

import json
from urllib.request import Request, urlopen


def generate(prompt: str) -> str:
    payload = json.dumps({
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "seed": 42, "num_ctx": 8192, "num_predict": 700},
    }).encode("utf-8")
    request = Request("http://127.0.0.1:11434/api/generate", data=payload,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=180) as response:
        text = json.load(response)["response"].strip()
    if not text:
        raise ValueError("Ollama returned an empty answer")
    return text
