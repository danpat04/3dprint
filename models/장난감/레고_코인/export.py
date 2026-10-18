"""레고_코인 — 부품별 STEP export.

    uv run python -m models.장난감.레고_코인.export

  exports/coin_1,5,10.step    숫자안 — 실제 출력물
  exports/pip_1,3,5.step      점안 — 실제 출력물
  exports/cutaway_number.step 숫자안 속을 보려고 뚜껑(윗살 1.2)을 벗긴 것
  exports/cutaway_pips.step   점안 뚜껑 벗긴 것
  (cutaway 는 **출력물이 아니다.** 속에 뭐가 들었는지 보려고 만든 것)

출력: 면을 bed 에 놓고 눕힌다. 앞뒤가 평평하고 테두리가 수직이라 서포트가
없고, 공동 위는 글자 획 폭(2mm 안팎)만 브리지하면 된다.
재료: 투명 PLA. 코인 하나 약 1.4 g.
"""

from pathlib import Path

from build123d import Box, Compound, Location, export_step

from models.장난감.레고_코인.coin import VOID_TOP, build_coin, build_coin_pips

EXPORTS = Path(__file__).parent / "exports"
_LID = Box(40, 40, 20).moved(Location((0, 0, VOID_TOP + 10)))


def _row(parts, gap=19.0):
    out = []
    for i, (name, p) in enumerate(parts):
        q = p.moved(Location((i * gap, 0, 0)))
        q.label = name
        out.append(q)
    return Compound(children=out)


def cutaway_number():
    return _row([(s, build_coin(s) - _LID) for s in ("1", "5", "10")])


def cutaway_pips():
    return _row([("pip%d" % n, build_coin_pips(n) - _LID) for n in (1, 3, 5)])


PARTS = {
    "coin_1": (lambda: build_coin("1"), 1),
    "coin_5": (lambda: build_coin("5"), 1),
    "coin_10": (lambda: build_coin("10"), 1),
    "pip_1": (lambda: build_coin_pips(1), 1),
    "pip_3": (lambda: build_coin_pips(3), 1),
    "pip_5": (lambda: build_coin_pips(5), 1),
    "cutaway_number": (cutaway_number, 0),
    "cutaway_pips": (cutaway_pips, 0),
}

if __name__ == "__main__":
    EXPORTS.mkdir(exist_ok=True)
    total = 0.0
    for name, (fn, qty) in PARTS.items():
        part = fn()
        path = EXPORTS / f"{name}.step"
        export_step(part, str(path))
        g = part.volume * 1.24e-3
        if qty:
            total += g * qty
        bb = part.bounding_box()
        note = f"× {qty}" if qty else "(속 보기용, 출력물 아님)"
        print(f"  {path.name:<18} {bb.size.X:6.1f} × {bb.size.Y:5.1f} × {bb.size.Z:4.1f}"
              f"   PLA {g:5.2f} g  {note}")
    print(f"\n코인 하나당 약 1.4 g")
