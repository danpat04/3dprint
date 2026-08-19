"""modular_rack — 부품별 STEP export.

  frame.step        틀 (사용 방향 그대로 출력)
  hook.step         S후크 (3개 출력, 옆으로 뉘여서)
  bin_1u.step 등    통 1/2/3유닛 (세워서 출력) — 높이는 기본 80,
                    용도별 통이 정해지면 build_bin(units, height) 로 개별 생성
"""

from pathlib import Path

from build123d import export_step

from models.camping.modular_rack.basket import build_basket
from models.camping.modular_rack.bin import build_bin
from models.camping.modular_rack.frame import build_frame
from models.camping.modular_rack.hook import build_hook

EXPORTS = Path(__file__).parent / "exports"

parts = {
    "frame": build_frame(),
    "hook": build_hook(),
    "bin_1u": build_bin(1, 80.0),
    "bin_2u": build_bin(2, 80.0),
    "bin_3u": build_bin(3, 80.0),
    "basket_1u": build_basket(1, 160.0),
    "basket_2u": build_basket(2, 160.0),
}

if __name__ == "__main__":
    EXPORTS.mkdir(exist_ok=True)
    for name, part in parts.items():
        path = EXPORTS / f"{name}.step"
        export_step(part, str(path))
        print(f"exported: {path}")
