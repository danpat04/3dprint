"""web v2 — 프로젝트 중심 모델링 도구.

3d.danp.at/v2 에 붙는다. Caddy 가 `/v2/*` 를 이 서버로 넘기고,
FastAPI 는 root_path="/v2" 로 URL 을 생성한다.

**인증 코드가 없다.** Caddy 의 forward_auth + oauth2-proxy 가 앞단에서 걸러내고,
통과된 요청에 사용자 이메일을 헤더로 붙여준다.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app import projects as P

STATIC_DIR = Path(__file__).resolve().parent / "static"
ROOT_PATH = os.environ.get("ROOT_PATH", "/v2")

app = FastAPI(title="modeling v2", root_path=ROOT_PATH, docs_url=None, redoc_url=None)


def current_user(request: Request) -> str | None:
    """oauth2-proxy 가 붙여준 이메일. 로컬 개발 시엔 없을 수 있다."""
    return request.headers.get("X-Auth-Request-Email")


@app.get("/api/me")
def api_me(request: Request):
    return {"email": current_user(request)}


@app.get("/api/projects")
def api_projects():
    """최근 변경 순 프로젝트 목록."""
    return [p.as_dict() for p in P.iter_projects()]


@app.get("/api/projects/{slug:path}")
def api_project(slug: str):
    """프로젝트 상세 — 파트 목록 + export 파일."""
    project = P.get_project(slug)
    if project is None:
        raise HTTPException(404, "project not found")
    return {
        **project.as_dict(),
        "parts": [vars(x) for x in P.list_parts(project)],
        "artifacts": P.list_artifacts(project),
        "images": sorted(
            p.name for p in (project.path / "images").glob("*.png")
        ) if (project.path / "images").is_dir() else [],
    }


@app.get("/dl/{slug:path}")
def download(slug: str):
    """exports/ 파일 다운로드. slug 는 `<project>/<filename>` 형태."""
    head, _, filename = slug.rpartition("/")
    project = P.get_project(head)
    if project is None or not filename or "/" in filename or filename.startswith("."):
        raise HTTPException(404, "not found")
    target = (project.path / "exports" / filename).resolve()
    if (project.path / "exports").resolve() not in target.parents \
            or not target.is_file() \
            or target.suffix.lower() not in P._ARTIFACT_SUFFIX:
        raise HTTPException(404, "not found")
    return FileResponse(target, filename=filename,
                        media_type="application/octet-stream")


@app.get("/img/{slug:path}")
def image(slug: str):
    """images/ PNG."""
    head, _, filename = slug.rpartition("/")
    project = P.get_project(head)
    if project is None or not filename.endswith(".png") or "/" in filename:
        raise HTTPException(404, "not found")
    target = (project.path / "images" / filename).resolve()
    if (project.path / "images").resolve() not in target.parents or not target.is_file():
        raise HTTPException(404, "not found")
    return FileResponse(target, media_type="image/png")


@app.get("/health")
def health():
    return {"ok": True, "projects": len(P.iter_projects())}


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
