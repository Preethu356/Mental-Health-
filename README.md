# Mental Health Assistant — Streamlit Demo

**What this is:** a small, non-clinical Streamlit app that demonstrates a mental-health-focused assistant with mood tracking, supportive suggestions, and calming exercises.

**Contents**
- `app.py` — main Streamlit app
- `helpers.py` — simple rule-based suggestion functions
- `requirements.txt` — Python packages
- `Procfile`, `runtime.txt` — optional files for Heroku deployment
- `deploy_instructions.txt` — step-by-step deploy instructions

**Important safety note:** This app provides non-clinical supportive suggestions only. It is *not* a replacement for professional diagnosis or treatment. Include relevant crisis numbers before publishing in your target country.

## Quick start (local)
1. Create a Python virtualenv and activate it.
2. `pip install -r requirements.txt`
3. `streamlit run app.py`

## Deploy
- To deploy on **Streamlit Community Cloud**:
  1. Push the repo to GitHub.
  2. Go to https://share.streamlit.io and follow the 'new app' flow to connect your GitHub repo and branch.
- To deploy on **Heroku**:
  1. Create a Heroku app and connect to GitHub or push via git.
  2. Ensure `Procfile` is present and set buildpacks for Python.

See `deploy_instructions.txt` for a step-by-step checklist.
