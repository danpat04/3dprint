"""레고_코인 — 부품별 STEP export.

    uv run python -m models.장난감.레고_코인.export

  exports/coin.step           실제 출력물. 필요한 개수만큼 슬라이서에서 복제한다

숫자 없는 민짜 코인. 속에 묻은 숫자는 실제 출력에서 안 보여 뺐다(README).

출력: 면을 bed 에 놓고 눕힌다. 앞뒤가 평평하고 테두리가 수직이라 서포트가
없다.
재료: 투명 PLA.
"""

from pathlib import Path

from build123d import export_step

from models.장난감.레고_코인.coin import build_coin

EXPORTS = Path(__file__).parent / "exports"


PARTS = {
    "coin": (lambda: build_coin(None), 1),
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
