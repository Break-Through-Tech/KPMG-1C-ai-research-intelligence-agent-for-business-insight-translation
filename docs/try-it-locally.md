# Try the live research chat on your computer

The GitHub Pages link shows recorded example answers. To ask a **new** question, run the chat on your own computer with Ollama. The model runs locally; the app uses the internet to search arXiv and download a few public papers. You do not need a Gemini key, a Render account, or the Jupyter notebook.

## 1. Install the two prerequisites

- Install [Python 3.10 or newer](https://www.python.org/downloads/) and [Ollama](https://ollama.com/download/).
- Start the Ollama app on macOS or Windows. On Linux, start `ollama serve` in a separate terminal if Ollama is not already running.
- In a terminal, download the model used in our evaluation:

  ```bash
  ollama pull qwen2.5:7b
  ```

The model download is separate from the repository download and may take a while. If `ollama pull` cannot connect, make sure Ollama is running, then retry it.

## 2. Download the repository

On [the GitHub repository](https://github.com/Break-Through-Tech/KPMG-1C-ai-research-intelligence-agent-for-business-insight-translation), choose **Code → Download ZIP**. Unzip it and open a terminal in the extracted folder (the one containing `frontend_server.py`). You can also use `git clone` if you prefer.

## 3. Install the small chat dependency

On macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pypdf
```

On Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install pypdf
```

The chat can run with this small install. It uses a simpler passage ranking method when the optional cross-encoder is not installed. Team members who want the full evaluation environment can install `evaluation/requirements.txt` instead.

## 4. Start the chat

On macOS or Linux:

```bash
.venv/bin/python frontend_server.py --arxiv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe frontend_server.py --arxiv
```

Leave that terminal open and visit **http://127.0.0.1:8765** in your browser. **Ask arXiv** should be selected. Try: “How do recent papers evaluate the faithfulness of retrieval-augmented generation answers?” Open a cited source to see the passage the answer used. You can also switch to **Examples** to see the recorded five-paper answers.

The first live question can be slow because the app searches arXiv and reads PDFs. Search is on demand across arXiv's catalog; the app does not download or index all of arXiv. The five-paper and tiny BEIR scores in the README do not measure this live search path.

## If something does not start

- **Ollama unavailable:** Start the Ollama app, or run `ollama serve` in a separate terminal. Run `ollama list` to check that `qwen2.5:7b` is installed.
- **Missing `pypdf`:** Repeat the install command from step 3 in the extracted repository folder.
- **Port 8765 is in use:** Add `--port 8766` to the start command and open `http://127.0.0.1:8766` instead.
- **No papers or a slow answer:** Check the internet connection. Live questions need access to arXiv; model generation runs in Ollama on your computer.
- **arXiv rate limit or timeout:** Wait a few minutes before retrying. The public arXiv API can throttle or delay searches, and repeated retries can make this worse.

To stop the chat, press **Ctrl+C** in its terminal. The local server only listens on your computer. Do not put private KPMG or client information into the public arXiv search prompt.
