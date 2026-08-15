# AI Research Agent

Web research agent — searches the live web and writes a sourced report, using only free-tier services.

**Stack:** Streamlit (UI) + Groq (LLM, free) + Tavily (search, free tier: 1000 searches/month)

---

## 1. Get free API keys (2 minutes each)

- **Groq**: https://console.groq.com → sign up → API Keys → Create key
- **Tavily**: https://tavily.com → sign up → dashboard shows your API key (free tier auto-active)

## 2. Run locally

```bash
cd research-agent
pip install -r requirements.txt

# Add your keys
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste your real keys

streamlit run app.py
```

Opens at `http://localhost:8501`.

## 3. Deploy live demo (free) — Streamlit Community Cloud

1. Push this folder to a **public GitHub repo** (e.g. `github.com/Alishba-py/research-agent`)
   ```bash
   git init
   git add .
   git commit -m "Research agent"
   git branch -M main
   git remote add origin https://github.com/Alishba-py/research-agent.git
   git push -u origin main
   ```
   ⚠️ Do NOT commit `.streamlit/secrets.toml` (it's already in `.gitignore`) — real keys stay off GitHub.

2. Go to https://share.streamlit.io → sign in with GitHub → "New app"
3. Select your repo, branch `main`, main file `app.py`
4. Before deploying, click **"Advanced settings" → Secrets** and paste:
   ```toml
   GROQ_API_KEY = "your_real_key"
   TAVILY_API_KEY = "your_real_key"
   ```
5. Click **Deploy**. You'll get a live URL like `https://your-app-name.streamlit.app` in ~2 minutes.

That URL is your shareable demo link — good for portfolio, Medium article, or client proposals.

## How it works

1. You type a research question
2. Tavily searches the web and returns content-rich excerpts (not just links)
3. Groq's Llama 3.3 70B model reads all sources and writes a structured report with inline citations `[1] [2]`
4. Report + source links are shown on screen

## Notes

- Free tiers: Groq (generous rate limits) and Tavily (1000 searches/month) are enough for a portfolio demo and moderate real use.
- To swap the LLM model, change `GROQ_MODEL` in `app.py` (see https://console.groq.com/docs/models for current free models).
- To customize report style/tone, edit `system_prompt` in `synthesize_report()`.
