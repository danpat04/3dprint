"""피드백 · 드래프트 저장.

v1 에서는 업로드할 때 프로젝트를 **드롭다운에서 골라야** 했고, 백지 스케치는
`models/_drafts/<이름>/` 로 따로 빠져 어느 프로젝트 얘기인지 알 수 없었다.
(실제로 `joint` 드래프트를 찾아 헤매고 refs/ 로 손수 옮겨야 했다.)

v2 는 프로젝트 페이지에서 올리므로 **프로젝트·파트가 URL 에 이미 있다.**
고를 필요도, 나중에 옮길 필요도 없다.

  피드백 (렌더 위 덧그림) → models/<project>/feedback/   (gitignore)
  드래프트 (백지 스케치)   → models/<project>/refs/       (git 추적)

드래프트를 refs/ 로 보내는 건 실제 쓰임 때문이다 — 백지 스케치는 설계 입력이라
결국 refs/ 로 옮겨 보관하게 된다. 처음부터 거기 두면 옮기는 단계가 사라진다.
"""

from __future__ import annotations

import base64
import re
import uuid
from datetime import datetime
from pathlib import Path

from app.projects import Project

_DATAURL = re.compile(r"^data:image/png;base64,(.+)$", re.DOTALL)
_SAFE = re.compile(r"[^\w가-힣.-]+")

# 3D 뷰 캡처 임시 보관 (그리기 페이지로 넘기는 용도)
_captures: dict[str, bytes] = {}
_CAPTURE_MAX = 20


def decode_png(data_url: str) -> bytes:
    m = _DATAURL.match(data_url or "")
    if not m:
        raise ValueError("PNG data URL 이 아닙니다")
    return base64.b64decode(m.group(1))


def put_capture(png: bytes) -> str:
    cap_id = uuid.uuid4().hex[:12]
    _captures[cap_id] = png
    while len(_captures) > _CAPTURE_MAX:
        _captures.pop(next(iter(_captures)))
    return cap_id


def get_capture(cap_id: str) -> bytes | None:
    return _captures.get(cap_id)


def _stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_feedback(project: Project, png: bytes, note: str, part: str | None) -> str:
    """렌더 위 덧그림. 어느 파트를 보고 그린 건지 파일명에 남긴다."""
    out_dir = project.path / "feedback"
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{_SAFE.sub('_', part)}" if part else ""
    base = f"{_stamp()}{suffix}"
    (out_dir / f"{base}.png").write_bytes(png)
    if note.strip():
        (out_dir / f"{base}.txt").write_text(note.strip(), encoding="utf-8")
    return f"{project.slug}/feedback/{base}.png"


def save_draft(project: Project, png: bytes, note: str, name: str) -> str:
    """백지 스케치 → refs/. 설계 입력이라 git 에 남는다."""
    out_dir = project.path / "refs"
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = _SAFE.sub("_", name.strip()) or "sketch"
    base = f"{stem}_{_stamp()}"
    (out_dir / f"{base}.png").write_bytes(png)
    if note.strip():
        (out_dir / f"{base}.txt").write_text(note.strip(), encoding="utf-8")
    return f"{project.slug}/refs/{base}.png"
