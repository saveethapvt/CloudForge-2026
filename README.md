# CloudForge 2026 — Streamlit prototype

A local hackathon prototype for queue-depth based worker scaling. It simulates queue depth, estimated workers, scaling decisions, trends, history, and logs.

**Important:** This is a local simulation. It does not connect to AWS SQS, create cloud workers, or incur cloud charges.

## Files
- `app.py` — complete Streamlit application
- `requirements.txt` — Python dependencies

## Run in VS Code (Windows)

1. Extract `CloudForge_2026_Streamlit.zip`.
2. Open VS Code.
3. Click **File → Open Folder...** and select the extracted `CloudForge_2026` folder.
4. Open **Terminal → New Terminal**.
5. Create a virtual environment (recommended):

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt terminal and run:

   ```bat
   .venv\Scripts\activate.bat
   ```

6. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

7. Start the app:

   ```powershell
   python -m streamlit run app.py
   ```

8. A browser tab should open. If it does not, copy the `Local URL` shown in the terminal (usually `http://localhost:8501`) into your browser.

## Test the demo
- **Add 5 Demo Tasks**: increases the simulated queue by 5.
- **Auto Generate 10 Tasks**: increases it by 10.
- **Process 5 Tasks**: decreases the queue by up to 5.
- **Reset Task Counter**: sets the queue to 0.
- Queue 0–5 → `SCALE DOWN`; 6–19 → `STEADY`; 20+ → `SCALE UP`.
- The Workers, Queue, Scaling, Logs, and Settings pages are available in the sidebar.
- Use Settings to change maximum estimated workers and tasks-per-worker.

## Common fixes
- If `py` is not recognized, try `python --version` and use `python` in place of `py`.
- If `streamlit` is not recognized, run the app using `python -m streamlit run app.py`.
- If port 8501 is busy, run `python -m streamlit run app.py --server.port 8502`.
- Keep the terminal open while using the app. Stop it with `Ctrl+C`.

## Replace an existing app
Make a backup copy of your current `app.py` first. Then replace its contents with the `app.py` included here, and update `requirements.txt`. If your current project has other files, do not delete them unless you know they are not needed.