"""식기세척기관_싱크대커버 — 부품별 STEP export.

    uv run python -m models.주방.식기세척기관_싱크대커버.export

  exports/cover.step     커버 (상판 위) — 1개
  exports/nut.step       너트 (상판 아래) — 1개
  exports/assembly.step  조립 확인용 (출력물 아님)

출력 방향:
  cover  플랜지를 bed 에. 엘보가 60도까지 꺾이므로 **45도를 넘는 구간에
         서포트가 필요하다** — 엘보 바깥 아랫면과 보어 천장 양쪽이다.
         보어가 ⌀33 이라 안쪽 서포트도 손이 들어간다.
         꺾임을 45도로 줄이면 서포트 없이 뽑을 수 있다 (높이도 32.6 으로 낮아짐)
  nut    바닥을 bed 에. 나사산이 수직이라 오버행 없음

재료: PETG. 배수가 뜨거운 물이고(Tg 80도) 습한 자리다. PLA 는 Tg 60도라 부적합.
오링: **내경 35 × 굵기 2.5 실리콘**. 홈이 그 치수로 파여 있다.
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
