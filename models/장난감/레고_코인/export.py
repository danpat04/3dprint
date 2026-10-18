"""레고_코인 — 부품별 STEP export.

    uv run python -m models.장난감.레고_코인.export

  exports/coin_1.step         실제 출력물. 필요한 개수만큼 슬라이서에서 복제한다

속에 묻힌 숫자는 3d.danp.at 뷰어의 **「투명」** 버튼으로 본다.
자른 모델을 따로 내보낼 필요가 없다.

출력: 면을 bed 에 놓고 눕힌다. 앞뒤가 평평하고 테두리가 수직이라 서포트가
없고, 공동 위는 글자 획 폭(2mm 안팎)만 브리지하면 된다.
재료: 투명 PLA. 코인 하나 약 1.4 g.
"""

from pathlib import Path

from build123d import export_step

from models.장난감.레고_코인.coin import build_coin

EXPORTS = Path(__file__).parent / "exports"


PARTS = {
    "coin_1": (lambda: build_coin("1"), 1),
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
        note = f"× {qty}"
        print(f"  {path.name:<18} {bb.size.X:6.1f} × {bb.size.Y:5.1f} × {bb.size.Z:4.1f}"
              f"   PLA {g:5.2f} g  {note}")
    print(f"\n코인 하나당 약 1.4 g")
