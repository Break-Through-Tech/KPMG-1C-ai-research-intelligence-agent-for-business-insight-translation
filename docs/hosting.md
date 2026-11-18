# Connect GitHub Pages to live arXiv chat

GitHub Pages hosts the browser UI. A separate HTTPS service runs arXiv retrieval and answer generation. The model key stays on that service; it must not go in the repository or browser files.

## Deploy the API

1. In Render, create a **Blueprint** from this GitHub repository and select the branch used by Pages. The committed [`render.yaml`](../render.yaml) defines a small Python web service. It uses the public arXiv API and a server-selected Gemini model. It does not need Ollama on a visitor's computer.
2. When Render requests `GEMINI_API_KEY`, add it as a secret environment variable. The Blueprint supplies `GEMINI_MODEL=gemini-3.5-flash-lite`. Keep the key out of Git and set a provider spending or usage limit appropriate for the demo.
3. Wait for Render to show the service's HTTPS URL. Open `<service URL>/api/health`; it should return `{"ready":true}`. The service allows browser requests only from `https://break-through-tech.github.io` and accepts up to 30 research requests per running instance per hour.

Render's free service may take time to wake after inactivity. Its local PDF cache is temporary. Because the lightweight hosted requirements omit the cross-encoder, hosted retrieval uses the arXiv search order and lexical passage fallback. The saved evaluation scores do not apply to this hosted path.

## Connect Pages

From the repository root, replace the example URL with the Render service's actual URL:

```bash
PAGES_API_BASE_URL=https://your-service.onrender.com python scripts/build_pages_demo.py
git add docs/demo
git commit -m "Connect Pages chat to hosted arXiv API"
git push
```

Pages must publish the branch and `/docs` folder containing that commit. The build writes the public service URL, never the API key, to `docs/demo/data/runtime-config.json`. Open the [Pages site](https://break-through-tech.github.io/KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation/) and ask a new question. The **Examples** tab continues to use recorded five-paper answers.

To disconnect live chat while keeping examples, run `python scripts/build_pages_demo.py` with no `PAGES_API_BASE_URL`, then commit and push `docs/demo/data/runtime-config.json`.
