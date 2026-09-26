"""web v2 — 프로젝트 중심 모델링 도구.

3d.danp.at/v2 에 붙는다. Caddy 가 `handle_path /v2/*` 로 **접두사를 떼고** 넘기므로
앱은 `/` 기준으로 동작한다.

`root_path` 는 쓰지 않는다. 일반 라우트는 경로를 그대로 매칭하지만 **마운트
(StaticFiles)는 root_path 를 먼저 떼어내서**, Caddy 가 이미 뗀 경로를 한 번 더 떼려다
정적 파일만 404 가 난다. 문서(OpenAPI)를 끈 상태라 root_path 가 필요 없고,
HTML 도 전부 상대 경로를 쓴다.

**인증 코드가 없다.** Caddy 의 forward_auth + oauth2-proxy 가 앞단에서 걸러내고,
통과된 요청에 사용자 이메일을 헤더로 붙여준다.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app import build, mesh, projects as P

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="modeling v2", docs_url=None, redoc_url=None)


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
        "parts": [{**{k: v for k, v in vars(x).items() if not k.startswith("_")},
                   "buildable": x.command is not None}
                  for x in P.list_parts(project)],
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


@app.get("/mesh/{slug:path}")
def mesh_stl(slug: str):
    """파트의 STL. exports/ 의 STEP 을 변환해 캐시에서 돌려준다.

    slug 는 `<project>/<part>` 형태. 아직 export 된 적 없는 파트는 404 —
    프런트가 "빌드 필요" 로 표시한다.
    """
    head, _, part = slug.rpartition("/")
    project = P.get_project(head)
    if project is None or not part or "/" in part or part.startswith("."):
        raise HTTPException(404, "not found")
    step = project.path / "exports" / f"{part}.step"
    if not step.is_file():
        raise HTTPException(404, "not exported yet")
    try:
        out = mesh.stl_for(step, project.slug, part)
    except Exception as exc:                      # 변환 실패를 그대로 노출
        raise HTTPException(500, f"mesh failed: {exc}") from exc
    return FileResponse(out, media_type="model/stl")


@app.on_event("startup")
async def _startup():
    build.start()


def _find_part(slug: str, part: str):
    project = P.get_project(slug)
    if project is None:
        raise HTTPException(404, "project not found")
    for p in P.list_parts(project):
        if p.name == part:
            return project, p
    raise HTTPException(404, "part not found")


@app.post("/build/{slug:path}")
def build_part(slug: str):
    """파트 빌드 요청. slug 는 `<project>/<part>`."""
    head, _, part = slug.rpartition("/")
    project, p = _find_part(head, part)
    cmd = p.command
    if cmd is None:
        raise HTTPException(400, "이 파트는 빌드할 방법이 없습니다 (소스 없음)")
    return build.submit(project.slug, p.name, cmd).as_dict()


@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    job = build.get(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    return job.as_dict()


@app.get("/jobs")
def jobs(slug: str | None = None):
    return build.recent(slug)


@app.get("/health")
def health():
    return {"ok": True, "projects": len(P.iter_projects())}


# 브라우저가 볼 때의 앱 루트. Caddy 가 /v2 접두사를 떼고 넘기므로 앱은 모르고,
# 상대 경로가 /p/<a>/<b> 같은 깊은 URL 에서 깨지지 않도록 <base> 로 못박는다.
BASE_HREF = os.environ.get("BASE_HREF", "/v2/")


def _page(name: str) -> str:
    return (STATIC_DIR / name).read_text(encoding="utf-8").replace("__BASE__", BASE_HREF)


@app.get("/", response_class=HTMLResponse)
def index():
    return _page("index.html")


@app.get("/p/{slug:path}", response_class=HTMLResponse)
def project_page(slug: str):
    project = P.get_project(slug)
    if project is None:
        raise HTTPException(404, "project not found")
    html = _page("project.html")
    return html.replace("<body class=\"proj\">",
                        f"<body class=\"proj\" data-slug=\"{project.slug}\">")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
