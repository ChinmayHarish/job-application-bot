# Job Application Bot (AI-Powered)

An automated job application agent designed to scrape job descriptions, tailor resumes (LaTeX), compile PDFs, and track applications via Google Sheets and Drive.

## 🚀 Key Features
- **Firecrawl Scraping**: robust JD extraction.
- **Gemini Tailoring**: Intelligent resume adjustment based on the target JD.
- **Tectonic Rendering**: Smooth LaTeX-to-PDF compilation.
- **Google Tracker**: Automatic logging to Sheets and storage in Drive via OAuth 2.0.
- **Dynamic Storage**: Resumes organized on the Desktop in dated subfolders.

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
