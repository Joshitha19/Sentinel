"""
Launcher script for the SENTINEL FastAPI backend server.
"""

import sys
from pathlib import Path
import uvicorn

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    print("[SENTINEL] Starting FastAPI server on http://localhost:8000...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
