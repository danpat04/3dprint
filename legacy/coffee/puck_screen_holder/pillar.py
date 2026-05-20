"""퍽 스크린 홀더 - 기둥."""

import math
from datetime import datetime
from pathlib import Path

from build123d import (
    Align, Box, BuildPart, Locations, Mode, chamfer,
)
from ocp_vscode import Camera, show

BOTTOM_X = 10
BOTTOM_Y = 2.5
BOTTOM_H = 5
TOP_X = 7
TOP_Y = 2.5
TOTAL_H = 46  # 바닥부터의 전체 높이
TIGHT_TOL = 0.1  # 빡빡한 공차 (양쪽 적용 → 단면당 +0.2)
HOLE_BASE = 4
HOLE_SIZE = HOLE_BASE + 2 * TIGHT_TOL
HOLE_Z_FROM_TOP = 4  # 위에서 내려온 거리 (구멍 중심)
CHAMFER = 0.5

ALIGN_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as part:
    Box(BOTTOM_X, BOTTOM_Y, BOTTOM_H, align=ALIGN_BOTTOM)
    with Locations((0, 0, BOTTOM_H)):
        Box(TOP_X, TOP_Y, TOTAL_H - BOTTOM_H, align=ALIGN_BOTTOM)
    # 위에서 HOLE_Z_FROM_TOP mm 내려온 위치에 넓은 면(±Y) 관통 사각 구멍
    with Locations((0, 0, TOTAL_H - HOLE_Z_FROM_TOP)):
        Box(HOLE_SIZE, TOP_Y + 4, HOLE_SIZE, mode=Mode.SUBTRACT)
    # 챔퍼: 윗면(Z=TOTAL_H)과 아래 단차 윗면(Z=BOTTOM_H) 모서리
    chamfer(
        [e for e in part.edges() if abs(e.center().Z - TOTAL_H) < 0.01],
        length=CHAMFER,
    )
    # 아래 단차 윗면: 안쪽 기둥(X=±TOP_X/2) 만나는 모서리는 제외
    chamfer(
        [e for e in part.edges()
         if abs(e.center().Z - BOTTOM_H) < 0.01
         and abs(e.center().X) > TOP_X / 2 + 0.1],
        length=CHAMFER,
    )

result = part.part

# STEP 내보내기
# export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
# export_dir.mkdir(exist_ok=True)
# timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# step_path = export_dir / f"puck_screen_holder_pillar_{timestamp}.step"
# export_step(result, str(step_path))
# print(f"Exported: {step_path}")

show(result, reset_camera=Camera.RESET)
