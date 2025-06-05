# ShellCoach Phase 1 Deployment Instructions

## Render.com Setup

1. Go to [Render.com](https://render.com)
2. Click "New Web Service"
3. Connect your GitHub repo (or upload ZIP manually)
4. Set these values:

- **Environment**: Python
- **Build Command**: pip install -r requirements.txt
- **Start Command**: python app.py
- **Environment Variables**:
    - `SECRET_KEY`: your_secure_key
    - `OPENAI_API_KEY`: your_openai_key

5. Set the port binding:
    - ShellCoach uses `port 5000`
    - Render will auto-detect if you use `host="0.0.0.0"` in `app.py`

6. Click "Deploy"

You're now running ShellCoach Phase 1 on the cloud!
