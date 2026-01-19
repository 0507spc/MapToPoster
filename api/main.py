from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import subprocess
import tempfile

app = FastAPI(title="MapToPoster API", version="1.0.0")

# ---------- Models ----------

class MapRequest(BaseModel):
    # Defaults
    location: str = "London,UK"
    style: str = "minimal"
    zoom: Optional[int] = 11
    width: Optional[int] = 1200
    height: Optional[int] = 800
    output_format: Optional[str] = "png"

# ---------- Health endpoints ----------

@app.get("/health")
async def health():
    """Basic 'is up' check."""
    return {"status": "ok", "service": "maptoposter-api"}

@app.get("/ready")
async def ready():
    """
    'Is working' check.
    Verifies create_map_poster module import and a quick dry-run.
    """
    try:
        # Verify import of the script/module
        import create_map_poster  # type: ignore

        # Try a very small / dry run call via subprocess.
        # Adjust args to match real CLI of create_map_poster.py when needed.
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "test.png"
            cmd = [
                "python",
                "create_map_poster.py",
                "--city", "TestCity",
                "--country", "TestCountry",
                "--output", str(output),
            ]
            subprocess.run(
                cmd,
                cwd="/home/python/app/maptoposter",
                capture_output=True,
                text=True,
                timeout=60,
                check=True,
            )

        return {"status": "ready", "service": "maptoposter"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {e!s}")

# ---------- Generate endpoints ----------

def _build_output_path(location: str, style: str, output_format: str = "png") -> Path:
    safe_loc = location.replace(",", "_").replace(" ", "_")
    safe_style = style.replace(" ", "_")
    posters_dir = Path("/home/python/app/posters")
    posters_dir.mkdir(parents=True, exist_ok=True)
    return posters_dir / f"{safe_loc}_{safe_style}.{output_format}"

def _run_generation(request: MapRequest):
    output_path = _build_output_path(request.location, request.style, request.output_format)

    # MapToPoster repo root in container
    repo_root = Path("/home/python/app/maptoposter")

    # CLI flags are inferred from examples in HN/Reddit; adjust to exact script args if needed.[web:32][web:19]
    cmd = [
        "python",
        "create_map_poster.py",
        "--city", request.location,
        "--country", "",  # can be blank if script supports city-only
        "--output", str(output_path),
    ]

    if request.zoom is not None:
        cmd += ["--zoom", str(request.zoom)]
    if request.width is not None:
        cmd += ["--width", str(request.width)]
    if request.height is not None:
        cmd += ["--height", str(request.height)]

    result = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Generation failed: {result.stderr}")

    return output_path

@app.post("/generate")
async def generate_map(request: MapRequest, background_tasks: BackgroundTasks):
    """
    Generate map poster with defaults but allow override.
    Returns where the poster will be written.
    """
    def task():
        _run_generation(request)

    background_tasks.add_task(task)
    out = _build_output_path(request.location, request.style, request.output_format)
    return {
        "message": "generation started",
        "location": request.location,
        "style": request.style,
        "output_path": str(out),
    }

@app.get("/generate/{location}/{style}")
async def generate_map_get(
    location: str,
    style: str,
    zoom: Optional[int] = 11,
    width: Optional[int] = 1200,
    height: Optional[int] = 800,
):
    """Simple GET wrapper with defaults."""
    req = MapRequest(
        location=location,
        style=style,
        zoom=zoom,
        width=width,
        height=height,
    )
    return await generate_map(req, BackgroundTasks())
