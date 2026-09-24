"""flair58_splash_guard — 부품별 STEP export.

    uv run python -m models.coffee.flair58_splash_guard.export

  exports/left.step      사용자 기준 왼쪽 — 전원선 홈 + 그루브
  exports/right.step     사용자 기준 오른쪽 — 텅
  exports/assembly.step  조립 상태 (배치 확인용, 출력용 아님)

출력은 left/right 를 **각각 세워서** (모델 좌표 그대로) 올리면 된다.
서포트 불필요, 브림 권장.
"""

from pathlib import Path

from build123d import export_step

from models.coffee.flair58_splash_guard.guard import (
    build_assembly,
    build_left,
    build_right,
)

EXPORTS = Path(__file__).parent / "exports"

PARTS = {
    "left": build_left,
    "right": build_right,
    "assembly": build_assembly,
}

if __name__ == "__main__":
    EXPORTS.mkdir(exist_ok=True)
    for name, fn in PARTS.items():
        part = fn()
        path = EXPORTS / f"{name}.step"
        export_step(part, str(path))
        bb = part.bounding_box()
        print(f"  {path.name:<16} {bb.size.X:6.1f} x {bb.size.Y:6.1f} x {bb.size.Z:6.1f}"
              f"  PETG {part.volume * 1.27e-3:5.0f} g")
