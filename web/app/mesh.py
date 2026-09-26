"""STEP → STL 변환과 캐시.

조립품 STEP 은 솔리드가 여럿이다 (드라이어 걸이 assembly = 리브2 + 커넥터 + 보).
하나로 합쳐 단색으로 그리면 어느 조각이 어디인지 안 보이므로 **솔리드별로 쪼개**
저장하고, 화면에서 색을 달리해 그린다.

한 번 변환할 때 전부 만든다. 요청마다 STEP 을 다시 읽으면 낭비다.

**캐시는 models/ 밖에 둔다.** models/ 는 사람이 관리하고 git 에 걸린 소스 트리다.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

CACHE_DIR = Path(os.environ.get("CACHE_DIR", "/app/cache"))
# 이보다 많으면 나누지 않고 통째로 본다. name_tag 는 양각 글자의 자모가 전부
# 개별 솔리드라 42 개가 나오는데, 42 가지 색으로 칠하면 오히려 난잡하다.
MAX_SOLIDS = 12

# 변환 규칙이 바뀌면 기존 캐시가 낡는다. 이 값을 올리면 전부 다시 만든다.
CACHE_VERSION = 2

# OCC 는 스레드 안전하지 않다. 변환을 직렬화한다.
_lock = threading.Lock()


def _dir(slug: str, name: str) -> Path:
    return CACHE_DIR / slug / name


def _fresh(d: Path, step: Path) -> dict | None:
    man = d / "manifest.json"
    if not (man.is_file() and man.stat().st_mtime >= step.stat().st_mtime):
        return None
    try:
        data = json.loads(man.read_text())
    except json.JSONDecodeError:
        return None
    return data if data.get("v") == CACHE_VERSION else None


def build(step: Path, slug: str, name: str) -> dict:
    """STEP 을 솔리드별 STL 로 변환(필요 시)하고 매니페스트를 돌려준다."""
    d = _dir(slug, name)
    cached = _fresh(d, step)
    if cached is not None:
        return cached

    with _lock:
        cached = _fresh(d, step)          # 락 대기 중 누가 만들었을 수 있다
        if cached is not None:
            return cached

        from build123d import export_stl, import_step

        shape = import_step(str(step))
        solids = shape.solids()
        # 조각이 지나치게 많으면(양각 글자 등) 나누는 의미가 없다
        parts = list(solids) if 1 < len(solids) <= MAX_SOLIDS else [shape]

        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.stl"):
            old.unlink()

        entries = []
        for i, s in enumerate(parts):
            out = d / f"{i}.stl"
            export_stl(s, str(out), tolerance=0.05, angular_tolerance=0.2)
            bb = s.bounding_box()
            entries.append({
                "index": i,
                "volume": round(s.volume / 1000, 2),          # cm3
                "size": [round(bb.size.X, 1), round(bb.size.Y, 1),
                         round(bb.size.Z, 1)],
            })
        # 큰 것부터 — 목록에서 본체가 위로 온다
        entries.sort(key=lambda e: -e["volume"])
        manifest = {"v": CACHE_VERSION, "count": len(entries), "solids": entries}
        (d / "manifest.json").write_text(json.dumps(manifest))
        return manifest


def stl_path(slug: str, name: str, index: int) -> Path:
    return _dir(slug, name) / f"{index}.stl"
