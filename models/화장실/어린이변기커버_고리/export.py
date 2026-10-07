"""어린이변기커버_고리 — 부품별 STEP export.

    uv run python -m models.화장실.어린이변기커버_고리.export

  exports/ring_plate.step  고리판 — 1개
  exports/base_plate.step  받침판 — 1개
  exports/pin.step         관통 핀 — 1개 (**이미 눕혀서** 내보낸다. 여벌 1~2개 권장)
  exports/lid.step         마감 뚜껑 — 1개 (기능 없음, 받침판 구조를 가린다)
  exports/assembly.step    조립 확인용 (출력물 아님)

출력 방향 — **힘 받는 방향과 맞춘다** (전부 서포트 불필요):

  고리판   판 면을 bed 에. 후크 → 고리 → 목 → 원반 으로 힘이 **판 면 안쪽**을
           흐르므로 압출선이 그대로 받는다. 세워 뽑으면 목의 인장이 층 사이를
           가로질러 가장 약한 방향이 된다.
  받침판   **카운터보어가 위로** (커버에 닿는 평평한 면을 bed 에).
           구멍이 6.5 → 8.8 로 **넓어지며** 올라가 오버행이 없다.
  핀       **눕혀서** — pin.step 이 이미 그 방향이다. 그대로 bed 에 앉히면 된다.
           갈래가 휠 때의 인장이 축 방향인데, 세워 뽑으면 그게 층을 가로질러
           부러진다(초판에서 실제로 부러졌다). 눕히면 압출선을 따라 흐른다.
           단면이 45도 모따기된 각기둥이라 옆면이 수직, 바닥이 자기지지다.

슬라이서: 벽 3 이상, 레이어 0.2, 서포트 끄기, 브림 불필요.
재료: PETG. PLA 는 항복이 ~2% 라 갈래 변형률 1.96% 에 바짝 붙는다.
"""

from pathlib import Path

from build123d import export_step

from models.화장실.어린이변기커버_고리.hook import (
    build_assembly,
    build_base_plate,
    build_lid,
    build_pin_print,
    build_ring_plate,
)

EXPORTS = Path(__file__).parent / "exports"

PARTS = {
    "ring_plate": (build_ring_plate, 1),
    "base_plate": (build_base_plate, 1),
    "pin": (build_pin_print, 1),
    "lid": (build_lid, 1),
    "assembly": (lambda: build_assembly(with_cover=False), 0),
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
        print(f"  {path.name:<18} {bb.size.X:6.1f} × {bb.size.Y:6.1f} × {bb.size.Z:6.1f}"
              f"   PETG {g:5.1f} g  {note}")
    print(f"\n출력 합계: PETG 약 {total:.1f} g")
