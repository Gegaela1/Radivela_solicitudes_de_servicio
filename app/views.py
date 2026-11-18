from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

WEB = Path(__file__).parent / "web"
assets = StaticFiles(directory=WEB)


def index():
    return FileResponse(WEB / "index.html", headers={"Cache-Control": "no-cache"})
