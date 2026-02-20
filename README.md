# Tablero Mayor — CEMACO Contact Center Dashboard

Real-time agent status dashboard for CEMACO's Contact Center, built with Streamlit. Fetches live data from an n8n webhook connected to the Freshdesk API.

## Features

- 🟢 Real-time agent availability (Disponible / En llamada / En ticket / Fuera de escritorio)
- 🔄 Auto-refresh every 60 seconds
- 🔍 Filter by status and search by name/email
- 📋 Agent detail panel with open tickets
- 📊 Summary metrics at the top

## Setup

### Local

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/tablero-mayor.git
cd tablero-mayor

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

Opens at `http://localhost:8501`

### Streamlit Cloud (free hosting)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repo and set `app.py` as the main file
5. Deploy — done!

## Configuration

Edit the top of `app.py` to change:

```python
WEBHOOK_URL = "https://jcdcemaco.app.n8n.cloud/webhook/agent-status"
REFRESH_SECONDS = 60
```

## Data Source

Data comes from an n8n workflow that:
1. Calls the Freshdesk Agents API filtered by the **Tablero Mayor** group
2. Gets all open tickets
3. Cross-references tickets to agents to infer real-time status
4. Exposes the result via a webhook endpoint

## Status Logic

| Status | Condition |
|--------|-----------|
| 📞 En llamada | Agent available + open ticket of type "Llamadas" |
| 🔵 En ticket | Agent available + any open ticket |
| 🟢 Disponible | Agent available + no open tickets |
| 🔴 Fuera de escritorio | Agent not available |
