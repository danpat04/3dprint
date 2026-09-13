"""name_tag — 부품별 / 합본 STEP export.

    uv run python -m models.name_tag.export             # model.py 의 기본 TEXT
    uv run python -m models.name_tag.export "홍길동"     # 글자 지정
    uv run python -m models.name_tag.export "A" "B" "C"  # 여러 개 한 번에

생성물 (글자마다):
    exports/<글자>.step         판 + 글자 2-바디 컴파운드 — 슬라이서엔 이것만 넣으면 됨
    exports/<글자>_plate.step   판만
    exports/<글자>_text.step    양각 글자만
"""

import re
import sys
from pathlib import Path

from build123d import export_step

from models.name_tag.model import TEXT, build_plate, build_tag, build_text, tag_size

EXPORTS = Path(__file__).parent / "exports"

_UNSAFE = re.compile(r'[^\w가-힣.-]+')


def slug(text: str) -> str:
    """파일명용 — 공백/특수문자를 _ 로. 한글은 그대로 둔다."""
    return _UNSAFE.sub("_", text.strip()) or "tag"


def export_tag(text: str) -> None:
    name = slug(text)
    w, h = tag_size(text)
    for suffix, part in (
        ("", build_tag(text)),
        ("_plate", build_plate(text)),
        ("_text", build_text(text)),
    ):
        path = EXPORTS / f"{name}{suffix}.step"
        export_step(part, str(path))
        print(f"  {path.name}")
    print(f"'{text}' → 판 {w:.1f} × {h:.1f}mm")


if __name__ == "__main__":
    EXPORTS.mkdir(exist_ok=True)
    for t in (sys.argv[1:] or [TEXT]):
        export_tag(t)
