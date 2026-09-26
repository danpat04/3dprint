"""STEP → STL 변환과 캐시.

브라우저가 three.js 로 직접 렌더하려면 메시가 필요하다. exports/ 의 STEP 을
STL 로 바꿔 캐시에 둔다.

**캐시는 models/ 밖에 둔다.** models/ 는 사람이 관리하는 소스 트리이고
git 에 걸려 있다. 파생물이 섞이면 지저분해진다.

변환은 STEP 이 STL 보다 새로울 때만 한다.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

CACHE_DIR = Path(os.environ.get("CACHE_DIR", "/app/cache"))

# OCC 는 스레드 안전하지 않다. 변환을 직렬화한다.
_lock = threading.Lock()


def _cache_path(slug: str, name: str) -> Path:
    return CACHE_DIR / slug / f"{name}.stl"


def stl_for(step: Path, slug: str, name: str) -> Path:
    """STEP 에 대응하는 STL 경로. 필요하면 변환한다."""
    out = _cache_path(slug, name)
    if out.is_file() and out.stat().st_mtime >= step.stat().st_mtime:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    with _lock:
        # 락을 잡는 사이 다른 요청이 만들었을 수 있다
        if out.is_file() and out.stat().st_mtime >= step.stat().st_mtime:
            return out
        from build123d import export_stl, import_step

        shape = import_step(str(step))
        tmp = out.with_suffix(".stl.tmp")
        export_stl(shape, str(tmp), tolerance=0.05, angular_tolerance=0.2)
        tmp.replace(out)
    return out
