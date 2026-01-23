# Job Application Bot (Simplified)

A streamlined, AI-driven system for rapid resume tailoring, compilation, and storage.

## 🚀 "JD Only" Workflow

Provide just a **Job Description (JD)** and the bot will:
1.  **Tailor**: Optimize your LaTeX resume with ATS keywords (zero fabrication).
2.  **Adaptive Render**: Automatically fits your resume to a **single page**. If it's too long, the bot dynamically tightens margins and spacing.
3.  **Local Save**: Archive files to `~/Desktop/job applications/[Date]`. (Only PDF shown to avoid clutter).
4.  **Google Drive**: Upload to Drive and log the link for easy tracking.

### Quick Start
```bash
export PYTHONPATH=.
python3 src/agents/manager_agent.py "We are looking for a Senior PM..."
```

## 📦 Replication & Portability (The .antigravity folder)
This repository contains a **Context Capsule** in the `.antigravity/` folder. This is designed to allow any future agent to pick up exactly where we left off.

### For Future Agents:
If you are an AI agent taking over this project:
1.  Read `.antigravity/state.json` to understand the current architectural state.
2.  Review `.antigravity/history/` for the development plans and walkthroughs.
3.  Consult `.antigravity/media/` for visual verification of past work.

## 🛠 Setup instructions
1.  **Clone the Repo**: `git clone https://github.com/ChinmayHarish/job-application-bot.git`
2.  **Environment Variables**: Create a `.env` file (use `.env.example` as a template).
3.  **Authentication**:
    -   Place your `client_secrets.json` in the root.
    -   Run `python3 generate_token.py` to authenticate your Google account and generate `token.json`.
4.  **Dependencies**: Install required packages (see `pyproject.toml`).
5.  **Tectonic**: Ensure `tectonic` is installed on your OS for PDF rendering.

## 🛡 Security Note
> [!IMPORTANT]
> This repository should always be kept **PRIVATE**. It contains detailed conversation history and logic that may contain personal context. Never commit `.env`, `token.json`, or your `credentials.json` directly.
