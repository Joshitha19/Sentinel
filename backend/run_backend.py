"""
Launcher script for the SENTINEL FastAPI backend server.
"""

import os
import sys
from pathlib import Path
import uvicorn

# Ensure backend directory is in python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"[SENTINEL] Starting FastAPI server on http://{host}:{port}...")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
