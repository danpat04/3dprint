"""프로젝트/파트 탐색.

models/ 아래를 훑어 프로젝트와 그 안의 "모델링(파트)" 목록을 만든다.

**코드를 실행하지 않는다.** 탐색하려고 export.py 를 import 하면 그 자체가
임의 코드 실행이 된다. AST 로 파싱해 딕셔너리 키만 읽는다.

파트 규약이 프로젝트마다 다르므로 폴백 사슬로 흡수한다:
  1. export.py 의 PARTS / parts 딕셔너리 키        (flair58, dyson, shrimp_scoop …)
  2. 실행하면 모델을 만드는 .py 모듈 — **두 형태를 모두 잡는다**:
       - `if __name__ == "__main__":` 가드가 있는 것        (신형)
       - 가드 없이 모듈 최상위에서 finalize_iteration() 호출  (구형, models/CLAUDE.md 예시)
  3. 위 둘이 비면 exports/ 의 STEP 파일 이름
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

MODELS_DIR = Path(os.environ.get("MODELS_DIR", "/app/models"))

# 프로젝트로 보지 않을 디렉토리
_SKIP = {"__pycache__", "_lib", "_drafts", "_assets"}
_SRC_SUFFIX = {".py", ".md"}
_ARTIFACT_SUFFIX = {".step", ".stl", ".3mf"}


def _mtime(p: Path) -> datetime:
    return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)


@dataclass
class Part:
    name: str
    source: str                  # 어떤 규약으로 찾았는지 (진단용)
    module: str | None = None    # 실행 가능한 모듈 경로 (있으면)
    artifact: str | None = None  # exports/ 안 파일명 (있으면)


@dataclass
class Project:
    slug: str                    # "coffee/tamper_stand" 같은 models/ 기준 상대경로
    name: str
    category: str | None
    path: Path = field(repr=False)
    updated: datetime | None = None
    title: str | None = None     # README 첫 h1

    def as_dict(self) -> dict:
        return {
            "slug": self.slug,
            "name": self.name,
            "category": self.category,
            "title": self.title,
            "updated": self.updated.isoformat() if self.updated else None,
        }


def _dict_keys_from_ast(src: str, names: set[str]) -> list[str]:
    """모듈 최상위에서 `names` 중 하나에 대입된 dict 의 문자열 키를 뽑는다."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        targets = {t.id for t in node.targets if isinstance(t, ast.Name)}
        if not (targets & names) or not isinstance(node.value, ast.Dict):
            continue
        return [k.value for k in node.value.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)]
    return []


def _is_runnable(src: str) -> bool:
    """실행하면 모델을 만드는 모듈인가.

    구형 프로젝트는 __main__ 가드 없이 최상위에서 finalize_iteration() 을 부른다
    (models/CLAUDE.md 의 예시가 그렇다). 가드만 보면 12 개 이상을 놓친다.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, ast.If) and "__main__" in ast.dump(node.test):
            return True
    return any(
        isinstance(n, ast.Call) and getattr(n.func, "id", None) == "finalize_iteration"
        for n in ast.walk(tree)
    )


def iter_projects() -> list[Project]:
    """models/ 아래 프로젝트 목록. 최근 변경 순."""
    if not MODELS_DIR.exists():
        return []
    found: list[Project] = []
    for d in sorted(MODELS_DIR.iterdir()):
        if not d.is_dir() or d.name in _SKIP or d.name.startswith("."):
            continue
        # 1단계: 바로 프로젝트인가 (.py 가 있으면)
        if any(p.suffix == ".py" for p in d.glob("*.py")):
            found.append(_load(d, category=None))
            continue
        # 2단계: 카테고리 디렉토리
        for sub in sorted(d.iterdir()):
            if sub.is_dir() and sub.name not in _SKIP and not sub.name.startswith("."):
                found.append(_load(sub, category=d.name))
    found.sort(key=lambda p: p.updated or datetime.min.replace(tzinfo=timezone.utc),
               reverse=True)
    return found


def _load(path: Path, category: str | None) -> Project:
    slug = path.relative_to(MODELS_DIR).as_posix()
    srcs = [p for p in path.iterdir()
            if p.is_file() and p.suffix in _SRC_SUFFIX]
    updated = max((_mtime(p) for p in srcs), default=None)
    title = None
    readme = path / "README.md"
    if readme.is_file():
        for line in readme.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    return Project(slug=slug, name=path.name, category=category,
                   path=path, updated=updated, title=title)


def get_project(slug: str) -> Project | None:
    """slug 로 프로젝트 조회. 경로 탈출 방지."""
    if not slug or "\\" in slug or any(
            seg in ("", ".", "..") or seg.startswith(".") for seg in slug.split("/")):
        return None
    if len(slug.split("/")) > 2:
        return None
    path = (MODELS_DIR / slug).resolve()
    if not path.is_dir() or MODELS_DIR.resolve() not in path.parents:
        return None
    parts = slug.split("/")
    return _load(path, category=parts[0] if len(parts) == 2 else None)


def list_parts(project: Project) -> list[Part]:
    """프로젝트의 모델링(파트) 목록. 폴백 사슬로 찾는다."""
    parts: list[Part] = []
    seen: set[str] = set()

    export_py = project.path / "export.py"
    if export_py.is_file():
        for key in _dict_keys_from_ast(
                export_py.read_text(encoding="utf-8"), {"PARTS", "parts"}):
            if key not in seen:
                seen.add(key)
                parts.append(Part(name=key, source="export.py"))

    for py in sorted(project.path.glob("*.py")):
        if py.name in ("export.py", "params.py", "__init__.py"):
            continue
        if not _is_runnable(py.read_text(encoding="utf-8")):
            continue
        name = py.stem
        if name not in seen:
            seen.add(name)
            mod = f"models.{project.slug.replace('/', '.')}.{name}"
            parts.append(Part(name=name, source="module", module=mod))

    exports = project.path / "exports"
    if exports.is_dir():
        by_stem = {p.stem: p.name for p in sorted(exports.iterdir())
                   if p.is_file() and p.suffix.lower() in _ARTIFACT_SUFFIX}
        for part in parts:
            if part.name in by_stem:
                part.artifact = by_stem[part.name]
        for stem, fname in by_stem.items():
            if stem not in seen:
                seen.add(stem)
                parts.append(Part(name=stem, source="exports", artifact=fname))

    return parts


def list_artifacts(project: Project) -> list[dict]:
    """exports/ 다운로드 목록. 시각은 UTC ISO 로 내보내고 표기는 브라우저에 맡긴다."""
    exports = project.path / "exports"
    if not exports.is_dir():
        return []
    out = []
    for p in sorted(exports.iterdir()):
        if p.is_file() and p.suffix.lower() in _ARTIFACT_SUFFIX:
            st = p.stat()
            out.append({
                "name": p.name,
                "size": st.st_size,
                "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
                         .isoformat(),
            })
    out.sort(key=lambda a: a["mtime"], reverse=True)
    return out
