"""Development server launcher."""

import sys

try:
    import uvicorn
except ImportError:
    print("Missing dependencies. Set up a virtual environment first:")
    print("  python3 -m venv venv")
    print("  source venv/bin/activate")
    print("  pip install -r requirements.txt")
    print("  python run.py")
    sys.exit(1)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
