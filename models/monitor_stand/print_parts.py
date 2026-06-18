"""print_parts — 출력용 개별 파츠 STEP 내보내기.

각 파츠 1개씩만 STEP 으로 저장. 슬라이서에서:
  - t_piece: 2개 배치 (1개는 X 미러)
  - pillar:  2개 배치

  exports/
    monitor_stand.step        (assembly 뷰 — 기존 유지)
    t_piece.step              (인쇄용 1개)
    pillar.step               (인쇄용 1개)
"""

from pathlib import Path

from build123d import export_step

from models.monitor_stand.pillar import build_pillar
from models.monitor_stand.t_piece import build_t_piece


EXPORTS = Path(__file__).resolve().parent / "exports"
EXPORTS.mkdir(exist_ok=True)

parts = {
    "t_piece": build_t_piece(),
    "pillar": build_pillar(),
}

for name, part in parts.items():
    out = EXPORTS / f"{name}.step"
    export_step(part, str(out))
    print(f"[print_parts] {out}")
