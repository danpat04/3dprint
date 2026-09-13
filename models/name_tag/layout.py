"""name_tag — 여러 택을 한 판에 배치해서 렌더/출력.

    uv run python -m models.name_tag.layout                      # 기본 네 방향 세트
    uv run python -m models.name_tag.layout "앞" "뒤" "좌" "우"    # 글자 지정

글자 길이가 달라 판 가로는 제각각이지만, **왼쪽 정렬**해서 고리 구멍이 한 줄로
맞도록 배치한다. 출력 시 그대로 슬라이서에 올리면 된다.

색 분리는 낱개와 동일 — 모든 판의 윗면이 z=PLATE_T 로 같으므로
z=2.4 에 색 변경 한 번이면 전체 택의 글자가 같이 바뀐다.
"""

import sys
from pathlib import Path

from build123d import Compound, Location, export_step

from models._lib.iter import finalize_iteration
from models.name_tag.model import PLATE_T, build_plate, build_text, tag_size

TEXTS = ["앞 - 오른쪽", "앞 - 왼쪽", "뒤 - 오른쪽", "뒤 - 왼쪽"]
GAP_Y = 6.0        # 택 사이 간격


def build_layout(texts: list[str] = None, gap: float = GAP_Y):
    texts = texts or TEXTS
    bodies, y = [], 0.0
    for i, t in enumerate(texts):
        _, h = tag_size(t)
        loc = Location((0, y, 0))
        plate, letters = build_plate(t).moved(loc), build_text(t).moved(loc)
        plate.label, letters.label = f"{i}_plate", f"{i}_text"
        bodies += [plate, letters]
        y += h + gap
    return Compound(children=bodies)


def layout_size(texts: list[str] = None, gap: float = GAP_Y) -> tuple[float, float]:
    texts = texts or TEXTS
    sizes = [tag_size(t) for t in texts]
    return max(w for w, _ in sizes), sum(h for _, h in sizes) + gap * (len(sizes) - 1)


EXPORTS = Path(__file__).parent / "exports"
SET_NAME = "set_4way"     # 배치 전체를 담는 STEP 이름


if __name__ == "__main__":
    texts = sys.argv[1:] or TEXTS
    w, h = layout_size(texts)
    for t in texts:
        tw, th = tag_size(t)
        print(f"  {t:<12} {tw:5.1f} x {th:4.1f}")
    print(f"전체 배치: {w:.1f} x {h:.1f} x {PLATE_T:.1f}(+양각)")

    layout = build_layout(texts)

    EXPORTS.mkdir(exist_ok=True)
    path = EXPORTS / f"{SET_NAME}.step"
    export_step(layout, str(path))
    print(f"exported: {path}")

    finalize_iteration(layout)
