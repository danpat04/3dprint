"""feedback_tool 업로드 서버.

ocp_vscode 뷰어(3939) 앞단의 Caddy 가 `/feedback/*` 를 이 서버(3940)로 보낸다.
같은 도메인(same-origin)이라 CORS 불필요.

엔드포인트:
  GET  /feedback/inject.js   캡처 버튼 스크립트 (뷰어 HTML 에서 로드)
  GET  /feedback/projects    models/ 하위 프로젝트 목록 (드롭다운용)
  POST /feedback/upload      덧그림 PNG + 메모 저장 → models/<project>/feedback/
  GET  /feedback/health      헬스체크
  GET  /draw                 Excalidraw 드로잉 페이지 (백지 제안 + 캡처 덧그림)
  POST /feedback/capture     뷰어 캡처 PNG 임시 저장 → id (draw?bg=<id> 로 전달)
  GET  /feedback/capture/{id}  임시 캡처 PNG 조회
  POST /feedback/draft       백지 스케치 저장 → models/_drafts/<이름>/
"""

from __future__ import annotations

import base64
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel

MODELS_DIR = Path("/app/models")
STATIC_DIR = Path(__file__).resolve().parent / "static"
# models/ 에서 프로젝트로 보지 않을 항목
_HIDDEN = {"__pycache__"}
_DATAURL_RE = re.compile(r"^data:image/png;base64,(.+)$", re.DOTALL)

app = FastAPI(title="modeling feedback tool")

# 가장 최근에 뷰어로 push 된 프로젝트. finalize_iteration() 이 통지한다.
# 단일 워커라 메모리 변수로 충분 (서버 재시작 시 다음 push 때 다시 채워짐).
_current_project: str | None = None


def _is_project(p: Path) -> bool:
    """모델 코드(.py)가 직접 들어 있으면 프로젝트, 아니면 카테고리로 본다."""
    return any(p.glob("*.py"))


def _list_projects() -> list[str]:
    """평면 + 카테고리 1단계 하위 프로젝트 ("camping/modular_rack" 형태)."""
    if not MODELS_DIR.exists():
        return []
    names: list[str] = []
    for p in MODELS_DIR.iterdir():
        if not p.is_dir() or p.name.startswith("_") or p.name in _HIDDEN:
            continue
        if _is_project(p):
            names.append(p.name)
        else:  # 카테고리 → 한 단계 더
            for q in p.iterdir():
                if q.is_dir() and not q.name.startswith("_") and _is_project(q):
                    names.append(f"{p.name}/{q.name}")
    return sorted(names)


def _resolve_project(project: str) -> Path:
    # path traversal 방지: "이름" 또는 "카테고리/이름"만 허용, 실제 디렉토리 확인
    if (
        not project
        or "\\" in project
        or project.count("/") > 1
        or any(seg.startswith(".") or not seg for seg in project.split("/"))
    ):
        raise HTTPException(400, "invalid project name")
    target = (MODELS_DIR / project).resolve()
    if MODELS_DIR.resolve() not in target.parents or not target.is_dir():
        raise HTTPException(404, "project not found")
    return target


class UploadBody(BaseModel):
    project: str
    image: str          # data:image/png;base64,...
    note: str = ""


class CurrentBody(BaseModel):
    project: str


class CaptureBody(BaseModel):
    image: str          # data:image/png;base64,...


class DraftBody(BaseModel):
    name: str           # 스케치 이름 (snake_case) → models/_drafts/<name>/
    image: str
    note: str = ""


def _decode_png(data_url: str) -> bytes:
    m = _DATAURL_RE.match(data_url.strip())
    if not m:
        raise HTTPException(400, "image must be a PNG data URL")
    try:
        return base64.b64decode(m.group(1))
    except Exception:
        raise HTTPException(400, "invalid base64 image")


def _timestamp_stem(target_dir: Path) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    stem, n = ts, 1
    while (target_dir / f"{stem}.png").exists():
        n += 1
        stem = f"{ts}_{n}"
    return stem


@app.post("/feedback/current")
def set_current(body: CurrentBody):
    """finalize_iteration() 이 모델을 뷰어로 push 할 때 호출 → 현재 프로젝트 등록."""
    global _current_project
    name = body.project.strip()
    _resolve_project(name)  # 검증 (실패 시 400/404)
    _current_project = name
    return {"ok": True, "project": name}


@app.get("/feedback/current")
def get_current():
    """inject.js 가 캡처 시 현재 프로젝트를 자동 선택하려고 조회."""
    return {"project": _current_project}


@app.get("/feedback/health")
def health():
    return {"ok": True, "models_dir": str(MODELS_DIR), "exists": MODELS_DIR.exists()}


@app.get("/feedback/inject.js")
def inject_js():
    return FileResponse(
        STATIC_DIR / "inject.js",
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/feedback/projects")
def projects():
    return {"projects": _list_projects()}


@app.post("/feedback/upload")
def upload(body: UploadBody):
    project_dir = _resolve_project(body.project)
    png = _decode_png(body.image)

    fb_dir = project_dir / "feedback"
    fb_dir.mkdir(exist_ok=True)
    stem = _timestamp_stem(fb_dir)
    png_path = fb_dir / f"{stem}.png"
    png_path.write_bytes(png)

    note = body.note.strip()
    if note:
        (fb_dir / f"{stem}.txt").write_text(note + "\n", encoding="utf-8")

    rel = png_path.relative_to(MODELS_DIR.parent) if MODELS_DIR.parent in png_path.parents else png_path
    return JSONResponse({"ok": True, "path": str(rel), "note_saved": bool(note)})


# ---------- Excalidraw 드로잉 페이지 (/draw) ----------

# 뷰어 캡처 임시 보관: id → PNG bytes. 단일 워커 메모리로 충분, 최근 것만 유지.
_captures: dict[str, bytes] = {}
_CAPTURE_LIMIT = 20
_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


@app.get("/draw")
def draw_page():
    return FileResponse(
        STATIC_DIR / "draw.html",
        media_type="text/html",
        headers={"Cache-Control": "no-cache"},
    )


@app.post("/feedback/capture")
def capture(body: CaptureBody):
    png = _decode_png(body.image)
    cap_id = datetime.now(timezone.utc).strftime("%H%M%S%f")
    _captures[cap_id] = png
    while len(_captures) > _CAPTURE_LIMIT:
        _captures.pop(next(iter(_captures)))
    return {"ok": True, "id": cap_id}


@app.get("/feedback/capture/{cap_id}")
def get_capture(cap_id: str):
    png = _captures.get(cap_id)
    if png is None:
        raise HTTPException(404, "capture not found (expired?)")
    return Response(png, media_type="image/png")


@app.post("/feedback/draft")
def draft(body: DraftBody):
    name = body.name.strip().lower().replace(" ", "_")
    if not _NAME_RE.match(name):
        raise HTTPException(400, "이름은 영소문자/숫자/_/- 만 가능합니다")
    png = _decode_png(body.image)

    d_dir = MODELS_DIR / "_drafts" / name
    d_dir.mkdir(parents=True, exist_ok=True)
    stem = _timestamp_stem(d_dir)
    (d_dir / f"{stem}.png").write_bytes(png)
    note = body.note.strip()
    if note:
        (d_dir / f"{stem}.txt").write_text(note + "\n", encoding="utf-8")

    rel = (d_dir / f"{stem}.png").relative_to(MODELS_DIR.parent)
    return JSONResponse({"ok": True, "path": str(rel), "note_saved": bool(note)})
