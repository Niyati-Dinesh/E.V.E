# =============================================================================
# MAIN BACKEND FILE
# START - uvicorn main:app --reload --port 8000
#
# Architecture:
#   React (5173) → FastAPI backend (8000) → Master Controller (8001)
#
# This file starts FastAPI on 8000 AND auto-launches the E.V.E. start_system.py.
# =============================================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from api.routers import auth, tasks, feedback, forgot_password, verify_email, profile
import subprocess
import sys
import os
import threading
import time

app = FastAPI(title="E.V.E Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded avatars as static files
# Avatars are saved to static/avatars/ by the profile router
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(feedback.router)
app.include_router(forgot_password.router)
app.include_router(verify_email.router)
app.include_router(profile.router)


@app.get("/")
def root():
    return {"message": "E.V.E Backend is running on port 8000"}


@app.get("/health")
def health():
    return {"status": "healthy", "port": 8000}


# =============================================================================
# AUTO-START E.V.E. SYSTEM (master controller on 8001 + workers)
# =============================================================================

_eve_process = None


def _start_eve_system():
    """Launch start_system.py after uvicorn has fully bound port 8000."""
    global _eve_process

    time.sleep(3)

    project_root = os.path.dirname(os.path.abspath(__file__))
    start_script = os.path.join(project_root, "start_system.py")

    if not os.path.exists(start_script):
        print(f"\n⚠️  start_system.py not found at: {start_script}")
        print("    Manually run:  python start_system.py")
        return

    print("\n🚀 Auto-launching E.V.E. system (master:8001 + workers)...")

    try:
        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE

        _eve_process = subprocess.Popen(
            [sys.executable, start_script],
            cwd=project_root,
            **kwargs,
        )
        print(f"✅ E.V.E. system launched  (PID {_eve_process.pid})")
        print(f"   Master controller → http://localhost:8001/health")
    except Exception as e:
        print(f"❌ Failed to launch E.V.E. system: {e}")
        print(f"   Run manually:  python start_system.py")


threading.Thread(target=_start_eve_system, daemon=True).start()