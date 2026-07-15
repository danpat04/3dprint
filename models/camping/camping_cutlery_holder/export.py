"""출력용 개별 STEP export.

- holder.step : 통 (세워서 출력 — 바닥이 bed)
- hook.step   : 후크 (옆으로 뉘여 출력 — 넓은끝 seat·보강판이 이루는 평면이 bed)

슬라이서에서 각 파트를 위 방향으로 배치하면 된다.
후크는 길이 257mm 라 베드(256mm)에 대각선으로 놓는다.
"""

from pathlib import Path

from build123d import export_step

from models.camping.camping_cutlery_holder.holder import build_holder
from models.camping.camping_cutlery_holder.hook import build_hook

_EXPORTS = Path(__file__).resolve().parent / "exports"
_EXPORTS.mkdir(exist_ok=True)

export_step(build_holder(), str(_EXPORTS / "holder.step"))
export_step(build_hook(), str(_EXPORTS / "hook.step"))
print(f"exported: {_EXPORTS / 'holder.step'}")
print(f"exported: {_EXPORTS / 'hook.step'}")
