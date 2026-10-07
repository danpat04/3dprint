"""식기세척기관_싱크대커버 — 부품별 STEP export.

    uv run python -m models.주방.식기세척기관_싱크대커버.export

  exports/cover.step     커버 (상판 위) — 1개
  exports/nut.step       너트 (상판 아래) — 1개
  exports/assembly.step  조립 확인용 (출력물 아님)

출력 방향:
  cover  **칼라를 아래로** (조립 자세 그대로). 브림 8mm 이상 — 접지가 칼라 끝
         링 78mm² 뿐이다. 서포트는 플랜지 아랫면 턱과 엘보 θ45~60° 구간(5.8mm).
         "빌드플레이트 위에만" 으로 두면 보어 안에는 안 들어간다.
         이음 모따기는 45° 라 자기지지. 엘리펀트 풋 보정 필요
  nut    바닥을 bed 에. 나사산이 수직이라 오버행 없음

재료: PETG. 배수가 뜨거운 물이고(Tg 80도) 습한 자리다. PLA 는 Tg 60도라 부적합.
오링: **내경 38 × 굵기 3.5 실리콘** (보유품). 홈이 그 치수로 파여 있다.
"""

from pathlib import Path

from build123d import export_step

from models.주방.식기세척기관_싱크대커버.cover import (
    build_assembly,
    build_cover,
    build_nut,
)

EXPORTS = Path(__file__).parent / "exports"

PARTS = {
    "cover": (build_cover, 1),
    "nut": (build_nut, 1),
    "assembly": (lambda: build_assembly(with_deck=False), 0),
}

if __name__ == "__main__":
    EXPORTS.mkdir(exist_ok=True)
    total = 0.0
    for name, (fn, qty) in PARTS.items():
        part = fn()
        path = EXPORTS / f"{name}.step"
        export_step(part, str(path))
        g = part.volume * 1.27e-3
        if qty:
            total += g * qty
        bb = part.bounding_box()
        note = f"× {qty}" if qty else "(조립 확인용)"
        print(f"  {path.name:<16} {bb.size.X:6.1f} × {bb.size.Y:6.1f} × {bb.size.Z:6.1f}"
              f"   PETG {g:5.1f} g  {note}")
    print(f"\n출력 합계: PETG 약 {total:.1f} g")
